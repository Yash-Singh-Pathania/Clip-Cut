from pydantic import BaseModel, EmailStr, validator
from typing import Optional

# -----------------------------------------------------------------------------
# Pydantic Schemas
# -----------------------------------------------------------------------------
class UserBase(BaseModel):
    name: str
    email: EmailStr
    occupation: str

    @validator("occupation")
    def validate_occupation(cls, v):
        allowed = {"salaries", "student", "other"}
        if v not in allowed:
            raise ValueError(f"Occupation must be one of {allowed}")
        return v

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    """ Fields that can be updated by the user or admin. """
    name: Optional[str]
    occupation: Optional[str]

    @validator("occupation")
    def validate_occupation(cls, v):
        if v is None:
            return v
        allowed = {"salaries", "student", "other"}
        if v not in allowed:
            raise ValueError(f"Occupation must be one of {allowed}")
        return v
