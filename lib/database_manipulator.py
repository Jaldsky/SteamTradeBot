from abc import ABC, abstractmethod
from dataclasses import dataclass
from sqlite3 import connect, Connection, Cursor
from typing import Optional

from settings import DB_NAME


@dataclass
class DatabaseManagerBase(ABC):
    """Base class for interacting with the database and executing SQL queries."""

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
    """Class for interacting with the database and executing SQL queries."""

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

    def create_table(self, table_name: str, fields: list[str]) -> None:
        """Table creation method.

        Args:
            table_name: table name.
            fields: fields to create (e.g. firstname TEXT or age INTEGER).
        """
        self.connect()
        fields = ','.join(fields)
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            {fields}
            )
        ''')
        self.conn.commit()
        self.close_connect()

    def delete_table(self, table_name: str) -> None:
        """Table drop method.

        Args:
            table_name: table name.
        """
        self.connect()
        self.cursor.execute(f'''
        DROP TABLE IF EXISTS {table_name};
            )
        ''')
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
        clause = ' AND '.join([f'{key} = :{key}' for key in data.keys()])
        self.cursor.execute(f'''
            SELECT *
            FROM {table_name}
            WHERE {clause}
        ''', data)
        result = self.cursor.fetchone()
        self.close_connect()
        return result is not None

    def insert_record_at_table_data(self, table_name: str, data: dict) -> None:
        """Method for adding new data to a table.

        Args:
            table_name: table name.
            data: data dict.
        """
        if not self.check_table_data_exist(table_name, data):
            self.connect()
            columns = ', '.join(data.keys())
            values = ', '.join([f':{key}' for key in data.keys()])
            self.cursor.execute(f'''
                INSERT INTO {table_name} ({columns})
                VALUES ({values})
            ''', data)
            self.conn.commit()
            self.close_connect()

    def get_table_data(self, table_name: str, search_condition: Optional[str] = None, limit: int = 50) -> list:
        """Method to get data from table.

        Args:
            table_name: table name.
            limit: limit on receiving rows in the table.
            search_condition: record search condition.

        Returns:
            List with arrays of data.
        """
        search_condition = '' if search_condition is None else f'WHERE {search_condition}'

        self.connect()
        self.cursor.execute(f'''
            SELECT *
            FROM {table_name}
            {search_condition}
            LIMIT {limit}
        ''')
        result = self.cursor.fetchall()
        self.close_connect()
        return result

    def update_record_at_table(self, table_name: str, data: dict, search_condition: str) -> None:
        """Method to clear records in a table.

        Args:
            table_name: table name.
            data: new data to replace.
            search_condition: record search condition.
        """
        data = ','.join(f'{k}=\'{v}\'' if isinstance(v, str) else f'{k}={v}' for k, v in data.items())
        self.connect()
        self.cursor.execute(f'''
            UPDATE {table_name}
            SET {data}
            WHERE {search_condition}
        ''')
        self.conn.commit()
        self.close_connect()

    def delete_table_data(self, table_name: str) -> None:
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


@dataclass
class DataBaseManipulatorBase(ABC):
    """Base class for data manipulation."""

    def __post_init__(self) -> None:
        """Post initialization."""
        self.db_manager = DatabaseManager(DB_NAME)
        if self.db_manager is None:
            raise Exception('DB Manager is missing')

    @abstractmethod
    def check_table_exist(self, table_name: str) -> bool:
        """Method of checking that a table exists in the database."""
        pass

    @abstractmethod
    def create_table(self, table_name: str, db_fields: list) -> None:
        """Method to create a table in a database."""
        pass

    @abstractmethod
    def delete_table(self, table_name: str) -> None:
        """Method for removing a table from a database."""
        pass

    @abstractmethod
    def check_table_data_exist(self, table_name: str, data: dict) -> bool:
        """A method for checking the existence of data in a table."""
        pass

    @abstractmethod
    def create_table_data(self, table_name: str, data: dict) -> None:
        """Method for creating data in a table."""
        pass

    @abstractmethod
    def get_table_data(self, table_name: str, search_condition: Optional[str], table_limit: Optional[int]
                       ) -> list[tuple]:
        """Method for obtaining data in a table."""
        pass

    @abstractmethod
    def update_table_data(self, table_name: str, data: dict, search_condition: str) -> None:
        """Method for updating data in a table."""
        pass

    @abstractmethod
    def delete_table_data(self, table_name: str) -> None:
        """Method for deleting data in a table."""
        pass

    @abstractmethod
    def create_or_update_table_data(self, table_name: str, data: dict, search_condition: str, limit: int) -> None:
        """A method for creating or updating data in a table."""


@dataclass
class DataBaseManipulator(DataBaseManipulatorBase):
    """Class-wrapper for data manipulation and data validation."""

    def check_table_exist(self, table_name: str) -> bool:
        """Method of checking that a table exists in the database.

        Args:
            table_name: table name.

        Returns:
            True - table exists, False - table not exists.
        """
        return bool(self.db_manager.check_table_exist(table_name))

    def create_table(self, table_name: str, fields: list) -> None:
        """Method to create a table in a database.

        Args:
            table_name: table name.
            fields: fields to create (e.g. firstname TEXT or age INTEGER).
        """
        self.db_manager.create_table(table_name, fields)

    def delete_table(self, table_name: str) -> None:
        """Method for removing a table from a database.

        Args:
            table_name: table name.
        """
        self.db_manager.delete_table(table_name)

    def check_table_data_exist(self, table_name: str, data: dict) -> bool:
        """Method for checking the existence of data in a table..

        Args:
            table_name: table name.
            data: data dict.

        Returns:
            True - data in table, False - data not in table.
        """

        return bool(self.db_manager.check_table_data_exist(table_name, data))

    def create_table_data(self, table_name: str, data: dict) -> None:
        """Method for creating data in a table.

        Args:
            table_name: table name.
            data: data dict.
        """
        self.db_manager.insert_record_at_table_data(table_name, data)

    def get_table_data(self, table_name: str, search_condition: Optional[str] = None, limit: Optional[int] = None
                       ) -> list[tuple]:
        """Method for obtaining data in a table.

        Args:
            table_name: table name.
            search_condition: record search condition.
            limit: limit on receiving rows in the table.

        Returns:
            List with arrays of data.
        """
        return self.db_manager.get_table_data(table_name, search_condition, limit)

    def update_table_data(self, table_name: str, data: dict, search_condition: str) -> None:
        """Method for updating data in a table.

        Args:
            table_name: table name.
            data: new data to replace.
            search_condition: record search condition.
        """
        self.db_manager.update_record_at_table(table_name, data, search_condition)

    def delete_table_data(self, table_name: str) -> None:
        """Method for deleting data in a table.

        Args:
            table_name: table name.
        """
        self.db_manager.delete_table_data(table_name)

    def create_or_update_table_data(self, table_name: str, data: dict, search_condition: str, limit: int) -> None:
        """A method for creating or updating data in a table.

        Args:
            table_name: table name.
            data: new data to replace.
            search_condition: record search condition.
            limit: limit on receiving rows in the table.
        """
        existing_data = self.db_manager.get_table_data(table_name, search_condition, limit)
        if existing_data:
            self.update_table_data(table_name, data, search_condition)
        else:
            self.db_manager.insert_record_at_table_data(table_name, data)
