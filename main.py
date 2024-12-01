from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Company as CompanyModel
from schemas import Company as CompanySchema, CompanyCreate
from utils import get_password_hash, verify_password, create_access_token
from typing import List
from datetime import timedelta

DATABASE_URL = "postgresql://myuser:mypassword@localhost:5432/mydatabase"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register/", response_model=CompanySchema)
def register_company(company: CompanyCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(company.hashed_password)
    db_company = CompanyModel(
        name=company.name,
        hashed_password=hashed_password,
        is_active=company.is_active,
        subscription_end=company.subscription_end
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

@app.post("/token/")
def login_for_access_token(form_data: CompanyCreate, db: Session = Depends(get_db)):
    company = db.query(CompanyModel).filter(CompanyModel.name == form_data.name).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.hashed_password, company.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": company.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/companies/", response_model=List[CompanySchema])
def read_companies(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    companies = db.query(CompanyModel).offset(skip).limit(limit).all()
    return companies

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
