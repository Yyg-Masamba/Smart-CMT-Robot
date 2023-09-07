"""
 * @author        peamasamba<peamasamba@gmail.com>
 * @date          2022-12-01 09:12:27
 * @projectName   Pea Masamba
 * Copyright @peamasamba All rights reserved
"""
from async_pymongo import AsyncClient

from misskaty.vars import DATABASE_NAME, DATABASE_URI

mongo = AsyncClient(DATABASE_URI)
dbname = mongo[DATABASE_NAME]
