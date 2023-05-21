from base import Config


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///db.sqlite"
