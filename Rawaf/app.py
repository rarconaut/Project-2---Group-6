#################################################
# Dependencies (from Lesson 10 Activity 10-Ins_Flask_with_ORM)
#################################################
# from .models import User, db
from flask import make_response, redirect, render_template, request, url_for
from flask import current_app as app
from datetime import datetime as dt
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
# engine = create_engine("postgresql://postgres:postgres@localhost/project_2_corp_capital")

# # reflect an existing database into a new model
# Base = automap_base()
# # reflect the tables
# Base.prepare(engine, reflect=True)

# # Save reference to the table
# Data = Base.classes.combined_data


#################################################
# Flask Setup
#################################################
# from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@localhost/project_2_corp_capital"
# f"postgresql://{username}:{password}@localhost/{database}"
# Remove tracking modifications
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


"""Data models."""
class Data(db.Model):
    __tablename__ = "combined_data"

    ticker = db.Column(db.Unicode, primary_key=True)
    exchange = db.Column(db.Unicode)
    sector = db.Column(db.Unicode)
    industry = db.Column(db.Unicode)
    state_val = db.Column(db.Unicode)
    city = db.Column(db.Unicode)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    rpt_year = db.Column(db.Unicode)
    revenue_scaled = db.Column(db.Integer)
    income_tax_scaled = db.Column(db.Integer)
    net_income_scaled = db.Column(db.Integer)
    market_cap = db.Column(db.Integer)
    median_hh_income = db.Column(db.Integer)

    def __repr__(self):
        return "<Data {}>".format(self.data)



# """Example table"""
# class User(db.Model):

# __tablename__ = "flasksqlalchemy-tutorial-users"
# id = db.Column(db.Integer, primary_key=True)
# username = db.Column(db.String(64), index=False, unique=True, nullable=False)
# email = db.Column(db.String(80), index=True, unique=True, nullable=False)
# created = db.Column(db.DateTime, index=False, unique=False, nullable=False)
# bio = db.Column(db.Text, index=False, unique=False, nullable=True)
# admin = db.Column(db.Boolean, index=False, unique=False, nullable=False)

# def __repr__(self):
#     return "<User {}>".format(self.username)


#################################################
# Flask Routes
#################################################


# Create route that renders index.html template
@app.route("/")
def home():
    return render_template("index.html")


# Create a different route for each element's API (built from querying our database)
# - these will be the source URLs for our visualizations' .js files
@app.route("/api")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/combined-data<br/>"
        # f"/api/map<br/>"
        # f"/api/hex<br/>"
        # f"/api/graph"
    )

@app.route("/api/combined-data")
def combinedData():
    results = db.session.query(
        Data.ticker,
        Data.exchange,
        Data.sector,
        Data.industry,
        Data.state_val,
        Data.city,
        Data.lat,
        Data.lon,
        Data.rpt_year,
        Data.revenue_scaled,
        Data.income_tax_scaled,
        Data.net_income_scaled,
        Data.market_cap,
        Data.median_hh_income
    ).all()

    ticker = [result[0] for result in results]
    exchange = [result[1] for result in results]
    sector = [result[2] for result in results]
    industry = [result[3] for result in results]
    state = [result[4] for result in results]
    city = [result[5] for result in results]
    lat = [result[6] for result in results]
    lon = [result[7] for result in results]
    year = [result[8] for result in results]
    revenue = [result[9] for result in results]
    tax = [result[10] for result in results]
    net = [result[11] for result in results]
    cap = [result[12] for result in results]
    mhi = [result[13] for result in results]
    # lat = [result[x] for result in results]

    # combined_data = [{
        # "ticker": ticker,
        # "exchange": exchange,
        # "sector": sector,
        # "industry": industry,
        # "state": state,
        # "city": city,
        # "lat": lat,
        # "lon": lon,
        # "report_year": year,
        # "revenue": revenue,
        # "income_tax": tax,
        # "net_income": net,
        # "market_cap": cap,
        # "median_hh_income": mhi
    # }]

      # return jsonify(combined_data)

    # Create a dictionary for each company (from the row data) and append to a list of all_passengers
    all_data = []
    for (
        ticker,
        exchange,
        sector,
        industry,
        state,
        city,
        lat,
        lon,
        year,
        revenue,
        tax,
        net,
        cap,
        mhi
        ) in results:
        combined_data = {}
        combined_data["ticker"] = ticker
        combined_data["exchange"] = exchange
        combined_data["sector"] = sector
        combined_data["industry"] = industry
        combined_data["state"] = state
        combined_data["city"] = city
        combined_data["lat"] = lat
        combined_data["lon"] = lon
        combined_data["report_year"] = year
        combined_data["revenue"] = revenue
        combined_data["income_tax"] = tax
        combined_data["net_income"] = net
        combined_data["market_cap"] = cap
        combined_data["median_hh_income"] = mhi
        all_data.append(combined_data)

    return jsonify(all_data)

  


# @app.route("/api/map", methods=["GET"])
# def mapAPI():
#     # Create our session (link) from Python to the DB
#     session = Session(engine)

#     """Return a list of all a Table and its entries"""
#     # Query all entries
#     results = session.query(Table.column).all()

#     session.close()

#     # Convert list of tuples into normal list
#     all_entries = list(np.ravel(results))

#     return jsonify(all_entries)


# @app.route("/api/hex", methods=["GET"])
# def hexAPI():
#     # Or for more complex queries, create and append a new custom list

#     # Create our session (link) from Python to the DB
#     session = Session(engine)

#     """Example: Return a list of passenger data including the name, age, and sex"""
#     # # Query all passengers
#     # results = session.query(Passenger.name, Passenger.age, Passenger.sex).all()

#     session.close()

#     # # Create a dictionary for each passenger (from the row data) and append to a list of all_passengers
#     # all_passengers = []
#     # for name, age, sex in results:
#     #     passenger_dict = {}
#     #     passenger_dict["name"] = name
#     #     passenger_dict["age"] = age
#     #     passenger_dict["sex"] = sex
#     #     all_passengers.append(passenger_dict)

#     # return jsonify(all_passengers)


# @app.route("/api/graph", methods=["GET"])
# def graphAPI():


# @app.route("/", methods=["GET"])
# def user_records():
#     # """Create a user via query string parameters."""
#     username = request.args.get("user")
#     email = request.args.get("email")
#     if username and email:
#         existing_user = User.query.filter(
#             User.username == username or User.email == email
#         ).first()
#         if existing_user:
#             return make_response(f"{username} ({email}) already created!")
#         new_user = User(
#             username=username,
#             email=email,
#             created=dt.now(),
#             bio="In West Philadelphia born and raised, \
#             on the playground is where I spent most of my days",
#             admin=False,
#         )  # Create an instance of the User class
#         db.session.add(new_user)  # Adds new User record to database
#         db.session.commit()  # Commits all changes
#         redirect(url_for("user_records"))
#     return render_template("users.jinja2", users=User.query.all(), title="Show Users")

if __name__ == '__main__':
    app.run(debug=True)
