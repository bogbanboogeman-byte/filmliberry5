import functools

from dateutil import parser

from  sqlalchemy import create_engine

from flask import Flask, render_template, redirect, url_for
from flask import request, session
import sqlite3
import database
import models

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class db_connection:
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.conn.row_factory = dict_factory
        self.cur = self.conn.cursor()

    def __enter__(self):
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()


def get_db_results(query):
    conn = sqlite3.connect('database.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    res = cur.execute(query)
    result = cur.fetchall()
    conn.close()
    return result

def deccorator_check_login(func):
    @functools.wraps(func)
    def wraper(*args, **kwargs):
        if 'looged_in' in session:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('user_login'))
    return wraper

@app.route('/')
@deccorator_check_login
def main_page():
    with db_connection() as cur:
        result = cur.execute("SELECT * FROM film order by added_at desc limit 10").fetchall()
    return render_template('main.html', films=result)

@app.route('/register', methods=['GET'])
def register_page():
    return render_template("register.html")


@app.route('/register', methods=['POST'])
def user_register():
    first_name = request.form['fname']
    last_name = request.form['lname']
    password = request.form['password']
    login = request.form['login']
    email = request.form['email']
    birthe_date = parser.parse(request.form['birthe_date'])

    databse.init_db()

    new_user = models.User(first_name=first_name, last_name=last_name, password=password, login=login, email=email, birthe_date=birthe_date)

    databse.db_session.add(new_user)
    databse.db_session.commit()
    return redirect(url_for('main_page'))

@app.route('/login', methods=['GET'])
def user_login():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def user_login_post():
    login = request.form['login']
    password = request.form['password']

    databse.init_db()

    stmt = select(models.User).where(models.User.login == login, models.User.password == password)
    data = databse.db_session.execute(stmt).fetchone()

    result = databse.db_session.query(models.User).filter_by(login=login, password=password).first()


    if result:
        session['logged_in'] = True
        session['user_id'] = result = ['id']
        return  f'login with user{result}'
    return 'Login failed'




@app.route('/logout', methods=['GET'])
@deccorator_check_login
def user_logout():
    session.clear()
    return 'Logout'

@app.route('/user/<user_id>', methods=['GET', 'POST'])
def user_profile(user_id):
    session['user_id'] = session.get('user_id')
    if reugest.method == 'POST':
        if int(user_id) != session_user_id:
            return('You can edit only your profile')

            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            password = request.form['password']
            birthe_date = request.form['birthe_date']
            phone = request.form['phone']
            photo = request.form['photo']
            additital.info = request.form ['additital_info']
            with (db_connection() as cur):
                cur.execute(f"UPDATE user SET first_name'{ first_name}', last_name'{ last_name}', email'{ email}', password'{password}',birthe_date'{birthe_date}', phone_namber'{phone}', photo'{photo}',  additital.info'{ additital.info}'  WHERE id = {user_id}")
            return f'User {user_id} updated'
        else:
            with (db_connection() as cur):
                cur.execute("SELECT * FROM user WHERE id = {user_id}")
                user_by_id = cur.fetchone()

                if session_user_id is None:
                    user_by_session = "No user in session"
                else:
                    cur.execute(f"SELECT * FROM user WHERE id = {session_user_id}")
                    user_by_session = cur.fetchone()
                return render_templates("user_pade.html", user_by_id=user_by_id, user_by_session=user_by_session)
            return f'You loogen in as {user_by_session}, user {user_id} data: {user_by_id}'

@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    session_user_id = session.get('user_id')
    if user_id == session_user_id:
        return f'User {user_id} deleted'
    else:
        return 'Yon can deleted only your profile'

@app.route('/films', methods=['GET'])
def films():
    filter_params = request.args
    filter_list_texts = []
    additional_filter = ""
    for key, value in filter_params.items():
        if value:
            if key =='name':
                filter_list_texts.append(f"name like '%{value}%'")
            else:
                filter_list_texts.append(f"{key} = '{value}'")

        if filter_params:
            additional_filter ="where " + " and ".join(filter_list_texts)
    result = get_db_results(f"SELECT * FROM film {additional_filter} order by added_at desc ")
    countries = get_db_results("select * from country")
    return render_template('films.html', films=result, countries=countries)


@app.route('/films', methods=['POST'])
def add_film():
    return 'Film added'

@app.route('/films/<film_id>', methods=['GET'])
def film_info(film_id):
    with db_connection() as cur:
        result = cur.execute("SELECT * FROM film WHERE id={film_id}").fetchall()
        actors = cur.execute(f"SELECT * FROM actor join actor_film on actor_id == actor_film.actor_id  where film_id={film_id}")
        genres = cur.execute(f"SELECT * FROM genre_film where film_id={film_id}")

    return f'Film {film_id} is {result}, actors: {actors}, genres: {genres}'

@app.route('/films/<film_id>', methods=['PUT'])
def update_film(film_id):
    return f'Film {film_id} updated'

@app.route('/films/<film_id>', methods=['DELETE'])
def delete_film(film_id):
    return f'Film {film_id} deleted'

@app.route('/films/<film_id>/reting', methods=['POST'])
def film_rating(film_id):
    return f'Film {film_id} rated'

@app.route('/films/<film_id>/reting', methods=['GET'])
def film_rating_info(film_id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    res = cur.execute(f"SELECT reting FROM film WHERE id={film_id}")
    rating = cur.fetchall()
    conn.close()
    return f'Film {film_id} rating is {rating}'


@app.route('/films/<film_id>/reting<feedback_id>', methods=['DELETE'])
def film_rating_delete(film_id, feedback_id):
    return f'Film {film_id} rating {feedback_id} deleted'

@app.route('/films/<film_id>/reting/<feedback_id>', methods=['PUT'])
def film_rating_update(film_id, feedback_id):
    return f'Film {film_id} rating {feedback_id} updated'


@app.route('/films/<film_id>/reting/<feedback_id>/feedback', methods=['GET'])
def film_rating_feedback(film_id, feedback_id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    res = cur.execute(f"SELECT * FROM feedback WHERE film_id={film_id} AND id={feedback_id}")
    feedback = cur.fetchall()
    conn.close()
    return f'Film {film_id} feedback {feedback_id}: {feedback}'


@app.route('/users/<user_id>/list', methods=["GET", 'POST'])
def user_list(user_id):
    return f'User {user_id} list'


@app.route('/users/<user_id>/list' , methods=["DELETE"])
def user_list_delete(user_id):
    return f'User {user_id} list deleted'

@app.route('/users/<user_id>/list/<list_id>', methods=["GET", "POST"])
def user_list_item(user_id, list_id):
    return f'User {user_id} list item {list_id}'

@app.route('/users/<user_id>/list/<list_id>/<film_id>', methods=["DELETE"])
def user_list_item_delete(user_id, list_id, film_id):
    return f'User {user_id} list item {list_id} film {film_id} deleted'

if __name__ == '__main__':
    app.run()

