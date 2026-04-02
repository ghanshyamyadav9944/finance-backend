from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from database import get_db
from models import User, Transaction, TypeEnum
from schemas import UserCreate, UserLogin, UserOut, Token
from schemas import TransactionCreate, TransactionUpdate, TransactionOut
from core import hash_password, verify_password, create_access_token, decode_token, oauth2_scheme
from typing import Optional
import datetime

router = APIRouter()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_role(*roles):
    def checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Access forbidden")
        return current_user
    return checker

@router.post("/auth/register", response_model=UserOut, tags=["Authentication"])
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/auth/login", response_model=Token, tags=["Authentication"])
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    if not db_user.is_active:
        raise HTTPException(status_code=400, detail="Account is inactive")
    token = create_access_token(data={"sub": db_user.email, "role": db_user.role})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/transactions", response_model=TransactionOut, tags=["Transactions"])
def create_transaction(
    t: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    transaction = Transaction(**t.dict(), user_id=current_user.id)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@router.get("/transactions", tags=["Transactions"])
def get_transactions(
    type: Optional[str] = None,
    category: Optional[str] = None,
    date: Optional[datetime.date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Transaction).filter(Transaction.is_deleted == False)
    if type:
        query = query.filter(Transaction.type == type)
    if category:
        query = query.filter(Transaction.category == category)
    if date:
        query = query.filter(Transaction.date == date)
    return query.all()

@router.put("/transactions/{id}", response_model=TransactionOut, tags=["Transactions"])
def update_transaction(
    id: int,
    t: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    transaction = db.query(Transaction).filter(Transaction.id == id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    for key, value in t.dict(exclude_unset=True).items():
        setattr(transaction, key, value)
    db.commit()
    db.refresh(transaction)
    return transaction

@router.delete("/transactions/{id}", tags=["Transactions"])
def delete_transaction(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    transaction = db.query(Transaction).filter(Transaction.id == id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    transaction.is_deleted = True
    db.commit()
    return {"message": "Transaction deleted successfully"}

@router.get("/dashboard/summary", tags=["Dashboard"])
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "analyst"))
):
    active = db.query(Transaction).filter(Transaction.is_deleted == False)
    total_income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.is_deleted == False,
        Transaction.type == "income"
    ).scalar() or 0
    total_expense = db.query(func.sum(Transaction.amount)).filter(
        Transaction.is_deleted == False,
        Transaction.type == "expense"
    ).scalar() or 0
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": total_income - total_expense,
        "total_transactions": active.count()
    }

@router.get("/dashboard/category", tags=["Dashboard"])
def get_category_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "analyst"))
):
    results = db.query(
        Transaction.category,
        Transaction.type,
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.is_deleted == False
    ).group_by(Transaction.category, Transaction.type).all()
    return [{"category": r.category, "type": r.type, "total": r.total} for r in results]

@router.get("/dashboard/trends", tags=["Dashboard"])
def get_monthly_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "analyst"))
):
    results = db.query(
        extract("year", Transaction.date).label("year"),
        extract("month", Transaction.date).label("month"),
        Transaction.type,
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.is_deleted == False
    ).group_by("year", "month", Transaction.type).all()
    return [{"year": int(r.year), "month": int(r.month), "type": r.type, "total": r.total} for r in results]

@router.get("/dashboard/recent", tags=["Dashboard"])
def get_recent_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "analyst"))
):
    results = db.query(Transaction).filter(
        Transaction.is_deleted == False
    ).order_by(Transaction.date.desc()).limit(10).all()
    return results

@router.get("/users", tags=["Users"])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    return db.query(User).all()

@router.patch("/users/{id}/status", tags=["Users"])
def update_user_status(
    id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = is_active
    db.commit()
    return {"message": f"User status updated to {is_active}"}
