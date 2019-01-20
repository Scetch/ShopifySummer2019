from sqlalchemy import *
from sqlalchemy.orm import (scoped_session, sessionmaker, relationship, backref)
from sqlalchemy.ext.declarative import declarative_base

# Set up the database
engine = create_engine('sqlite:///database.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

""" Holds individual Product inventory information """
class Product(Base):
    __tablename__ = 'product'
    """ The unique id of the product """
    id = Column(Integer, primary_key=True)
    """ The title (name) of the product """
    title = Column(String)
    """ The price of an invidual instance of the product """
    price = Column(Float)
    """ The amount of product is available """
    inventory_count = Column(Integer)

""" A CartItem is a quantity instance of a Product assigned to a cart """
class CartItem(Base):
    __tablename__ = 'cartitem'
    """ The unique id of the item """
    id = Column(Integer, primary_key=True)
    """ The cart id this item is assigned to """
    cart_id = Column(Integer, ForeignKey('cart.id'))
    """ The product id that this product is assigned to """
    product_id = Column(Integer, ForeignKey('product.id'))
    """ The quantity of the product that this item represents """
    quantity = Column(Integer)
    """ The product that this item is assigned to """
    product = relationship(Product)

class Cart(Base):
    __tablename__ = 'cart'
    """ The unique id of the cart """
    id = Column(Integer, primary_key=True)
    """ The status of the cart, if it is completed or not """
    completed = Column(Boolean)
    """ The items that are assigned to this cart """
    items = relationship(CartItem, backref="cart")