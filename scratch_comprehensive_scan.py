import os
import ast
import re

routes_dir = r"d:\TTCS\app\api\routes"
app_dir = r"d:\TTCS\app"

issues_annotated = []
issues_routers = []
issues_blocking = []
issues_print = []
issues_di = []
issues_pydantic = []

# Walk all python files in app/
py_files = []
for root, dirs, files in os.walk(app_dir):
    # Skip virtualenv or cache
    if "venv" in root or "__pycache__" in root or ".pytest_cache" in root:
        continue
    for f in files:
        if f.endswith(".py"):
            py_files.append(os.path.join(root, f))

for filepath in py_files:
    rel_path = os.path.relpath(filepath, d:=r"d:\TTCS")
    is_route_file = "app\\api\\routes" in rel_path
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    try:
        tree = ast.parse(content, filename=filepath)
    except Exception as e:
        print(f"Skipping {rel_path} due to parse error: {e}")
        continue

    # Clean check: print usage
    for node in ast.walk(tree):
        # 1. Print statements
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
            issues_print.append({
                "file": rel_path,
                "line": node.lineno,
                "code": ast.unparse(node)
            })

        # 2. Async blocking code in async def functions
        if isinstance(node, ast.AsyncFunctionDef):
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Call):
                    func_name = ast.unparse(subnode.func)
                    # Check for time.sleep, requests.get/post/etc., builtins.open
                    if "time.sleep" in func_name or "requests." in func_name or func_name == "open":
                        issues_blocking.append({
                            "file": rel_path,
                            "line": subnode.lineno,
                            "func": node.name,
                            "code": ast.unparse(subnode),
                            "reason": f"Blocking call '{func_name}' inside async function"
                        })
                    # Check for sync db session call (e.g. Session.exec or session.commit but without await)
                    # Actually, if we use a sync session inside an async function without await, that is blocking.
                    # Since we are using SQLAlchemy async session, we must await session.commit(), await session.exec(), etc.
                    # If we call session.commit() without await inside async function, that is also a syntax or runtime error in async driver,
                    # but let's check for standard blocking libraries.

        # 3. Router checks (only for files in app/api/routes)
        if is_route_file and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            is_endpoint = False
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) and getattr(dec.func.value, 'id', None) == 'router':
                    is_endpoint = True
                    break
            
            if is_endpoint:
                # Check DB/Repo access inside the router function
                db_access = []
                for subnode in ast.walk(node):
                    code_str = ast.unparse(subnode)
                    # Check for DB session methods or crud imports/calls
                    if isinstance(subnode, ast.Call):
                        called = ast.unparse(subnode.func)
                        if any(x in called for x in ["session.add", "session.commit", "session.delete", "session.refresh", "session.exec", "session.get"]):
                            db_access.append(f"DB call: {code_str}")
                        elif "crud." in called or "sinhvien_crud." in called or "canbo_crud." in called or "buoihoc_crud." in called:
                            db_access.append(f"CRUD call: {code_str}")
                
                if db_access:
                    issues_routers.append({
                        "file": rel_path,
                        "line": node.lineno,
                        "func": node.name,
                        "access": db_access
                    })

                # Check for Non-Annotated parameters in route functions
                # Arguments are in node.args.args
                # Default values are in node.args.defaults
                # If an argument has a default value that contains Depends, Query, Path, Body, Form, File but doesn't use Annotated.
                # Let's align defaults with arguments.
                args = node.args.args
                defaults = node.args.defaults
                # defaults aligns with the end of args
                offset = len(args) - len(defaults)
                for idx, default_node in enumerate(defaults):
                    arg = args[offset + idx]
                    arg_name = arg.arg
                    default_str = ast.unparse(default_node)
                    # Check if it uses Depends, Query, Path, etc.
                    if any(x in default_str for x in ["Depends(", "Query(", "Path(", "Body(", "Form(", "File("]):
                        # Check if annotation contains Annotated. In AST, arg.annotation would be ast.Subscript with value.id == 'Annotated'
                        uses_annotated = False
                        if arg.annotation:
                            ann_str = ast.unparse(arg.annotation)
                            if "Annotated[" in ann_str:
                                uses_annotated = True
                        if not uses_annotated:
                            issues_annotated.append({
                                "file": rel_path,
                                "line": arg.lineno,
                                "func": node.name,
                                "arg": arg_name,
                                "old_syntax": f"{arg_name}: {ast.unparse(arg.annotation) if arg.annotation else 'None'} = {default_str}",
                                "recommended": f"{arg_name}: Annotated[{ast.unparse(arg.annotation) if arg.annotation else 'Any'}, {default_str}]"
                            })

        # 4. Dependency Injection checks (e.g. manual sessionmaker calls or direct Service/Client creation)
        # Check for SessionFactory() or Session() instantiation or direct instantiation of Services
        # (This can happen in services or endpoints)
        if isinstance(node, ast.Call):
            called = ast.unparse(node.func)
            if called in ["async_sessionmaker", "SessionLocal", "SessionFactory"] and not rel_path.endswith("database.py") and not "test" in rel_path:
                issues_di.append({
                    "file": rel_path,
                    "line": node.lineno,
                    "code": ast.unparse(node),
                    "reason": f"Manual creation/instantiation of '{called}' instead of using FastAPI dependency injection"
                })

        # 5. Pydantic check (ConfigDict, field_validator)
        # Check for v1 class Config or json_encoders
        if isinstance(node, ast.ClassDef):
            for body_node in node.body:
                if isinstance(body_node, ast.ClassDef) and body_node.name == "Config":
                    issues_pydantic.append({
                        "file": rel_path,
                        "line": body_node.lineno,
                        "class": node.name,
                        "reason": "Legacy Pydantic v1 inner 'class Config' used instead of Pydantic v2 model_config = ConfigDict(...)"
                    })
                if isinstance(body_node, ast.Assign):
                    for target in body_node.targets:
                        if isinstance(target, ast.Name) and target.id == "model_config":
                            val = ast.unparse(body_node.value)
                            if "json_encoders" in val:
                                issues_pydantic.append({
                                    "file": rel_path,
                                    "line": body_node.lineno,
                                    "class": node.name,
                                    "reason": "Deprecated 'json_encoders' config found in model_config"
                                })

