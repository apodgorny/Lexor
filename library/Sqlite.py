import sqlite3

class Sqlite:
    def __init__(self, schema_file, db_file):
        self.db = sqlite3.connect(db_file)
        self.cursor = self.db.cursor()
        self.lastid = 0
        schema = ''
        with open(schema_file) as file:
            schema = file.read()
        self.cursor.execute('DROP TABLE b3')
        self.cursor.execute(schema)

    def execute(self, s):
        return self.cursor.execute(s)

    def commit(self):
        return self.db.commit()

    def insert(self, s, debug=False):
        if debug: print(s)
        try:
            self.execute(s)
            self.commit()
            self.lastid = self.cursor.lastrowid
            return self.lastid
        except Exception:
            return None

    def insert_many(self, s, data, debug=False):
        if debug: print(s)
        rowids = []
        self.cursor.executemany(s, data)
        self.commit()
        last_insert_id = self.select_value('SELECT last_insert_rowid()')
        rowids = [*range(self.lastid + 1, self.cursor.lastrowid + 1)]
        self.lastid = last_insert_id
        return rowids

    def select(self, s, debug=False):
        if debug: print(s)
        result = self.execute(s)
        return result.fetchall()

    def select_row(self, s, debug=False):
        if debug: print(s)
        rows = self.select(s)
        return rows[0] if len(rows) > 0 else []

    def select_col(self, s, debug=False):
        if debug: print(s)
        rows = self.select(s)
        return [x[0] for x in rows]

    def select_value(self, s, debug=False):
        if debug: print(s)
        row = self.select_row(s)
        return row[0]
