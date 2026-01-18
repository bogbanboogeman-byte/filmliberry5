database.init_db()

    film_by_id = select(models.Film).where(models.Film.id == film_id)
    result_film = database.db_session.execute(film_by_id).scalar_one()

    actors = select(models.Actor).join(models.ActorsFilms, models.Actor.id == models.ActorActorsFilms.actor_id).where(models.ActorsFilms.film_id == film_id)
    result_actors = database.db_session.execute(actors).scalars()

    genres = select(models.Genre).join(models.GenresFilm,models.Genre.genre ==models.GenreFilm.genre_id).where(models.GenreFilm == film_id)
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