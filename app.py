from flask import Flask
from flask import render_template, session, request, flash, redirect, jsonify
from flask import url_for as furl_for
# from routes import *

from models import create_app, create_tables, StatusEnum
from mysecurity import verify, decode

import mydb as db
from models import Person
from datetime import datetime

app = Flask(__name__)
create_app(app)

app.secret_key = 'fa-rg3qt3452-ghd'
# session.permanent = True

from datetime import date
from datetime import timedelta

def check_login(redirect_to=None):
    if 'token' not in session:
        return redirect(furl_for('login'))
    
    token = session['token']
    if verify(token) == False:
        return redirect(furl_for('login'))
    
    if redirect_to:
        return redirect(furl_for(f'{redirect_to}'))
    
    return True

@app.route('/', methods=['POST', 'GET'])
def index():
    if 'token' not in session:
        return redirect(furl_for('login'))
    sort = request.args.get("sort", "created_desc")
    
    sort_full = request.args.get("sort", "created_desc")
    sort, order = sort_full.split("_") if "_" in sort_full else (sort_full, "desc")
    sort_parts = sort.rsplit('_', 1)
    current_sort = sort_parts[0]
    current_order = sort_parts[1] if len(sort_parts) > 1 else 'desc'

    query = Person.query
    if sort == "created":
        query = query.order_by(Person.created_at.asc() if order == "asc" else Person.created_at.desc())
    elif sort == "status":
        query = query.order_by(Person.status.asc() if order == "asc" else Person.status.desc())
    elif sort == "name":
        query = query.order_by(Person.name.asc() if order == "asc" else Person.name.desc())

    persons = query.all()

    stats = db.person_get_stats()
    today = date.today()
    today_add_7 = today + timedelta(days=7)

    return render_template(
        'index.html',
        persons=persons,
        stats=stats,
        current_sort=current_sort,
        current_order=current_order,
        today=today,
        today_add_7=today_add_7
    )


@app.route("/person/delete/<int:id>", methods=["POST"])
def delete_person(id):
    db.person_delete(id)
    
    flash(f"Пациент успешно удален")
    return "", 204


@app.route('/person/add', methods=['POST'])
def add_person_api():
    name = request.form.get('name')
    status = int(request.form.get('status'))
    arrival = request.form.get('arrival')
    departure = request.form.get('departure')

    flash(f"Добавлен <span>{name}</span>")
    
    try:
        db.person_add(name, status, arrival, departure)
        return jsonify({"message": "Пациент добавлен"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@app.route("/person/edit", methods=["POST"])
def edit_person():
    id = request.form.get("id")

    name = request.form.get("name")
    arrival = request.form.get("arrival")
    departure = request.form.get("departure")
    status = int(request.form.get("status"))

    db.update_person(id, name, arrival, departure, status)

    flash(f"Обновлен <span>{name}</span>")
    return '', 204



@app.route('/person/<int:person_id>/promote', methods=['POST'])
def promote_person_status(id):
    person = db.person_get_one(id)
    if not person:
        print("не найден")
        return jsonify({'message': 'Пользователь не найден'}), 404
    if person.promote_status():
        print("промоут")

        return jsonify({'message': 'Статус успешно повышен'}), 200
    print("не вышло")
    return jsonify({'message': 'Невозможно повысить статус'}), 400

@app.route("/person/<int:person_id>")
def person_detail(person_id):
    person = db.person_get_one(person_id)
    return render_template("person_edit.html", person=person)


@app.get('/login')
def login():
    if check_login() == True:
        return redirect(furl_for('index'))
    return render_template('login.html')

@app.post('/login')
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    token = db.login_post(username, password)
    if not token:
        return redirect(furl_for('login'))

    session['token'] = token
    return redirect(furl_for('index'))

@app.route('/logout')
def logout():
    session.pop('token', None)

    flash(f"Вы вышли из аккаунта")
    return redirect(furl_for('login'))


if __name__ == "__main__":
    with app.app_context():
        create_tables()

    app.run(debug=True, port=5500, host='0.0.0.0')