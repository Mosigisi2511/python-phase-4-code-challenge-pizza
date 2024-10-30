from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    address = db.Column(db.String, nullable=False)

    # Relationship with RestaurantPizza
    restaurant_pizzas = relationship('RestaurantPizza', back_populates='restaurant', cascade='all, delete-orphan')

    # Serialization rules
    def to_dict(self, *args, **kwargs):
        return super().to_dict(*args, **kwargs)

    def __repr__(self):
        return f"<Restaurant {self.name}>"

class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    ingredients = db.Column(db.String, nullable=False)

    # Relationship with RestaurantPizza
    restaurant_pizzas = relationship('RestaurantPizza', back_populates='pizza')

    # Serialization rules
    def to_dict(self, *args, **kwargs):
        return super().to_dict(*args, **kwargs)

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"

class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    pizza_id = db.Column(db.Integer, ForeignKey('pizzas.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, ForeignKey('restaurants.id'), nullable=False)

    # Relationships
    pizza = relationship('Pizza', back_populates='restaurant_pizzas')
    restaurant = relationship('Restaurant', back_populates='restaurant_pizzas')

    # Serialization rules
    def to_dict(self, *args, **kwargs):
        return super().to_dict(
            *args, 
            relationships={
                'pizza': self.pizza.to_dict(only=('id', 'name', 'ingredients')),
                'restaurant': self.restaurant.to_dict(only=('id', 'name', 'address'))
            },
            **kwargs
        )

    @validates('price')
    def validate_price(self, key, price):
        if price < 1 or price > 30:
            raise ValueError("Price must be between 1 and 30.")
        return price

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
