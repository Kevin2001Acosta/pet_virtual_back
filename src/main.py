from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError

from src.routes.chatbot_route import router as chatbot_router
from src.routes.user_route import router as user_router

from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/static"), name="static")

@app.get("/")
def read_root():
    return {"message": "Welcome to the MVC FastAPI application!"}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    for error in errors:
        if error.get("loc")[-1] == "email":
            return JSONResponse(
                status_code=422,
                content={"detail": "El email no es válido."}
            )
    # Mensaje genérico para otros errores de validación
    return JSONResponse(
        status_code=422,
        content={"detail": "Datos de entrada no válidos."}
    )

app.include_router(chatbot_router)
app.include_router(user_router)