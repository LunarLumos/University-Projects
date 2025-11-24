import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dutp-secret-key-2025'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/dutp'
    SQLALCHEMY_TRACK_MODIFICATIONS = False