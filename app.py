import functools
from sqlalchemy import select
from dateutil import parser

from  sqlalchemy import create_engine

from flask import Flask, render_template, redirect, url_for
from flask import request, session
import sqlite3
import database
import models

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
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
        if session.get('user_id'):
            return func(*args, **kwargs)
        else:
            return redirect(url_for('user_login'))
    return wraper

@app.route('/')
@deccorator_check_login
def main_page():

    database.init_db()
    smth = select(models.Film).limit(10).order_by(models.Film.added_at.desc())
    data = database.db_session.execute(smth).fetchall()
    data2 = [itn[0] for itn in data]
    return render_template('main.html', films=data2)

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
    brith_date = parser.parse(request.form['birthe_date'])

    database.init_db()

    new_user = models.User(first_name=first_name, last_name=last_name, password=password, login=login, email=email, birthe_date=birthe_date)

    database.db_session.add(new_user)
    database.db_session.commit()
    return 'Registrer'

@app.route('/login', methods=['GET'])
def user_login():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def user_login_post():
    login = request.form.get('login') or request.form.get('Login')
    password = request.form.get('password')

    database.init_db()

    stmt = select(models.User).where(models.User.login == login, models.User.password == password)
    data = database.db_session.execute(stmt).fetchone()

    result = database.db_session.query(models.User).filter_by(login=login, password=password).first()


    if result:
        session['logged_in'] = True
        session['user_id'] = result.id
        return redirect(url_for('user_profile', user_id=result.id))
    return 'Login failed'




@app.route('/logout', methods=['GET'])
@deccorator_check_login
def user_logout():
    session.clear()
    return 'Logout'

@app.route('/user/<user_id>', methods=['GET', 'POST'])
@deccorator_check_login
def user_profile(user_id):

    database.init_db()
    session_user_id = session.get('user_id')
    user_id = int(user_id)
    if session_user_id is None:
        return redirect(url_for('user_login'))
    session_user_id = int(session_user_id)

    if request.method == 'POST':
            if user_id != session_user_id:
                return('You can edit only your profile')

            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            password = request.form['password']
            birthe_date = parser.parse(request.form['birthe_date'])
            phone = request.form['phone']
            photo = request.form['photo']
            additital_info = request.form['additital_info']

            stmt = update(models.User).where(models.User.id == user_id).valuaes(first_name =first_name, last_name=last_name, email=email, password=password, birthe_date=birthe_date, phone_namber=phone, photo=photo, addtital_info=additital_info)
            database.db_session.execute(stmt)
            database.db_session.commit()
            return f'User {user_id} updated'


    else:

        query_user_by_id = select(models.User).where(models.User.id == user_id)
        user_by_id = database.db_session.execute(query_user_by_id).scalar_one()

        if session_user_id is None:

            user_by_session = "No user in session"

        else:

            query_user_by_session = select(models.User).where(models.User.id == session_user_id)
            user_by_session=database.db_session.execute(query_user_by_session).scalar_one()

        database.db_session.commit()

        return render_template("user_pade.html", user=user_by_id, user_session=user_by_session)



@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    session_user_id = session.get('user_id')
    if user_id == session_user_id:
        return f'User {user_id} deleted'
    else:
        return 'Yon can deleted only your profile'

@app.route('/films', methods=['GET'])
@deccorator_check_login
def films():
    filter_params = request.args
    filter_list_texts = []
    films_query = select(models.Film)
    for key, value in filter_params.items():
        if value:
            if key =='name':
                films_query = films_query.where(models.Film.name.like(f"%{value}%"))
            else:
                if key == 'rating':
                    value = float(value)
                    films_query = films_query.where(models.Film.rating == value)
                if key == 'country':
                    films_query = films_query.where(models.Film.country == value)
                if key == 'year':
                    films_query = films_query.where(models.Film.year == int(value))

    films = films_query.order_by(models.Film.added_at.desc())
    result_films = database.db_session.execute(films).scalars()
    countries = select(models.Country)
    result_countries = database.db_session.execute(countries).scalars()
    return render_template('films.html', films=result_films, countries=result_countries)


