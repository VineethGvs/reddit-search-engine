from flask import Flask
from os import path


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'abcd1234 5678defg'

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    return app