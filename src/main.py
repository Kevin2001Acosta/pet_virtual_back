from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
import logging

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.routes.chatbot_route import router as chatbot_router
from src.routes.user_route import router as user_router

from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/static"), name="static")

@app.get("/")
def read_root():
    return {"message": "Welcome to the MVC FastAPI application!"}

# Middleware global para capturar cualquier error no manejado
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error no manejado en {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Ocurrió un error interno en el servidor.",
            "error": str(exc) # Opcional: quitar en producción si se prefiere no exponer detalles
        }
    )

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

# Ejecutable directo con puerto dinámico (DigitalOcean App Platform asigna PORT)
if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.getenv("PORT", 8000))  # DO inyecta PORT; fallback 8000 local
    uvicorn.run("src.main:app", host="0.0.0.0", port=port)