from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserProfileUpdate(BaseModel):
    college: str | None = None
    degree: str | None = None
    branch: str | None = None
    graduation_year: int | None = None
    target_role: str | None = None
    experience_level: str | None = None
    interests: list[str] | None = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    college: str | None
    degree: str | None
    branch: str | None
    graduation_year: int | None
    target_role: str | None
    experience_level: str | None
    interests: list[str] | None = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
