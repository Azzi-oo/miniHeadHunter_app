from sqlalchemy import insert, text
from database import engine, async_engine, session_factory, async_session_factory
from models import metadata_obj
from src.models import WorkersOrm


def create_tables():
    engine.echo = False
    metadata_obj.drop_all(engine)
    metadata_obj.create_all(engine)
    engine.echo = True

def insert_data():
    worker_bobr = WorkersOrm(username="Bobr")
    worker_volk = WorkersOrm(username="Bure")
    with session_factory() as session:
        session.add_all([worker_bobr, worker_volk])
        session.commit()

async def insert_data():
    async with async_session_factory() as session:
        worker_bobr = WorkersOrm(username="Bobr")
        worker_volk = WorkersOrm(username="Bure")
        session.add_all([worker_bobr, worker_volk])
        await session.commit()
