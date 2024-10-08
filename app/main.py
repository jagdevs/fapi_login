from fastapi.responses import RedirectResponse
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

@app.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request, token: str = Depends(auth.oauth2_scheme)):
    try:
        current_user = await auth.get_current_user(db=Depends(get_db), token=token)
        return RedirectResponse(url="/home")
    except HTTPException:
        return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/token")
async def login(
    request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Invalid username or password"}
        )
    
    access_token_expires = timedelta(minutes=60)
    access_token = auth.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    
    # Create a response that redirects to /home and set the token in a cookie
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="Authorization", value=f"Bearer {access_token}", httponly=True)
    return response


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("Authorization")
    
    # If there's no token in the cookie, render the login page
    if not token:
        return templates.TemplateResponse("login.html", {"request": request, "error": None})

    # Try to get the current user from the token
    try:
        current_user = auth.get_current_user(request=request, db=db)
        # If the token is valid, show the user the "home" page (welcome with username)
        return templates.TemplateResponse("home.html", {"request": request, "username": current_user.username})
    except HTTPException:
        # If the token is invalid, render the login page again
        return templates.TemplateResponse("login.html", {"request": request, "error": None})



@app.get("/me")
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return {"username": current_user.username}

#@app.get("/home", response_class=HTMLResponse)
#async def home(request: Request, current_user: models.User = Depends(auth.get_current_user)):
#    return templates.TemplateResponse("home.html", {"request": request, "username": current_user.username})

@app.post("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/")
    response.delete_cookie("Authorization")
    return response
