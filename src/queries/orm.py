from sqlalchemy import Integer, and_, cast, func, insert, inspect, or_, select, text
from sqlalchemy.orm import aliased, contains_eager, joinedload, selectinload

from database import Base, async_engine, async_session_factory, session_factory, sync_engine
from models import ResumesOrm, VacanciesOrm, WorkersOrm, Workload
from schemas import (
    ResumesRelVacanciesRepliedDTO,
    ResumesRelVacanciesRepliedWithoutVacancyCompensationDTO,
    WorkersRelDTO,
)


class SyncORM:
    @staticmethod
    def create_tables():
        sync_engine.echo = False
        Base.metadata.drop_all(sync_engine)
        Base.metadata.create_all(sync_engine)
        sync_engine.echo = True

    @staticmethod
    def insert_workers():
        with session_factory() as session:
            worker_jack = WorkersOrm(username="Jack")
            worker_michael = WorkersOrm(username="Michael")
            session.add_all([worker_jack, worker_michael])
            # flush отправляет запрос в базу данных
            # После flush каждый из работников получает первичный ключ id, который отдала БД
            session.flush()
            session.commit()

    @staticmethod
    def select_workers():
        with session_factory() as session:
            worker_id = 1
            worker_jack = session.get(WorkersOrm, worker_id)
            query = select(WorkersOrm)
            result = session.execute(query)
            workers = result.scalars().all()
            print(f"{workers=}")

    @staticmethod
    def update_worker(worker_id: int = 2, new_username: str = "Misha"):
        with session_factory() as session:
            worker_michael = session.get(WorkersOrm, worker_id)
            worker_michael.username = new_username
            session.refresh(worker_michael)
            session.commit()

    @staticmethod
    def insert_resumes():
        with sync_engine.connect() as conn:
            resumes = [
                {"title": "Python Junior Developer", "compensation": 50000, "workload": Workload.fulltime, "worker_id": 1},
                {"title": "Python Разработчик", "compensation": 150000, "workload": Workload.fulltime, "worker_id": 1},
                {"title": "Python Data Engineer", "compensation": 250000, "workload": Workload.parttime, "worker_id": 2},
                {"title": "Data Scientist", "compensation": 300000, "workload": Workload.fulltime, "worker_id": 2},
            ]
            stmt = insert(resumes_table).values(resumes)
            conn.execute(stmt)
            conn.commit()

    @staticmethod
    def select_resumes_avg_compensation(like_language: str = "Python"):
        with session_factory() as session:
            query = (
                select(
                    ResumesOrm.workload,
                    cast(func.avg(ResumesOrm.compensation), Integer).label("avg_compensation"),
                )
                .select_from(ResumesOrm)
                .filter(and_(
                    ResumesOrm.title.contains(like_language),
                    ResumesOrm.compensation > 40000,
                ))
                .group_by(ResumesOrm.workload)
                .having(cast(func.avg(ResumesOrm.compensation), Integer) > 70000)
            )
            res = session.execute(query)
