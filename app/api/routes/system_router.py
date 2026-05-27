from fastapi import APIRouter
from fastapi.responses import JSONResponse, RedirectResponse

router = APIRouter(tags=["system"])


@router.get("/health", include_in_schema=False)
def health() -> JSONResponse:
    return JSONResponse({"message": "It worked!!"})


@router.get("/home/")
def home():
    return {"message": "Welcome"}


@router.get("/")
async def root():
    return RedirectResponse(url="/api/docs")


@router.get("/ui-redirect")
async def ui_redirect():
    return RedirectResponse(url="/ui")
