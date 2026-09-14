from fastapi import FastAPI

app = FastAPI(title="The Lenny Growth Assistant API")

@app.get("/health")
def health_check():
    return {"status": "healthy"}