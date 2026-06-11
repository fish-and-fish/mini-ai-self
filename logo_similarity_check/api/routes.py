from fastapi import APIRouter

router = APIRouter()

@router.get("/download/font")
async def check_logo():
    return {
        "result": False,
        "error_msg": ""
    }


@router.get("/api/compare_logo")
async def compare_logo():
    return {"result": True}


@router.get("/api/validate_logo")
async def validate_logo():
    return {"result": True}