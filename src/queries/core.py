from sqlalchemy import insert, text, select
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

class SyncCore:
    @staticmethod
    def create_tables():
        engine.echo = False
        metadata_obj.drop_all(engine)
        metadata_obj.create_all(engine)
        engine.echo = True

    @staticmethod
    def insert_workers():
        with engine.connect() as conn:
            # stmt = """INSERT INTO workers (username) VALUES
            #     ('Jack'),
            #     ('Michael');"""
            stmt = insert(workers_table).values(
                [
                    {"username": "Jack"},
                    {"username": "Michael"},
                ]
            )
            conn.execute(stmt)
            conn.commit()

    @staticmethod
    def select_workers():
        with engine.connect() as conn:
            query = select(workers_table)
            result = conn.execute(query)
            workers = result.all()
            print(f"{workers=}")

    @staticmethod
    def update_workers(worker_id: int = 2, new_username: str = "Misha"):
        with engine.connect() as conn:
            stmt = text("UPDATE workers SET username=:new_username WHERRE id=:id")
            stmt = stmt.bindparams(username=new_username)
            conn.execute(stmt)
            conn.commit()
