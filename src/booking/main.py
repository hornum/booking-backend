import uvicorn
from fastapi import FastAPI
from booking.api.routes import routers

app = FastAPI()

for router in routers:
    app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("booking.main:app", port=8000, reload=True)
