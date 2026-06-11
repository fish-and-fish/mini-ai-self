from fastapi import FastAPI
from .api.routes import router

app = FastAPI(title="Logo Similarity Check Service", version="1.0.0")

app.include_router(router)


@app.get("/")
async def root():
    return {"message": "Logo Similarity Check Service is running"}


def main():
    import uvicorn
    uvicorn.run("logo_similarity_check:app", host="0.0.0.0", port=15903, reload=True)


if __name__ == "__main__":
    main()