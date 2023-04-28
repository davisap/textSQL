import json
from app.generation_engine.streaming_table_selection import get_tables
from app.generation_engine.streaming_sql_generation import text_to_sql_with_retry


class Engine:

    query = ''
    table_selection_method = 'llm'
    tables = []

    def __init__(self, table_selection_method='llm'):
        self.table_selection_method = table_selection_method

    def set_query(self, query):
        self.query = query

    def run(self):
        yield {"status": "working", "state": "Query Received", "step": "query"}

        for res in self.get_tables():
            if res['status'] == 'error':
                return res
            yield res

        for res in self.get_sql():
            if res['status'] == 'error':
                return res
            yield res

    def get_tables(self):
        yield {"status": "working", "state": "Acquiring Tables", "step": "tables"}

        try:
            new_tables = get_tables(
                self.query, method=self.table_selection_method)
            self.tables = new_tables
            yield {"status": "working", "state": "Tables Acquired", "tables": new_tables, "step": "tables"}
        except Exception as e:
            yield {"status": "error", "error": str(e), 'step': 'tables'}

    def get_enums(self):
        # todo
        pass

    def get_examples(self):
        # todo
        pass

    def get_sql(self):
        for res in text_to_sql_with_retry(self.query, self.tables):
            yield res