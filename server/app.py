#!/usr/bin/env python3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

from models import db, Restaurant, RestaurantPizza, Pizza

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


# Implementing the GET route for /restaurants
class RestaurantListResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict() for restaurant in restaurants], 200


# Implementing the GET route for /restaurants/<int:id>
class RestaurantResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return restaurant.to_dict(), 200
        return {"error": "Restaurant not found"}, 404


# Implementing the DELETE route for /restaurants/<int:id>
class RestaurantDeleteResource(Resource):
    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return "", 204  # 204 No Content
        return {"error": "Restaurant not found"}, 404


# Implementing the POST route for /restaurant_pizzas
class RestaurantPizzaResource(Resource):
    def post(self):
        data = request.get_json()
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')
        price = data.get('price')

        if not pizza_id or not restaurant_id or not price:
            return {"error": "Missing data"}, 400

        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)

        if not pizza or not restaurant:
            return {"error": "Pizza or Restaurant not found"}, 404

        restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(restaurant_pizza)
        db.session.commit()

        return restaurant_pizza.to_dict(), 201


# Add Resources to API (creating the endpoints)
api.add_resource(RestaurantListResource, '/restaurants')
api.add_resource(RestaurantResource, '/restaurants/<int:id>')
api.add_resource(RestaurantDeleteResource, '/restaurants/delete/<int:id>')
api.add_resource(RestaurantPizzaResource, '/restaurant_pizzas')


if __name__ == "__main__":
    app.run(port=5555, debug=True)
