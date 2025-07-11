#User object
from fastapi import APIRouter, HTTPException
from .. import schemas, models, auth
from fastapi import Depends
from .. import auth

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate):
    db_user = models.User.get_or_none(models.User.login == user.login)
    if db_user:
        raise HTTPException(status_code=400, detail="Login already registered")
    
    hashed_password = auth.hash_password(user.password)

    new_user = models.User.create(
        login = user.login,
        password = hashed_password,
        role = user.role
    )
    return new_user

@router.get("/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user