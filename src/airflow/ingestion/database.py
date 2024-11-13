from sqlalchemy import create_engine, inspect, MetaData, Table
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List

class Database:
    def __init__(
            self,
            username: str,
            password: str,
            database_name: str
    ) -> None:
        self.__username = username
        self.__password = password
        self.__database_name = database_name

        self.engine = create_engine(f"mysql+pymysql://{self.__username}:{self.__password}@localhost/{self.__database_name}")
        self.Session = sessionmaker(bind=self.engine)
        self.metadata = MetaData()

        self.session: Optional[Session] = None

    def show_tables(self) -> List[str]:
        inspector = inspect(self.engine)
        return inspector.get_table_names()
    
    def insert_data(
            self,
            table_name: str,
            data: dict
    ) -> None:
        table = Table(table_name, self.metadata, autoload_with=self.engine)

        try:
            self.session.execute(table.insert(), data)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Failed to insert data: {e}")

    def __enter__(self) -> 'Database':
        self.session = self.Session()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.session.close()
        if exc_type: print(f"An error occured: {exc_val}")

        return True