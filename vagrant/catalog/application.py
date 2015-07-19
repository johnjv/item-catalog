from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, session as login_session
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Genre, Song
import random, string

app = Flask(__name__)

#Connect to Database and create database session
engine = create_engine('sqlite:///musicdump.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Login route
@app.route('/login')
def showLogin():
	# create a state token to prevent request forgery
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	# store it in session for later use
	login_session['state'] = state
	return "The current session state is %s" % login_session['state']

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

# Show all genres
@app.route('/')
def showGenres():
	songs = session.query(Song).order_by(asc(Song.name))
	# return jsonify(songs = [i.serialize for i in songs])
	return render_template('songs.html', songs = songs)

# Create a new music genre
@app.route('/genre/new', methods=['GET','POST'])
def newGenre():
	if request.method == 'POST':
		newGenre = Genre(name = request.form['name'])
		session.add(newGenre)
		flash('Succesfully added %s genre' % newGenre.name)
		session.commit()
		return redirect(url_for('showGenres'))
	else:
		return render_template('new-genre.html')

# Edit a genre
@app.route('/genre/<int:genre_id>/edit/', methods = ['GET', 'POST'])
def editGenre(genre_id):
	editedGenre = session.query(Genre).filter_by(id = genre_id).one()
	if request.method == 'POST':
		if request.form['name']:
			editedGenre.name = request.form['name']
			flash('Genre successfully edited %s' % editedGenre.name)
			return redirect(url_for('showGenres'))
		else:
			return render_template('edit-genre.html', genre = editedGenre)

# Delete a genre
@app.route('/genre/<int:genre_id>/delete/', methods = ['GET', 'POST'])
def deleteGenre(genre_id):
	genreToDelete = session.query(Genre).filter_by(id = genre_id).one()
	if request.method == 'POST':
		session.delete(genreToDelete)
		flash('%s successfully deleted' % genreToDelete.name)
		session.commit()
		return redirect(url_for('showGenres', genre_id = genre_id))
	else:
		return render_template('delete-genre.html', genre = genreToDelete)

# Show songs from a genre
@app.route('/genre/<int:genre_id>/')
@app.route('/genre/<int:genre_id>/songs/')
def showSongs(genre_id):
	genre = session.query(Genre).filter_by(id = genre_id).one()
	songs = session.genre(Song).filter_by(genre_id = genre_id).all()
	return render_template(song.html, songs = songs, genre = genre)

# Create a new song for a genre
@app.route('/genre/<int:genre_id>/songs/new/', methods = ['GET', 'POST'])
def newSong(genre_id):
	genre = session.query(Genre).filter_by(id = genre_id).one()
	if request.method == 'POST':
		newSong = Song(name = request.form[name],
					   band_name = request.form[band_name],
					   country = request.form[country],
					   youtube_url = request.form[youtube_url])
		session.add(newSong)
		session.commit()
		flash('New song %s successfully created' % (newSong.name))
		return redirect(url_for('showSongs', genre_id = genre_id))
	else:
		return render_template('new-song.html', genre_id = genre_id)

# Edit a song
@app.route('/genre/<int:genre_id>/song/<int:song_id>/edit', methods = ['GET', 'POST'])
def editSong(genre_id, song_id):
	editedSong = session.query(Song).filter_by(id = song_id).one()
	genre = session.query(Genre).filter_by(id = genre_id).one()
	if request.method == 'POST':
		if request.form['name']:
			editedSong.name = request.form['name']
		if request.form['band_name']:
			editedSong.band_name = request.form['band_name']
		if request.form['country']:
			editedSong.country = request.form['country']
		if request.form['youtube_url']:
			editedSong.youtube_url = request.form['youtube_url']
		session.add(editedSong)
		session.commit()
		flash('Song successfully edited')
		return redirect(url_for('showSongs', genre_id = genre_id))
	else:
		return render_template('edit-song.html', genre_id = genre_id, song_id = song_id, item = editedSong)

# Delete a song
@app.route('/genre/<int:genre_id>/songs/<int:song_id>/delete', methods = ['GET', 'POST'])
def deleteSong(genre_id, song_id):
	genre = session.query(Genre).filter_by(id = genre_id).one()
	songToDelete = session.query(Song).filter_by(id = song_id).one()
	if request.method == 'POST':
		session.delete(songToDelete)
		session.commit()
		flash('Song successfully deleted')
		return redirect(url_for('showSong', genre_id = genre_id))
	else:
		return render_template('delete-song.html', item = songToDelete)


if __name__ == '__main__':
	app.secret_key = "secret key"
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)
