from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    
class changePasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
