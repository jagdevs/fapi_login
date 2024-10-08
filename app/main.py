from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db, engine
from app import models, auth

# Initialize FastAPI app
app = FastAPI()

# Load templates for UI
templates = Jinja2Templates(directory="app/templates")

# Pre-create database
models.Base.metadata.create_all(bind=engine)

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=60)  # 1 hour session duration
    access_token = auth.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/", response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/me")
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return {"username": current_user.username}

@app.post("/logout")
async def logout():
    # Frontend should remove token, no server-side session management required
    return {"msg": "Successfully logged out"}

