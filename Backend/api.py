import fastapi
import threading
from fastapi.middleware.cors import CORSMiddleware


def databaseRunner():
    import database

threading.Thread(target=databaseRunner).start()

app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*']
)

@app.get("/drones")
def index():
    return {open("Database/drones.csv", "r").read()}

@app.get("/pilots")
def index():
    return {open("Database/pilots.csv", "r").read()}


