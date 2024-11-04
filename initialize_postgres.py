'''Creates and init postgres db schema'''

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# PostgreSQL connection URL
DATABASE_URL = "postgresql+psycopg2://user:mypassword@localhost:5430/db"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):  # pylint: disable=too-few-public-methods
    """
    Represents a user in the system.

    Attributes:
        id (int): Primary key for the user.
        name (str): Name of the user.
        email (str): Email address of the user, unique to each user.
        shipping_address (str): Shipping address of the user.
        orders (list): List of orders associated with the user.
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    shipping_address = Column(String)

    orders = relationship('Order', back_populates='user')

class Inventory(Base):  # pylint: disable=too-few-public-methods
    """
    Represents an item in the inventory.

    Attributes:
        id (int): Primary key for the inventory item.
        item_name (str): Name of the item.
        quantity (int): Quantity of the item in stock.
        price (float): Price of the item.
        orders (list): List of orders associated with the item.
    """
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True)
    item_name = Column(String)
    quantity = Column(Integer)
    price = Column(Float)

    orders = relationship('Order', back_populates='item')

class Order(Base):  # pylint: disable=too-few-public-methods
    """
    Represents an order in the system.

    Attributes:
        id (int): Primary key for the order.
        user_id (int): Foreign key to associate with a user.
        item_id (int): Foreign key to associate with an item.
        status (str): Status of the order, e.g., 'fulfilled', 'shipped', 'delivered'.
        user (User): User who placed the order.
        item (Inventory): Item in the inventory that was ordered.
    """
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    item_id = Column(Integer, ForeignKey('inventory.id'))
    status = Column(String)  # Example statuses: 'fulfilled', 'shipped', 'delivered'

    user = relationship('User', back_populates='orders')
    item = relationship('Inventory', back_populates='orders')

Base.metadata.create_all(engine)

def load_data():
    """
    Loads sample data into the database.
    
    Adds sample users, items in inventory, and orders, and commits them to the database.
    """
    user1 = User(name="John Doe", email="john@example.com", shipping_address="123 Elm St")
    user2 = User(name="Jane Smith", email="jane@example.com", shipping_address="456 Oak St")

    session.add_all([user1, user2])

    item1 = Inventory(item_name="Laptop", quantity=50, price=999.99)
    item2 = Inventory(item_name="Headphones", quantity=100, price=199.99)
    item3 = Inventory(item_name="Monitor", quantity=30, price=299.99)

    session.add_all([item1, item2, item3])

    order1 = Order(user=user1, item=item1, status="shipped")
    order2 = Order(user=user2, item=item2, status="fulfilled")
    order3 = Order(user=user1, item=item3, status="delivered")

    session.add_all([order1, order2, order3])

    session.commit()

    print("Data loaded successfully!")

if __name__ == "__main__":
    load_data()
