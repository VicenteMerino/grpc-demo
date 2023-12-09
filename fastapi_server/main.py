from fastapi import FastAPI
from pydantic import BaseModel
from typing import List


app = FastAPI()


class Data(BaseModel):
    foo: str
    bar: int
    baz: bool
    hello: str
    world: int
    lorem: bool
    ipsum: str


@app.post("/")
def blocking_endpoint(data: Data):
    return {"message": "ok", "data": data}


class DataBatch(BaseModel):
    data: List[Data]


@app.post("/batch")
def blocking_endpoint_batch(data: DataBatch):
    return {"message": "ok", "data": data}
