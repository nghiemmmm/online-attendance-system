import os

def fix_tests(dir_path):
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                content = content.replace("from app.models import Item, User", "from app.models import TaiKhoan")
                content = content.replace("from app.models import User, UserCreate", "from app.models import TaiKhoan, TaiKhoanCreate")
                content = content.replace("from app.models import User, UserCreate, UserUpdate", "from app.models import TaiKhoan, TaiKhoanCreate, TaiKhoanUpdate")
                content = content.replace("from app.models import User", "from app.models import TaiKhoan")
                
                content = content.replace("UserCreate(", "TaiKhoanCreate(")
                content = content.replace("UserUpdate(", "TaiKhoanUpdate(")
                content = content.replace("User(", "TaiKhoan(")
                content = content.replace("User.", "TaiKhoan.")
                content = content.replace("select(User)", "select(TaiKhoan)")
                content = content.replace("db.get(User", "db.get(TaiKhoan")
                content = content.replace("delete(User)", "delete(TaiKhoan)")
                
                content = content.replace("email=", "ten_dang_nhap=")
                content = content.replace(".email", ".ten_dang_nhap")
                content = content.replace("is_active=", "trang_thai=")
                content = content.replace(".is_active", ".trang_thai")
                content = content.replace("is_superuser=True", "vai_tro=\"ADMIN\"")
                content = content.replace(".is_superuser", "vai_tro == \"ADMIN\"")
                content = content.replace("[\"email\"]", "[\"ten_dang_nhap\"]")
                content = content.replace("\"email\"", "\"ten_dang_nhap\"")
                content = content.replace("User with this email already exists", "The account with this username already exists")
                content = content.replace("User not found", "Account not found")
                content = content.replace("User deleted successfully", "Account deleted successfully")

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

fix_tests("d:/TTCS/tests")
