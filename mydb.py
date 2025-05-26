from models import User, Person, StatusEnum
from models import db
from datetime import datetime
from sqlalchemy import func

import uuid
from mysecurity import myhash, verify, encode

def save_to_db(instance):
    db.session.add(instance)
    db.session.commit()


# Юзеры

def login_post(username, password):

    user = User.query.filter_by(username=username).first()
    print(user.password, password)

    if not user:
        raise ValueError('Такого аккаунта не существует')

    # password = myhash(password)
    if not user.password == password:
        raise ValueError('Пароль не подходит')

    token = encode(username)
    return token





def person_get_all():
    persons = Person.query.all()
    return persons

def person_get_one(id):
    person = Person.query.get(id)
    return person

def person_post_levelup(id):
    person = Person.query.filter_by(id=id).first()

    return True

def person_get_stats():
    stats = (
        db.session.query(Person.status, func.count(Person.id))
        .group_by(Person.status)
        .all()
    )
    return {status: count for status, count in stats}

def update_person(id, name, arrival, departure, status):
    person = Person.query.get(id)
    person.name = name
    person.arrival = arrival
    person.departure = departure

    person.arrival = datetime.strptime(arrival, "%Y-%m-%d").date()
    person.departure = datetime.strptime(departure, "%Y-%m-%d").date()

    status_map = {
        0: StatusEnum.NOT_READY,
        1: StatusEnum.IN_WORK,
        2: StatusEnum.READY
    }
    person.status = status_map[status]

    try:
        db.session.commit()
        print("Update successful")
        return True
    except Exception as e:
        db.session.rollback()
        print("DB Error:", e)
        return False



def person_add(name, status, arrival, departure):
    arrival = datetime.strptime(arrival, '%Y-%m-%d').date() if arrival else None
    departure = datetime.strptime(departure, '%Y-%m-%d').date() if departure else None
    status_map = {
        0: StatusEnum.NOT_READY,
        1: StatusEnum.IN_WORK,
        2: StatusEnum.READY
    }
    status = status_map[status]
    created_at = datetime.now().date()

    person = Person(
        name=name,
        status=status,
        arrival=arrival,
        departure=departure,
        created_at=created_at
    )
    save_to_db(person)

def person_delete(id):
    person = Person.query.get(id)
    db.session.delete(person)
    db.session.commit()


def register_post(username, password):

    # Проверки перед отправкой
    if not username or not password:
        raise ValueError("Заполните все поля")
    
    existing_user = User.query.filter_by(username = username).first()
    if existing_user:
        raise ValueError("Аккаунт с таким именем уже существует")
    
    if len(username) < 3:
        raise ValueError("Юзернейм должен быть от 3 символов")
    
    if len(password) < 5:
        raise ValueError("Пароль должен быть от 5 символов")

    password = myhash(password)

    user = User(username = username, password = password)
    save_to_db(user)

    return user