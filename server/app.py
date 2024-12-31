#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

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

class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants], 200

api.add_resource(Restaurants, '/restaurants')

class RestaurantById(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant:
            return restaurant.to_dict(), 200
        return {"error": "Restaurant not found"}, 404

    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant:
            RestaurantPizza.query.filter_by(restaurant_id = id).delete()
            db.session.delete(restaurant)
            db.session.commit()
            return '', 204
        return {"error": "Restaurant not found"}, 404

api.add_resource(RestaurantById, '/restaurants/<int:id>')

class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict(only=('id', 'ingredients', 'name')) for pizza in pizzas], 200

api.add_resource(Pizzas, '/pizzas')

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_pizza = RestaurantPizza(
                price = data['price'],
                pizza_id = data['pizza_id'],
                restaurant_id= data['restaurant_id']
            )
            db.session.add(new_pizza)
            db.session.commit()

            return new_pizza.to_dict(), 201
        except ValueError:
            db.session.rollback()
            return {"errors": ["validation errors"]}, 400
        except Exception as e:
            db.session.rollback()
            return{"errors": [str(e)]}, 400

api.add_resource(RestaurantPizzas, '/restaurant_pizzas')


if __name__ == "__main__":
    app.run(port=5555, debug=True)
