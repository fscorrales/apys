from sqlalchemy import (MetaData, Table, Column, Integer, Numeric, String,
DateTime, ForeignKey, create_engine)
from dataclasses import dataclass

metadata = MetaData()

@dataclass
class IOLModel:
    sql_path: str

    def __post_init__(self):
        self.metadata = MetaData()
        self.model_tables()
        self.create_engine()
        self.create_database()

    def model_tables(self):
        """Create table models"""

        self.iol_asset_class_country = Table(
            'iol_asset_class_country', self.metadata,
            Column('id', Integer(), primary_key=True, autoincrement = True),
            Column('asset_class', String(20), nullable=False),
            Column('country', String(20), nullable=False)
        )

    def create_engine(self):
        """Create an SQLite DB engine"""
        self.engine = create_engine(f'sqlite:///{self.sql_path}')

    def create_database(self):
        """Create DataBase from engine"""
        self.metadata.create_all(self.engine)



# cookies = Table('cookies', metadata,
# Column('cookie_id', Integer(), primary_key=True),
# Column('cookie_name', String(50), index=True),
# Column('cookie_recipe_url', String(255)),
# Column('cookie_sku', String(55)),
# Column('quantity', Integer()),
# Column('unit_cost', Numeric(12, 2))
# )
# users = Table('users', metadata,
# Column('user_id', Integer(), primary_key=True),
# Column('customer_number', Integer(), autoincrement=True),
# Column('username', String(15), nullable=False, unique=True),
# Column('email_address', String(255), nullable=False),
# Column('phone', String(20), nullable=False),
# Column('password', String(25), nullable=False),
# Column('created_on', DateTime(), default=datetime.now),
# Column('updated_on', DateTime(), default=datetime.now, onupdate=datetime.now)
# )
# orders = Table('orders', metadata,
# Column('order_id', Integer(), primary_key=True),
# Column('user_id', ForeignKey('users.user_id'))
# )
# line_items = Table('line_items', metadata,
# Column('line_items_id', Integer(), primary_key=True),
# Column('order_id', ForeignKey('orders.order_id')),
# Column('cookie_id', ForeignKey('cookies.cookie_id')),
# Column('quantity', Integer()),
# Column('extended_cost', Numeric(12, 2))
# )
# engine = create_engine('sqlite:///:memory:')
# metadata.create_all(engine)