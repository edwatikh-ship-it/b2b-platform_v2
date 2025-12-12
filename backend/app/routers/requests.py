from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_requests():
    """Placeholder для requests router"""
    return {"status": "requests router placeholder"}
