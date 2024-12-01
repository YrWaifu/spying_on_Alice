from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CompanyBase(BaseModel):
    name: str
    hashed_password: str
    is_active: bool
    subscription_end: Optional[datetime] = None

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    company_id: int
    registered_at: datetime

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    e_mail: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    user_id: int

    class Config:
        orm_mode = True

class VisitBase(BaseModel):
    user_id: int
    site_url: str
    company_id: int

class VisitCreate(VisitBase):
    pass

class Visit(VisitBase):
    visit_id: int
    time_visited: datetime

    class Config:
        orm_mode = True
