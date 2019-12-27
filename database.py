from clickhouse_driver import Client
import sqlite3
import pandas as pd

with sqlite3.connect('./data/new_events.db', check_same_thread = False) as con:
    SqliteConn = con

class CHDatabase:
    client = None

    def __init__(self, params):
        self.client = Client(params['host'],
                             user=params['user'],
                             password=params['password'],
                             secure=False,
                             verify=False,
                             database=params['database'],
                             compression=True,
                             connect_timeout=60 * 19900)

    def Query(self, sql):
        data = self.client.execute(sql, with_column_types=True)
        return pd.DataFrame(data[0], columns=[c[0] for c in data[1]])

    def QueryOne(self, sql):
        data = self.client.execute(sql, with_column_types=True)
        return [{d1[0]: d0[0]} for d0, d1 in zip(data[0], data[1])][0]

    def QueryOnly(self, sql):
        self.client.execute(sql)


CHData = CHDatabase({
    'host': '',
    'user': '',
    'password': '',
    'database': ''
})
