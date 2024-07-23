import asyncio
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '...'))

from queries.core import SyncCore
from queries.orm import SyncORM

SyncORM.create_tables()
SyncORM.select_workers()

SyncORM.insert_workers()

SyncCore.select_workers()
SyncCore.update_workers()
