from fastapi import FastAPI

app = FastAPI(title="DetectX AI")

@app.get("/")
def root():
    return {
        "message": "Welcome to DetectX AI"
    }