from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import Enum as SQLEnum
from datetime import date


db = SQLAlchemy()

def create_app(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
    app.config ["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app

def create_tables():
    db.create_all()
    if not User.query.first():
        user = User(username="anna", password="911x")
        db.session.add(user)
        db.session.commit()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(24))
    password = db.Column(db.String(32))

    def anonim(self):
        return {
            "username": self.username
        }
    
from enum import Enum

class StatusEnum(str, Enum):
    NOT_READY = "not_ready"
    IN_WORK = "in_work"
    READY = "ready"


class Person(db.Model):
    __tablename__ = 'persons'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(24))
    status = db.Column(SQLEnum(StatusEnum), default=StatusEnum.NOT_READY)
    arrival = db.Column(db.Date)
    departure = db.Column(db.Date)

    created_at = db.Column(db.Date)

    def status_display(self):
        display_map = {
            "not_ready": "Не готов",
            "in_work": "В работе",
            "ready": "Готов"
        }
        return display_map.get(self.status, self.status)
    
    def days_left(self):
        if self.departure and self.departure >= date.today():
            return (self.departure - date.today()).days
        return "0"
    
    def promote_status(self):
        order = [StatusEnum.NOT_READY.value, StatusEnum.IN_WORK.value, StatusEnum.READY.value]
        try:
            current_index = order.index(self.status)
        except ValueError:
            current_index = 0

        if current_index < len(order) - 1:
            self.status = StatusEnum(order[current_index + 1])
            db.session.commit()
            return True
        
        return False