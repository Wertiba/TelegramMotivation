from dbutils.pooled_db import PooledDB

_pool = None

def get_pool(host, user, password, name, **conn_params):
    global _pool
    if _pool is None:
        _pool = PooledDB(host, user, password, name, **conn_params)
    return _pool
