from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    """
    Clase body request para crear un usuario

    Attributes:
        name --> str
        email --> EmailStr
        password --> str
        petName --> str
    Args:
        BaseModel (_type_): default de pydantic
    """
    name: str
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    petName: str
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    
class changePasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
