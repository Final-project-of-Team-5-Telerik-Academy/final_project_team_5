from fastapi import FastAPI




app = FastAPI(title='Match Score', description='Organization and management app of sport events.')



if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="127.0.0.1", port=8000, reload=True)