# Write findings to a temporary audit report
with open(r"d:\TTCS\audit_scan_results.txt", "w", encoding="utf-8") as out:
    out.write("COMPREHENSIVE AUDIT SCAN RESULTS\n")
    out.write("================================\n\n")
    
    out.write(f"1. ROUTER LAYER VIOLATIONS (DB / CRUD DIRECT CALLS) ({len(issues_routers)})\n")
    out.write("------------------------------------------------------------------------\n")
    for iss in issues_routers:
        out.write(f"File: {iss['file']}:{iss['line']} in function {iss['func']}\n")
        for call in iss['access']:
            out.write(f"  -> {call}\n")
        out.write("\n")
        
    out.write(f"2. MISSING ANNOTATED IN ENDPOINTS ({len(issues_annotated)})\n")
    out.write("----------------------------------------------------------\n")
    for iss in issues_annotated:
        out.write(f"File: {iss['file']}:{iss['line']} in function {iss['func']}, arg '{iss['arg']}'\n")
        out.write(f"  Old: {iss['old_syntax']}\n")
        out.write(f"  New: {iss['recommended']}\n\n")
        
    out.write(f"3. BLOCKING CALLS IN ASYNC FUNCTIONS ({len(issues_blocking)})\n")
    out.write("--------------------------------------------------------\n")
    for iss in issues_blocking:
        out.write(f"File: {iss['file']}:{iss['line']} in function {iss['func']}\n")
        out.write(f"  Code:   {iss['code']}\n")
        out.write(f"  Reason: {iss['reason']}\n\n")
        
    out.write(f"4. MANUAL DATABASE SESSION / ENGINE CREATIONS ({len(issues_di)})\n")
    out.write("------------------------------------------------------------\n")
    for iss in issues_di:
        out.write(f"File: {iss['file']}:{iss['line']}\n")
        out.write(f"  Code:   {iss['code']}\n")
        out.write(f"  Reason: {iss['reason']}\n\n")
        
    out.write(f"5. PRINT STATEMENTS FOUND ({len(issues_print)})\n")
    out.write("---------------------------\n")
    for iss in issues_print:
        out.write(f"File: {iss['file']}:{iss['line']} -> {iss['code']}\n")
    out.write("\n")
        
    out.write(f"6. LEGACY PYDANTIC V1 PATTERNS ({len(issues_pydantic)})\n")
    out.write("-------------------------------\n")
    for iss in issues_pydantic:
        out.write(f"File: {iss['file']}:{iss['line']} in class {iss['class']}\n")
        out.write(f"  Reason: {iss['reason']}\n\n")

print("Scan completed! Output written to audit_scan_results.txt")
