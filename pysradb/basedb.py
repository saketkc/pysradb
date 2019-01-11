import sqlite3
import warnings

import pandas as pd

from .utils import _extract_first_field


class BASEdb(object):
    def __init__(self, sqlite_file):
        """Initialize SRAdb.

        Parameters
        ----------

        sqlite_file: string
                     Path to unzipped SRAmetadb.sqlite file


        """
        self.sqlite_file = sqlite_file
        self.open()
        self.cursor = self.db.cursor()

    def open(self):
        """Open sqlite connection."""
        self.db = sqlite3.connect(self.sqlite_file)
        self.db.text_factory = str

    def close(self):
        """Close sqlite connection."""
        self.db.close()

    def list_tables(self):
        """List all tables in the sqlite file.

        Returns
        -------
        table_list: list
                    List of all table names
        """
        results = self.cursor.execute(
            'SELECT name FROM sqlite_master WHERE type="table";'
        ).fetchall()
        return _extract_first_field(results)

    def list_fields(self, table):
        """List all fields in a given table.

        Parameters
        ----------
        table: string
               Table name.
               See `list_tables` for getting all table names

        Returns
        -------
        field_list: list
                    A list of field names for the table
        """
        results = self.cursor.execute("SELECT * FROM {}".format(table))
        return _extract_first_field(results.description)

    def desc_table(self, table):
        """Describe all fields in a table.

        Parameters
        ----------
        table: string
               Table name.
               See `list_tables` for getting all table names

        Returns
        -------
        table_desc: DataFrame
                    A DataFrame with field name and its
                    schema description
        """
        results = self.cursor.execute(
            'PRAGMA table_info("{}")'.format(table)
        ).fetchall()
        columns = ["cid", "name", "dtype", "notnull", "dflt_value", "pk"]
        data = []
        for result in results:
            data.append(list(map(lambda x: str(x), result)))
        table_desc = pd.DataFrame(data, columns=columns)
        return table_desc

    def query(self, sql_query):
        """Run SQL query.

        Parameters
        ----------
        sql_query: string
                   SQL query string

        Returns
        -------
        results: DataFrame
                 Query results formatted as dataframe

        """
        results = self.cursor.execute(sql_query).fetchall()
        column_names = list(map(lambda x: x[0], self.cursor.description))
        results = [dict(zip(column_names, result)) for result in results]
        df = pd.DataFrame(results)
        if not results:
            warnings.warn("Found no matching results for query.", RuntimeWarning)
        return df

    def get_row_count(self, table):
        """Get row counts for a table.

        Parameters
        ----------
        table: string
               Table name.
               See `list_tables` for getting all table names

        Returns
        -------
        row_count: int
                   Number of rows in table
        """
        return self.cursor.execute(
            "SELECT max(rowid) FROM {}".format(table)
        ).fetchone()[0]

    def all_row_counts(self):
        """Get row counts of all tables in the db file.

        Returns
        -------
        row_counts: DataFrame
                    A dataframe with table names and corresponding
                    row count.

        """
        tables = self.list_tables()
        results = dict([(table, self.get_row_count(table)) for table in tables])
        return pd.DataFrame.from_dict(results, orient="index", columns=["count"])
