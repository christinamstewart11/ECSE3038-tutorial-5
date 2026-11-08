import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response 
from pydantic import BaseModel
from pymongo import MongoClient

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["ecse3038"]
devices = db["tutorial5"]

app = FastAPI()

class Device(BaseModel):
    name: str
    room: str
    temp: float
    online: bool

# Task 1
@app.get("/devices")
def get_devices():
    return list(devices.find({}, {"_id": 0}))

# Task 2
@app.get("/devices/{name}")
def get_device(name: str):
    device = devices.find_one({"name": name}, {"_id": 0})
    if device is None:
        raise HTTPException(status_code=404, detail="No device called " + name)
    return device

# Task 3
@app.post("/devices", status_code=201)
def create_device(device: Device):
    if devices.find_one({"name": device.name}):
        raise HTTPException(status_code=409, detail="A device called " + device.name + " already exists")
    devices.insert_one(device.model_dump())
    return device

# Task 4
@app.put("/devices/{name}")
def put_device(name: str, device: Device, response: Response):
    new_state = device.model_dump()
    new_state["name"] = name
    result = devices.replace_one({"name": name}, new_state, upsert=True)
    if result.upserted_id is not None:
        response.status_code = 201
    return new_state

# 200, with GET /devices/attic should show room: "loft" instead of room: "attic"
# 201 Created probe, GET /devices shows 6.
# 200, stored name is attic. The URL identifies the resource & overwrites the body’s name.