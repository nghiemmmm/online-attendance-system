# PEP257 Change Summary

This file summarizes the docstring-standard work applied to the backend.

## Tooling

- Enabled Ruff docstring checks in `pyproject.toml` by adding rule group `D`.
- Configured Ruff pydocstyle to use the Google convention.
- Temporarily ignored:
  - `D100`: missing module docstring
  - `D104`: missing package docstring
  - `D107`: missing `__init__` docstring

These ignores keep the existing codebase manageable while new and touched code
can move toward the convention.

## Completed Scope

- Added English module docstrings to every file in `app/models`.
- Added English docstrings to public model classes and helper functions in
  `app/models`.
- Replaced Vietnamese or mojibake docstrings in `app/models` with English
  PEP257-style docstrings.
- Added English module/function docstrings to:
  - `app/crud/hocphan_crud.py`
  - `app/crud/nganh_crud.py`
  - `app/crud/dangkyhocphan_crud.py`
  - `app/services/auth_token_service.py`
- Upgraded complex service and route functions to Google Style docstrings with
  `Args`, `Returns`, and `Raises` where applicable:
  - `app/services/auth_token_service.py`
  - `app/services/face_service.py`
  - `app/api/routes/anhkhuonmat.py`

## Current Result

- `app/models`: 0 files missing module docstrings.
- `app/models`: 0 public classes/functions missing docstrings by static scan.
- No Vietnamese docstring text remains in the completed scope.

## Remaining Scope

Still needs follow-up:

- `app/api`: many router files still need module and endpoint docstrings.
- `app/services`: remaining services need module/function docstrings.
- `app/crud`: remaining CRUD modules need English function docstrings.

## Verification

Completed:

```powershell
git diff --check
```

Also checked the completed scope for:

- Lines longer than 88 characters.
- Vietnamese text inside docstring summaries.
- Trailing whitespace or malformed patch output via `git diff --check`.

Not completed because the local Python environment is broken:

```powershell
ruff check app --select D
pytest
```

The current `python` command still resolves to a WindowsApps-based shim through
another virtual environment and cannot create a Python process.
