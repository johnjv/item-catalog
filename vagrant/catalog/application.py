from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Genre, Song

app = Flask(__name__)

#Connect to Database and create database session
engine = create_engine('sqlite:///musicdump.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# JSON APIs to view music dump
@app.route('/genre/<int:genre_id>/JSON')
def genreSongsJSON(genre_id):
	genre = session.query(Genre).filter_by(id = genre_id).one()
	songs = session.query(Song).filter_by(genre_id = genre_id).all()
	return jsonify(songs = [i.serialize for i in songs])

@app.route('/genre/<int:genre_id>/<int:song_id>/JSON')
def songJSON(genre_id, song_id):
    song = session.query(Song).filter_by(id = song_id).one()
    return jsonify(song = song.serialize)

@app.route('/genre/JSON')
def genresJSON():
    genres = session.query(Genre).all()
    return jsonify(genres = [i.serialize for i in genres])

# Show all of music dump
@app.route('/')
def homepage():
	songs = session.query(Song).order_by(asc(Song.name))
	# return jsonify(songs = [i.serialize for i in songs])
	return render_template('songs.html', songs = songs)

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)