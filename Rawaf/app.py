"""Initialize Flask app."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from ddtrace import patch_all


db = SQLAlchemy()
patch_all()


def create_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.Config")

    db.init_app(app)

    with app.app_context():
        from . import routes  # Import routes

        db.create_all()  # Create database tables for our data models

        return app
        


"""Data models."""
from . import db


class User(db.Model):
    """Data model for user accounts."""

    __tablename__ = "flasksqlalchemy-tutorial-users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=False, unique=True, nullable=False)
    email = db.Column(db.String(80), index=True, unique=True, nullable=False)
    created = db.Column(db.DateTime, index=False, unique=False, nullable=False)
    bio = db.Column(db.Text, index=False, unique=False, nullable=True)
    admin = db.Column(db.Boolean, index=False, unique=False, nullable=False)

    def __repr__(self):
        return "<User {}>".format(self.username)



"""Application routes."""
from datetime import datetime as dt

from flask import current_app as app
from flask import make_response, redirect, render_template, request, url_for

from .models import User, db


@app.route("/", methods=["GET"])
def user_records():
    """Create a user via query string parameters."""
    username = request.args.get("user")
    email = request.args.get("email")
    if username and email:
        existing_user = User.query.filter(
            User.username == username or User.email == email
        ).first()
        if existing_user:
            return make_response(f"{username} ({email}) already created!")
        new_user = User(
            username=username,
            email=email,
            created=dt.now(),
            bio="In West Philadelphia born and raised, \
            on the playground is where I spent most of my days",
            admin=False,
        )  # Create an instance of the User class
        db.session.add(new_user)  # Adds new User record to database
        db.session.commit()  # Commits all changes
        redirect(url_for("user_records"))
    return render_template("users.jinja2", users=User.query.all(), title="Show Users")