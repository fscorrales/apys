from dataclasses import dataclass

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer,
                        MetaData, Numeric, String, Table, create_engine)

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

        self.asset_class_country = Table(
            'asset_class_country', self.metadata,
            Column('id', Integer(), primary_key=True, autoincrement = True),
            Column('asset_class', String(20), nullable=False),
            Column('country', String(20), nullable=False)
        )

        self.fci_info = Table(
            'fci_info', self.metadata,
            Column('symbol', String(20), primary_key=True, unique=True, nullable=False),
            Column('desc', String(50)),
            Column('type', String(20)),
            Column('adm_type', String(20)),
            Column('horizon', String(20)),
            Column('profile', String(20)),
            Column('yearly_var', Numeric(5,5)),
            Column('monthly_var', Numeric(5,5)),
            Column('investment', String(300)),
            Column('term', String(2)),
            Column('rescue', String(2)),
            Column('report', String(250)),
            Column('regulation', String(250)),
            Column('currency', String(20)),
            Column('country', String(20)),
            Column('market', String(20)),
            Column('bloomberg', String(20)),
        )

        self.screen_last_price = Table(
            'screen_last_price', self.metadata,
            Column('country', String(20), nullable=False),
            Column('asset_class', String(20), nullable=False),
            Column('screen', String(20), nullable=False),
            Column('symbol', String(20), primary_key=True, unique=True, nullable=False),
            Column('desc', String(50)),
            Column('date_time', DateTime()),
            Column('open', Numeric(12,2)),
            Column('high', Numeric(12,2)),
            Column('low', Numeric(12,2)),
            Column('close', Numeric(12,2)),
            Column('bid_q', Numeric(12,2)),
            Column('bid_price', Numeric(12,2)),
            Column('ask_price', Numeric(12,2)),
            Column('ask_q', Numeric(12,2)),
            Column('vol', Numeric(12,2)),
        )

        self.screens_country_instrument = Table(
            'screens_country_instrument', self.metadata,
            Column('id', Integer(), primary_key=True, autoincrement = True),
            Column('country', String(20), nullable=False),
            Column('asset_class', String(20), nullable=False),
            Column('screen', String(20), nullable=False),
        )

        self.symbol_daily = Table(
            'symbol_daily', self.metadata,
            Column('id', Integer(), primary_key=True, autoincrement = True),
            Column('symbol', String(20), nullable=False),
            Column('market', String(20), nullable=False),
            Column('date', DateTime()),
            Column('open', Numeric(12,2)),
            Column('high', Numeric(12,2)),
            Column('low', Numeric(12,2)),
            Column('close', Numeric(12,2)),
            Column('vol', Numeric(12,2)),
        )

        self.symbol_info = Table(
            'symbol_info', self.metadata,
            Column('symbol', String(20), primary_key=True, unique=True, nullable=False),
            Column('market', String(20)),
            Column('desc', String(50)),
            Column('country', String(20)),
            Column('type', String(20)),
            Column('term', String(2)),
            Column('currency', String(20)),
        )

        self.symbol_last_price = Table(
            'symbol_last_price', self.metadata,
            Column('id', Integer(), primary_key=True, autoincrement = True),
            Column('symbol', String(20)),
            Column('type', String(20)),
            Column('date_time', DateTime()),
            Column('open', Numeric(12,2)),
            Column('high', Numeric(12,2)),
            Column('low', Numeric(12,2)),
            Column('close', Numeric(12,2)),
            Column('bid_q', Numeric(12,2)),
            Column('bid_price', Numeric(12,2)),
            Column('ask_price', Numeric(12,2)),
            Column('ask_q', Numeric(12,2)),
            Column('vol', Numeric(12,2)),
            Column('desc', String(50)),
            Column('market', String(20)),
            Column('currency', String(20)),
            Column('country', String(20)),
            Column('term', String(2)),
            Column('lote', Numeric(12,2)),
            Column('lamina_min', Numeric(12,2)),
            Column('q_min', Numeric(12,2)),
            Column('shown', Boolean()),
            Column('buyable', Boolean()),
            Column('sellable', Boolean()),
        )

        self.symbol_options = Table(
            'symbol_options', self.metadata,
            Column('underlying', String(20)),
            Column('date_time', DateTime()),
            Column('symbol', String(20), primary_key=True, unique=True, nullable=False),
            Column('type', String(20)),
            Column('expire', DateTime()),
            Column('days_expire', Numeric(3)),
            Column('desc', String(50)),
            Column('strike', Numeric(12,2)),
            Column('open', Numeric(12,2)),
            Column('high', Numeric(12,2)),
            Column('low', Numeric(12,2)),
            Column('close', Numeric(12,2)),
            Column('bid_ask', Numeric(12,2)),
            # Column('bid_price', Numeric(12,2)),
            # Column('ask_price', Numeric(12,2)),
            # Column('ask_q', Numeric(12,2)),
            Column('vol', Numeric(12,2)),
            Column('var', Numeric(12,2)),
            # Column('market', String(20)),
            # Column('currency', String(20)),
            Column('country', String(20)),
            # Column('term', String(2)),
            # Column('lote', Numeric(12,2)),
            # Column('lamina_min', Numeric(12,2)),
            # Column('q_min', Numeric(12,2)),
            # Column('shown', Boolean()),
            # Column('buyable', Boolean()),
            # Column('sellable', Boolean()),
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