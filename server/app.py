#!/usr/bin/env python3
from flask import Flask, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
import os

from models import db, Restaurant, RestaurantPizza, Pizza

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

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


# ---------------------- RESOURCES ----------------------

class RestaurantList(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [r.to_dict(rules=("-restaurant_pizzas",)) for r in restaurants], 200


class RestaurantByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        return restaurant.to_dict(), 200

    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        db.session.delete(restaurant)
        db.session.commit()
        return {}, 204


class PizzaList(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        # Exclude restaurant_pizzas so test passes
        return [p.to_dict(rules=("-restaurant_pizzas",)) for p in pizzas], 200


class RestaurantPizzaList(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_rp = RestaurantPizza(
                price=data["price"],
                pizza_id=data["pizza_id"],
                restaurant_id=data["restaurant_id"],
            )
            db.session.add(new_rp)
            db.session.commit()
            return new_rp.to_dict(), 201
        except Exception:
            return {"errors": ["validation errors"]}, 400


# ---------------------- ROUTES ----------------------

api.add_resource(RestaurantList, "/restaurants")
api.add_resource(RestaurantByID, "/restaurants/<int:id>")
api.add_resource(PizzaList, "/pizzas")
api.add_resource(RestaurantPizzaList, "/restaurant_pizzas")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
