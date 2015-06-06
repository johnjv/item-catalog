from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import session

app = Flask(__name__)

#Connect to Database and create database session
engine = create_engine('sqlite:///musicdump.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# JSON APIs to view music dump
@app.route('/genre/<int:genre_id>/dump/JSON')
def genreSongsJSON:
	genre = session.query(Genre).filter_by(id = genre_id).one()
	songs = session.query(Songs).filter_by(genre_id = genre_id).all()
	return jsonify(songs = [i.serialize for i in songs])

@app.route('/genre/<int:genre_id>/dump/<int:song_id>/JSON')
def songJSON(genre_id, song_id):
    song = session.query(Songs).filter_by(id = song_id).one()
    return jsonify(song = song.serialize)

@app.route('/genres/JSON')
@app.route('/genres/dump/JSON')
def genresJSON():
    genres = session.query(Genre).all()
    return jsonify(genres = [r.serialize for r in genres])


@app.route('/')
def HelloWorld():
	return "Hello World"

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)