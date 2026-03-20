from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

# Base de datos
# DATABASE_URL = "postgresql://user:password@localhost/neondb"
DATABASE_URL = "postgresql://neondb_owner:npg_igQ20oLGnfpB@ep-sparkling-thunder-aim4a2y1-pooler.c-4.us-east-1.aws.neon.tech/neondb"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class ReadingTable(Base):
    __tablename__ = "readings"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(Integer)
    timestamp = Column(Integer)
    deviceName = Column(String)
    units = Column(String)

# APP
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
    db = SessionLocal()
    reading_to_save = ReadingTable(
        value = reading.value,
        timestamp = reading.timestamp,
        deviceName = reading.deviceName,
        units = reading.units
    )
    db.add(reading_to_save)
    db.commit()
    db.refresh(reading_to_save)
    db.close()
    return {
        "message": "Reading received",
        "value" : reading.value,
        "timestamp" : reading.timestamp,
    }
# [{},{},{}]
# [{"value":514, "timestamp":200, "deviceName":"Temp01","units":"celsius"},{"value":514, "timestamp":200, "deviceName":"Temp01","units":"celsius"},{"value":514, "timestamp":200, "deviceName":"Temp01","units":"celsius"}]
@app.post("/readings/batch")
async def receive_batch(batch:list[Reading]):
    db = SessionLocal()
    
    readings_to_save = [ReadingTable(
        value = r.value,
        timestamp = r.timestamp,
        deviceName = r.deviceName,
        units = r.units
    ) for r in batch] 
    # list[Reading] -> list[ReadingTable]
    # Para poder almacenarlo en SQL

    db.add_all(readings_to_save)
    db.commit()
    db.refresh()
    db.close()
    return {
        "message": "Batch saved",
    }


Base.metadata.create_all(bind=engine)