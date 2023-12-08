""" FastAPI Querier """
import os
from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from pydantic import BaseModel
from string import ascii_letters, digits
import random
from typing import List

load_dotenv()
app = FastAPI()

POSTGRES_URL = os.getenv(
    "POSTGRES_URI", "postgresql://postgres:postgres@postgres:5432/postgres"
)
ALPHABET = ascii_letters + digits
engine = create_engine(POSTGRES_URL)


def get_db_session():
    db = engine.connect()
    try:
        yield db
    finally:
        db.close()


class Data(BaseModel):
    foo: str
    bar: int
    baz: bool
    hello: str
    world: int
    lorem: bool
    ipsum: str


@app.post("/")
def blocking_endpoint(data: Data, db_session: Session = Depends(get_db_session)):
    db_session.execute(
        text(
            """
        SELECT * FROM data
        WHERE foo = :foo AND bar = :bar AND baz = :baz
        AND hello = :hello AND world = :world AND lorem = :lorem
        AND ipsum = :ipsum
        """
        ),
        data.model_dump(),
    )
    db_session.commit()
    return {"message": "ok", "data": data}


class DataBatch(BaseModel):
    data: List[Data]


@app.post("/batch")
def blocking_endpoint_batch(
    data: DataBatch, db_session: Session = Depends(get_db_session)
):
    for d in data.data:
        db_session.execute(
            text(
                """
            SELECT * FROM data
            WHERE foo = :foo AND bar = :bar AND baz = :baz
            AND hello = :hello AND world = :world AND lorem = :lorem
            AND ipsum = :ipsum
            """
            ),
            d.model_dump(),
        )
    db_session.commit()
    return {"message": "ok", "data": data}


@app.post("/load")
def load_data(db_session: Session = Depends(get_db_session)):
    db_session.execute(
        text(
            """
        CREATE TABLE IF NOT EXISTS data (
            id SERIAL PRIMARY KEY,
            foo VARCHAR(255),
            bar INTEGER,
            baz BOOLEAN,
            hello VARCHAR(255),
            world INTEGER,
            lorem BOOLEAN,
            ipsum VARCHAR(255)
        )
        """
        )
    )
    db_session.commit()
    data = [
        {
            "foo": "".join(random.choices(ALPHABET, k=255)),
            "bar": random.randint(0, 100000),
            "baz": random.choice([True, False]),
            "hello": "".join(random.choices(ALPHABET, k=255)),
            "world": random.randint(0, 100000),
            "lorem": random.choice([True, False]),
            "ipsum": "".join(random.choices(ALPHABET, k=255)),
        }
        for _ in range(100000)
    ]
    db_session.execute(
        text(
            """
        INSERT INTO data (foo, bar, baz, hello, world, lorem, ipsum)
        VALUES (:foo, :bar, :baz, :hello, :world, :lorem, :ipsum)
        """
        ),
        data,
    )
    db_session.commit()
    return {"message": "ok"}
