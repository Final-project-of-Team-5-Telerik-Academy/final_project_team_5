from fastapi import FastAPI
from routers.users import users_router
from routers.admins import admins_router


app = FastAPI(title='Match Score', description='Organization and management app of sport events.')
app.include_router(users_router)
app.include_router(admins_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="127.0.0.1", port=8000, reload=True)
