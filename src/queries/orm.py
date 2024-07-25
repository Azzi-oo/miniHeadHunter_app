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

    @staticmethod
    def insert_additional_resumes():
        with sync_engine.connect() as conn:
            workers = [
                {"username": "Artem"},  # id 3
                {"username": "Roman"},  # id 4
                {"username": "Petr"},   # id 5
            ]
            resumes = [
                {"title": "Python программист", "compensation": 60000, "workload": "fulltime", "worker_id": 3},
                {"title": "Machine Learning Engineer", "compensation": 70000, "workload": "parttime", "worker_id": 3},
                {"title": "Python Data Scientist", "compensation": 80000, "workload": "parttime", "worker_id": 4},
                {"title": "Python Analyst", "compensation": 90000, "workload": "fulltime", "worker_id": 4},
                {"title": "Python Junior Developer", "compensation": 100000, "workload": "fulltime", "worker_id": 5},
            ]
            insert_workers = insert(workers_table).values(workers)
            insert_resumes = insert(resumes_table).values(resumes)
            conn.execute(insert_workers)
            conn.execute(insert_resumes)
            conn.commit()

    @staticmethod
    def join_cte_subquery_window_func():
        """
        WITH helper2 AS (
            SELECT *, compensation-avg_workload_compensation AS compensation_diff
            FROM
            (SELECT
                w.id,
                w.username,
                r.compensation,
                r.workload,
                avg(r.compensation) OVER (PARTITION BY workload)::int AS avg_workload_compensation
            FROM resumes r
            JOIN workers w ON r.worker_id = w.id) helper1
        )
        SELECT * FROM helper2
        ORDER BY compensation_diff DESC;
        """
        with sync_engine.connect() as conn:
            r = aliased(resumes_table)
            w = aliased(workers_table)
            subq = (
                select(
                    r,
                    w,
                    func.avg(r.c.compensation).over(partition_by=r.c.workload).cast(Integer).label("avg_workload_compensation"),
                )
                # .select_from(r)
                .join(r, r.c.worker_id == w.c.id).subquery("helper1")
            )
            cte = (
                select(
                    subq.c.worker_id,
                    subq.c.username,
                    subq.c.compensation,
                    subq.c.workload,
                    subq.c.avg_workload_compensation,
                    (subq.c.compensation - subq.c.avg_workload_compensation).label("compensation_diff"),
                )
                .cte("helper2")
            )
            query = (
                select(cte)
                .order_by(cte.c.compensation_diff.desc())
            )

            res = conn.execute(query)
            result = res.all()
            print(f"{len(result)=}. {result=}")

    # Relationships отсутствуют при использовании Table
