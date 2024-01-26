from abc import ABC, abstractmethod
from dataclasses import dataclass
from sqlite3 import connect, Connection, Cursor
from typing import Optional, Any

from settings import DB_PATH


@dataclass
class DatabaseManagerBase(ABC):
    """Base class for interacting with the database and executing SQL queries."""

    db_name: str = DB_PATH
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
        return bool(result)

    def create_table(self, table_name: str, fields: dict[str, str]) -> None:
        """Table creation method.

        Args:
            table_name: table name.
            fields: fields to create (e.g. firstname TEXT or age INTEGER).
        """
        self.connect()
        fields = ','.join(f'{k} {v}' for k, v in fields.items())
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
            DROP TABLE IF EXISTS {table_name}
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

    def get_record_from_table(self, table_name: str, search_condition: Optional[dict] = None,
                              limit: Optional[int] = None) -> list:
        """Method to get data from table.

        Args:
            table_name: table name.
            search_condition: record search condition.
            limit: limit on receiving rows in the table.

        Returns:
            List with arrays of data.
        """
        if limit is None:
            limit = 50

        self.connect()
        if search_condition is None:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            self.cursor.execute(query)
        else:
            condition = ' AND '.join(f'{k} = ?' for k in search_condition.keys())
            query = f"SELECT * FROM {table_name} WHERE {condition} LIMIT {limit}"
            self.cursor.execute(query, tuple(search_condition.values()))

        result = self.cursor.fetchall()
        self.close_connect()
        return result

    def update_record_at_table(self, table_name: str, data: dict, search_condition: dict) -> None:
        """Method to clear records in a table.

        Args:
            table_name: table name.
            data: new data to replace.
            search_condition: record search condition.
        """
        data = ','.join(f'{k}=\'{v}\'' if isinstance(v, str) else f'{k}={v}' for k, v in data.items())
        condition = ' AND '.join(f'{k} = ?' for k in search_condition.keys())
        self.connect()
        self.cursor.execute(f'''
            UPDATE {table_name}
            SET {data}
            WHERE {condition}
        ''', tuple(search_condition.values()))
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
    _instance = None
    db_manager: DatabaseManager = DatabaseManager(DB_PATH)

    def __new__(cls, *args, **kwargs):
        """There is always one instance of the class.

        Args:
            args: args.
            kwargs: kwargs.

        Returns:
            Class instance.
        """
        if cls._instance is None:
            cls._instance = super(DataBaseManipulatorBase, cls).__new__(cls)
        return cls._instance

    def __post_init__(self) -> None:
        """Post initialization."""
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
    def create_or_update_table_data(self, table_name: str, data: dict, search_condition: str) -> None:
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
        if not table_name or not isinstance(table_name, str):
            raise TableNameException(table_name)

        return bool(self.db_manager.check_table_exist(table_name))

    def create_table(self, table_name: str, field: dict[str, str]) -> None:
        """Method to create a table in a database.

        Args:
            table_name: table name.
            field: fields to create (e.g. {'firstname': 'TEXT', 'age': 'INTEGER').
        """
        if not table_name or not isinstance(table_name, str):
            raise TableNameException(table_name)

        if not field or not isinstance(field, dict):
            raise DataCreateTableException(field)

        self.db_manager.create_table(table_name, field)

    def delete_table(self, table_name: str) -> None:
        """Method for removing a table from a database.

        Args:
            table_name: table name.
        """
        if not table_name or not isinstance(table_name, str):
            raise TableNameException(table_name)

        self.db_manager.delete_table(table_name)

    def check_table_data_exist(self, table_name: str, data: dict) -> bool:
        """Method for checking the existence of data in a table..

        Args:
            table_name: table name.
            data: data dict.

        Returns:
            True - data in table, False - data not in table.
        """
        if not table_name or not isinstance(table_name, str):
            raise TableNameException(table_name)

        if not data or not isinstance(data, dict):
            raise DataTableException(data)

        return bool(self.db_manager.check_table_data_exist(table_name, data))

    def create_table_data(self, table_name: str, data: dict[str, str]) -> None:
        """Method for creating data in a table.

        Args:
            table_name: table name.
            data: data dict.
        """
        if not table_name or not isinstance(table_name, str):
            raise TableNameException(table_name)

        if not data or not isinstance(data, dict):
            raise DataTableException(data)

        self.db_manager.insert_record_at_table_data(table_name, data)

    def get_table_data(self, table_name: str, search_condition: Optional[dict] = None,
                       limit: Optional[int] = None) -> list[tuple]:
        """Method for obtaining data in a table.

        Args:
            table_name: table name.
            search_condition: record search condition.
            limit: limit on receiving rows in the table.

        Returns:
            List with arrays of data.
        """
        if not table_name or not isinstance(table_name, str):
            raise TableNameException(table_name)

        return self.db_manager.get_record_from_table(table_name, search_condition, limit)

    def update_table_data(self, table_name: str, data: dict, search_condition: dict) -> None:
        """Method for updating data in a table.

        Args:
            table_name: table name.
            data: new data to replace.
            search_condition: record search condition.
        """
        if not table_name or not isinstance(table_name, str):
            raise TableNameException(table_name)

        if not data or not isinstance(data, dict):
            raise DataTableException(data)

        if not search_condition:
            raise SearchConditionException(search_condition)

        self.db_manager.update_record_at_table(table_name, data, search_condition)

    def delete_table_data(self, table_name: str) -> None:
        """Method for deleting data in a table.

        Args:
            table_name: table name.
        """
        if not isinstance(table_name, str):
            raise TableNameException(table_name)

        self.db_manager.delete_table_data(table_name)

    def create_or_update_table_data(self, table_name: str, data: dict, search_condition: dict) -> None:
        """A method for creating or updating data in a table.

        Args:
            table_name: table name.
            data: new data to replace.
            search_condition: record search condition.
        """
        if not isinstance(table_name, str):
            raise TableNameException(table_name)

        if not data or not isinstance(data, dict):
            raise DataTableException(data)

        if not search_condition:
            raise SearchConditionException(search_condition)

        if self.get_table_data(table_name, data):  # if the record is already present in the table
            return

        existing_data = self.get_table_data(table_name, search_condition)
        if existing_data:
            self.update_table_data(table_name, data, search_condition)
        else:
            self.create_table_data(table_name, data)


@dataclass
class DataBaseManipulatorException(Exception):
    field: Any

    def __str__(self):
        return f'Invalid type of parameter - {self.field}.'


@dataclass
class TableNameException(DataBaseManipulatorException):
    field: str


@dataclass
class DataCreateTableException(DataBaseManipulatorException):
    field: dict[str, str]


@dataclass
class DataTableException(DataBaseManipulatorException):
    field: dict[str, str]


class SearchConditionException(DataBaseManipulatorException):

    def __str__(self):
        return f'Invalid search argument - {self.field}'
