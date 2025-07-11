from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from .. import models, auth, schemas

router = APIRouter(tags=["Authentication"])

@router.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = models.User.get_or_none(models.User.login == form_data.username)
    
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(
        data={"user_id":user.id, "sub": user.login}
    )

    return {"access_token": access_token, "token_type": "bearer"}