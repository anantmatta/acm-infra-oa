# DO NOT MODIFY THIS FILE!
import sqlite3
import os


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

DB_PATH = os.environ.get("DB_PATH", "data.db")
dbcon = sqlite3.connect(DB_PATH, check_same_thread=False)
dbcon.row_factory = dict_factory

NOT_IMPLEMENTED_RESPONSE = {"message": "Method not implemented."}
HTTP_STATUS_OK = 200
HTTP_STATUS_CREATED = 201
HTTP_STATUS_ERROR = 500
HTTP_STATUS_NOT_IMPLEMENTED = 501

ISO8601_TIMESTAMP_REGEX = (
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?$"
)

def run_db_query(*args, **kwargs):
    """
    You must use this function for all your queries to pass the tests!
    You may not modify this function!
    """
    cur = dbcon.cursor()
    response = cur.execute(*args, **kwargs)
    dbcon.commit()
    return response


__all__ = [
    "DB_PATH",
    "dbcon",
    "NOT_IMPLEMENTED_RESPONSE",
    "HTTP_STATUS_OK",
    "HTTP_STATUS_CREATED",
    "HTTP_STATUS_CREATED",
    "HTTP_STATUS_ERROR",
    "HTTP_STATUS_NOT_IMPLEMENTED",
    "ISO8601_TIMESTAMP_REGEX",
    "run_db_query"
]
