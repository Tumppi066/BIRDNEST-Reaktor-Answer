import fastapi
import threading
from fastapi.middleware.cors import CORSMiddleware
import time

# Run the database in a separate thread
# to let the API run in the main thread
def databaseRunner():
    import database

threading.Thread(target=databaseRunner).start()

startTime = time.time() 
app = fastapi.FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*']
)

# Main drone endpoint
@app.get("/drones")
def index():
    return {open("Database/drones.csv", "r").read()}

# Main pilot endpoint
@app.get("/pilots")
def index():
    return {open("Database/pilots.csv", "r").read()}

@app.get("/runtime")
def index():
    return {time.time() - startTime}

