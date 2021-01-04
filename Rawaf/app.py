# """Initialize Flask app."""
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{username}:{password}@localhost/{database}"
db = SQLAlchemy(app)


# """Data models."""
from . import db


# # """Example table"""
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



# """Application routes."""
from datetime import datetime as dt

from flask import current_app as app
from flask import make_response, redirect, render_template, request, url_for

from .models import User, db

# Create a different route for each element's API (built from querying our database) 
# - these will be the source URLs for our visualizations' .js files 
@app.route("/api")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/map<br/>"
        f"/api/v1.0/hex<br/>"
        f"/api/v1.0/graph"
    )


@app.route("/api/v1.0/map", methods=["GET"])
def mapAPI():

@app.route("/api/v1.0/hex", methods=["GET"])
def hexAPI():

@app.route("/api/v1.0/graph", methods=["GET"])
def graphAPI():



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