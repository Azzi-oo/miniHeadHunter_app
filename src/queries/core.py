from sqlalchemy import insert, text
from database import engine, async_engine
from models import metadata_obj
from src.models import workers_table


async def get_123():
    async with async_engine.connect() as conn:
        res = await conn.execute(text("SELECT VERSION()"))
        print(f"{res.first()=}")

def create_tables():
    metadata_obj.drop_all(engine)
    metadata_obj.create_all(engine)

def insert_data():
    with engine.connect() as conn:
        # stmt = """INSERT INTO employerss (username) VALUES
        #     ('Bobr'),
        #     ('Volk');"""
        stmt = insert(workers_table).values(
            [
                {"username": "Bobr"},
                {"username": "Volk"},
            ]
        )
        conn.execute(text(stmt))
        conn.commit()
