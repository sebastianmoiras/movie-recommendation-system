from fastapi import FastAPI
from routes import signup, login, movies, recommendation
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

app = FastAPI(
    title="Notflix API",
    swagger_ui_parameters={"persistAuthorization": True}
)

security = HTTPBearer()

# Router
app.include_router(signup.router)
app.include_router(login.router)
app.include_router(movies.router)
app.include_router(recommendation.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
