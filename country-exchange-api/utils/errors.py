from fastapi import HTTPException
from fastapi.responses import JSONResponse

def validation_error(field: str, message: str = "is required"):
    raise HTTPException(
        status_code=400,
        detail={
            "error": "Validation failed",
            "details": {field: message}
        }
    )

def not_found():
    return JSONResponse(
        status_code=404,
        content={"error": "Country not found"}
    )