import sqlite3
import pandas as pd


class DB:
    def __init__(self, db_file_name, table_name, keys=None, columns=None, primary_key=None):
        if columns is not None and len(keys) != len(columns):
            raise Exception('not eq length keys and columns')
        if keys is None:
            keys = ['id']
        self.conn = sqlite3.connect(db_file_name)
        self.table_name = table_name
        self.keys = keys
        self.columns = columns
        self.primary_key = keys[0] if primary_key is None else primary_key

        self.create_table(table_name, keys, columns, self.primary_key)

    def create_table(self, table_name, keys, columns, primary_key):
        column_list = []
        if columns is None:
            columns = [None for i in range(len(keys))]

        for key, column in zip(keys, columns):
            if column is None:
                c_type = 'text'
            elif column == int:
                c_type = 'integer'
            elif column == float:
                c_type = 'real'
            else:
                c_type = 'text'

            s = f'{key} {c_type}'
            if key == primary_key:
                s += ' primary key'
            column_list.append(s)
        c = ','.join(column_list)
        sql = f"CREATE TABLE IF NOT EXISTS {table_name}({c})"
        self.conn.execute(sql)
        self.commit()

    def insert(self, data):
        values = ','.join(['?' for _ in range(len(data))])
        sql = f'INSERT INTO {self.table_name} values({values})'
        self.conn.execute(sql, data)
        self.commit()

    def many_insert(self, data):
        values = ','.join(['?' for _ in range(len(data[0]))])
        sql = f'INSERT INTO {self.table_name} values({values})'
        self.conn.executemany(sql, data)
        self.commit()

    def update(self, id, key, value):
        sql = f'''
        update {self.table_name}
        set {key} = ?
        where {self.primary_key} = ?'''
        param = (value, id)
        self.conn.execute(sql, param)
        self.commit()

    def search(self, key, value):
        sql = f'''
        select *
        from {self.table_name}
        where {key} = "{value}"'''
        return pd.read_sql(sql, self.conn)

    def get_all_data(self):
        return pd.read_sql(f'select * from {self.table_name}', self.conn)

    def execute(self, sql):
        return self.conn.execute(sql)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.commit()
        self.conn.close()