@app.route('/films', methods=['POST'])
@deccorator_check_login
def add_film():
    database.init_db()

    film_by_id = select(models.Film).where(models.Film.id == film_id)
    result_film = database.db_session.execute(film_by_id).scalar_one()

    actors = select(models.Actor).join(models.ActorsFilms, models.Actor.id == models.ActorActorsFilms.actor_id).where(
        models.ActorsFilms.film_id == film_id)
    result_actors = database.db_session.execute(actors).scalars()

    genres = select(models.Genre).join(models.GenresFilm, models.Genre.genre == models.GenreFilm.genre_id).where(
        models.GenreFilm == film_id)
    result_genres = database.db_session.execute(genres).scalars()

    return jsonify({
        "id": result_film_by_id.id,
        "name": result_film_by_id.name,
        "poster": result_film_by_id.poster,
        "description": result_film_by_id.description,
        "rating": result_film_by_id.rating,
        "country": result_film_by_id.country,
        "added_at": result_film_by_id.added_at,
        "actors": [itm.to_dict() for itm in result_actors],
        "genres": [itm.to.dict() for itm in result_genres]
    })

            
@app.route('/films/<int:film_id>', methods=['GET'])
@deccorator_check_login
def film_info(film_id):
    film = db.session.get(Film, film_id)
    if not film:
        return f'Film {film_id} not found'

    result = film
    actors = film.actors
    genres = film.genres

    return f'Film {film_id} is {result}, actors: {actors}, genres: {genres}'

@app.route('/films/<film_id>', methods=['PUT'])
@deccorator_check_login
def film_update(film_id):
    data = request.get_json() or{}
    database.init_db()

    new_film_query = select(models.Film).where(models.Film.id == film_id).values(data)
    new_film_query = database.db_session.execute(new_film_query).scalar_one()

    new_film.name = data.get("name")
    new_film.poster = data.get("poster")
    new_fillm.description = data.get("description")
    new.film.rating = data.get("rating")
    new.film.country = data.get("country")

    database.db.session.abb(new_film)
    database.db_session.commit()


    return jsonify({"film_id": film_id})

@app.route('/films/search', methods=['GET'])
def films_search():
    name = request.args.get('name', '')

    database.init_db()
    films_search_query = select(models.Film).where(models.Film.name.like(f"%{name}%")).order_by(models.Film.added_at.desc())
    result_films_search = database.db_session.execute(films_search_query).scalars()

    return jsonify([itm.to_dict() for itm in result_films_search])

@app.route('/films/<int:film_id>', methods=['DELETE'])
@deccorator_check_login
def delete_film(film_id):
    film = db.session.get(Film, film_id)

    if not film:
        return jsonify({"error": "Film not found"}), 484

    db.session.delete(film)
    db.session.commit()

    return jsonify({"fitm_id": film_id})

@app.route('/films/<int:film_id>/reting', methods=['POST'])
def film_rating(film_id):
    return f'Film {film_id} rated'

@app.route('/films/<film_id>/reting', methods=['GET'])
def film_rating_info(film_id):
    database.init_db()

    retings_guery = select(models.Feedback).where(models.Feedback.film == film_id)
    retings = database.db_session.execute(retings_guery).scalars()

    grades_query = select(
        func.avg(models.Feedback.grade).label('average'),
        func.count(models.Feedback.id).label('ratinngs_count')
    ).where(models.Feedback.film == film_id)
    grades = database.db_session.execute(grades_query).fetchone()

    return jsonify({"film_id": film_id, "retings": retings, "average_rating": grade[0], "rating_count": grade[1]})


@app.route('/films/<film_id>/reting<feedback_id>', methods=['DELETE'])
def film_rating_delete(film_id, feedback_id):
    return f'Film {film_id} rating {feedback_id} deleted'

@app.route('/films/<film_id>/reting/<feedback_id>', methods=['PUT'])
def film_rating_update(film_id, feedback_id):
    return f'Film {film_id} rating {feedback_id} updated'


@app.route('/films/<film_id>/reting/<feedback_id>/feedback', methods=['GET'])
@deccorator_check_login
def film_rating_feedback(film_id, feedback_id):
    feedback = db.session.query(Feedback).filter_by(id=feedback_id,film=film_id).first()

    if not feedback:
        return f'No feedback with id {feedback_id} for film {film_id}', 404

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

