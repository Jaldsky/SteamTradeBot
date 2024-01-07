from abc import ABC
from dataclasses import dataclass
from sqlite3 import connect, Connection, Cursor
from typing import Optional

DB_NAME = 'SteamTradeBot.db'


@dataclass
class DatabaseManagerBase(ABC):
    """Base class for interacting with a database."""

    db_name: str = DB_NAME
    conn: Optional[Connection] = None
    cursor: Optional[Cursor] = None

    def connect(self) -> None:
        """Create connection."""
        self.conn: Connection = connect(self.db_name)
        if not self.conn:
            raise Exception('No connection')

        self.cursor: Cursor = self.conn.cursor()

    def close_connect(self) -> None:
        """Close connection."""
        if self.conn:
            self.conn.close()


class DatabaseManager(DatabaseManagerBase):
    """Class for interacting with a database."""

    def create_table(self, table_name: str, fields: list[str]) -> None:
        """Table creation method.

        Args:
            table_name: table name.
            fields: fields to create (e.g. firstname TEXT or age INTEGER).
        """
        self.connect()
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            {', '.join(fields)}
            )
        ''')
        self.conn.commit()
        self.close_connect()

    def check_table_exist(self, table_name: str) -> bool:
        """Method for checking whether a table has been created.

        Args:
            table_name: table name.

        Returns:
            True - table exists, False - table not exists.
        """
        self.connect()
        self.cursor.execute(f'''
            SELECT name
            FROM sqlite_master
            WHERE type='table' AND name='{table_name}'
        ''')
        result = self.cursor.fetchone()
        self.close_connect()
        return result is not None

    def insert_table_data(self, table_name: str, data: dict) -> None:
        """Method for adding new data to a table.

        Args:
            table_name: table name.
            data: data dict.
        """
        if not self.check_table_data_exist(table_name, data):
            self.connect()
            columns = ', '.join(data.keys())
            values = ', '.join([f":{key}" for key in data.keys()])
            self.cursor.execute(f'''
                INSERT INTO {table_name} ({columns})
                VALUES ({values})
            ''', data)
            self.conn.commit()
            self.close_connect()

    def check_table_data_exist(self, table_name: str, data: dict) -> bool:
        """Method for checking the existence of data in a table.

        Args:
            table_name: table name.
            data: data dict.

        Returns:
            True - data in table, False - data not in table.
        """
        self.connect()
        clause = " AND ".join([f"{key} = :{key}" for key in data.keys()])
        self.cursor.execute(f'''
            SELECT *
            FROM {table_name}
            WHERE {clause}
        ''', data)
        result = self.cursor.fetchone()
        self.close_connect()
        return result is not None

    def get_table_data(self, table_name: str, limit: int = 1) -> list:
        """Method to get data from table.

        Args:
            table_name: table name.
            limit: limit on receiving rows in the table.

        Returns:
            List with arrays of data.
        """
        self.connect()
        self.cursor.execute(f'''
            SELECT *
            FROM {table_name}
            LIMIT {limit}
        ''')
        result = self.cursor.fetchall()
        self.close_connect()
        return result

    def clear_table_data(self, table_name: str) -> None:
        """Method to clear records in a table.

        Args:
            table_name: table name.
        """
        self.connect()
        self.cursor.execute(f'''
            DELETE FROM {table_name}
        ''')
        self.conn.commit()
        self.close_connect()

    def update_record_at_table(self, table_name: str, new_data: str, search_condition: str) -> None:
        """Method to clear records in a table.

        Args:
            table_name: table name.
            new_data: new data to replace.
            search_condition: record search condition.
        """
        self.connect()
        self.cursor.execute(f'''
            UPDATE {table_name}
            SET {new_data}
            WHERE {search_condition}
        ''')
        self.conn.commit()
        self.close_connect()
