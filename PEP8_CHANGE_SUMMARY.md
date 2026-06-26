# PEP8 Change Summary

This file summarizes the PEP8/FastAPI coding-standard changes applied to the
backend.

## Tooling

- Added formatting and linting rules in `pyproject.toml`.
- Configured:
  - Black line length: `88`
  - isort profile: `black`
  - Ruff rules: `E`, `F`, `I`, `B`, `UP`, `SIM`
  - mypy baseline settings

## Runtime Cleanup

- Removed startup test-token printing from `app/main.py`.
- Replaced runtime `print()` calls with `logger` usage in service code.
- Reordered imports into standard library, third-party, and local application
  groups.
- Broke long CORS configuration lines into multiline lists.

## FastAPI Style

- Updated `app/api/routes/anhkhuonmat.py` to use `Annotated` for `File` and
  `Form` parameters.
- Replaced inline route helper logic with small named helper functions.
- Added short docstrings for public route/helper functions.

## SQLModel Style

- Replaced boolean SQL comparisons like:

```python
LopHocPhan.trang_thai == True
```

with SQL expression style:

```python
LopHocPhan.trang_thai.is_(True)
```

- Replaced `!= None` SQL checks with:

```python
AnhKhuonMat.embedding_vector.is_not(None)
```

## Main Files Changed

- `pyproject.toml`
- `app/main.py`
- `app/api/routes/anhkhuonmat.py`
- `app/services/face_service.py`
- `app/services/models.py`
- `app/crud/canhbaohoc_tap_crud.py`
- `app/crud/diemdanh_summary_crud.py`
- `app/crud/lichhoc_crud.py`
- `app/crud/lichday_crud.py`
- `app/api/routes/sinhvien.py`

## Verification

Completed:

```powershell
git diff --check
```

Result: passed.

Not completed because the local Python environment is broken:

```powershell
ruff check app tests
black --check app tests
pytest
```

The current `python` command points to a WindowsApps shim that cannot create a
Python process.
