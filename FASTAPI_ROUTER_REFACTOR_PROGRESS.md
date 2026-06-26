# FastAPI Router Refactor Progress

This document tracks the router cleanup requested by the Senior FastAPI review.

## Completed In This Pass

The following routers were refactored so that they no longer import CRUD modules
or access the database directly:

| Router | Service Added | Status |
| --- | --- | --- |
| `app/api/routes/hocphan.py` | `app/services/course_service.py` | Done |
| `app/api/routes/nganh.py` | `app/services/major_service.py` | Done |
| `app/api/routes/dangkyhocphan.py` | `app/services/course_registration_service.py` | Done |
| `app/api/routes/thoikhoabieu.py` | `app/services/timetable_service.py` | Done |

## Applied Router Standards

For the completed routers:

- Endpoints use `async def`.
- Endpoints include `response_model`.
- Endpoints include `status_code`.
- Endpoints include `summary`.
- Endpoints include `description`.
- Routers keep `APIRouter`, `prefix`, and `tags`.
- Routers call service functions instead of CRUD functions.
- Routers do not call `session.exec`, `session.get`, `session.add`,
  `session.commit`, `session.delete`, or SQL `select`.

## Preserved Contract

Existing URL paths and tags were preserved to avoid breaking frontend calls.

## Remaining Router Groups

The following router groups still need the same cleanup:

1. `sinhvien.py`, `canbo.py`
2. `lophocphan.py`, `buoihoc.py`
3. `diemdanh.py`, `khieunai.py`
4. `user.py`
5. `anhkhuonmat.py`
6. `hethong.py`, `baocao.py`
7. `login.py`, `google_auth_router.py`
8. `system_router.py`, `ketnoi_router.py`
