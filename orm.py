import sqlite3

SQLITE_TYPES = {
    "INTEGER": int,
    "TEXT": str,
    "REAL": float,
    "BLOB": bytes,
    "NULL": None,
}


class Table:
    """
    Base class for all tables.
    """

    @classmethod
    def fields(cls):
        # return [field for field in cls.__dict__.keys() if not field.startswith("_")]
        # Add the values of the fields
        return [
            f"{key} {value}"
            for key, value in vars(cls).items()
            if not key.startswith("_")
        ]

    @classmethod
    def keys(cls):
        """
        Returns the keys of the class.

        Example:
        >>> class Person(Table):
        ...     name = "TEXT"
        ...     age = "INTEGER"
        >>> Person.keys()
        ['name', 'age']
        """
        return [key for key in vars(cls).keys() if not key.startswith("_")]


class Database:
    CREATE_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        {fields}
    );
    """

    def __init__(self, db_name) -> None:
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def sync(self):
        # todo: Create a script that the user can call from the cli
        # to do all this like python bony.py migrate
        if len(Table.__subclasses__()) == 0:
            print(">>> 😔 No tables found.")
            return

        for table in Table.__subclasses__():
            self.cursor.execute(
                self.CREATE_TABLE_QUERY.format(
                    table_name=table.__name__.lower(), fields=", ".join(table.fields())
                )
            )

        self.conn.commit()

        print(">>> 🚀 Created {} tables.".format(len(Table.__subclasses__())))

    def select_all(self, table: Table):
        print("""select * from {}""".format(table.__name__))
        items = self.cursor.execute(
            """select * from {}""".format(table.__name__)
        ).fetchall()

        return [
            {
                key: item[index]
                for index, key in enumerate(vars(table).keys())
                if not key.startswith("_")
            }
            for item in items
        ]

    def select_one(self, table: Table, **kwargs):
        values = ", ".join([f"{key} = '{value}'" for key, value in kwargs.items()])
        items = self.cursor.execute(
            """select * from {} where {}""".format(table.__name__, values)
        ).fetchone()

        # Transforming the received data to the format of the table
        return {
            key: items[index]
            for index, key in enumerate(vars(table).keys())
            if not key.startswith("_")
        }

    def insert(self, table: Table, data: dict):
        fields = ", ".join(data.keys())
        values = ", ".join([f"'{value}'" for value in data.values()])
        query = Table.INSERT_QUERY.format(
            table_name=table.__name__.lower(), fields=fields, values=values
        )
        self.cursor.execute(query)
        self.conn.commit()
