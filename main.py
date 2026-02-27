from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Modelo de datos
class Reading(BaseModel):
    value: int
    timestamp: int
    deviceName: str
    units: str



# http://localhost:8000/
@app.get("/")
async def root():
    return {"message": "Hello World"}

# http://localhost:8000/example
@app.post("/example")
async def example():
    return {"message": "Hello World"}

# http://localhost:8000/readings
# {"value":514, "timestamp":200, "deviceName":"Temp01","units":"celsius"}
@app.post("/readings")
async def receive_reading(reading:Reading):
    return {
        "message": "Reading received",
        "value" : reading.value,
        "timestamp" : reading.timestamp,
    }