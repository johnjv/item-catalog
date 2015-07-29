from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, session as login_session, make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Genre, Song
import random, string
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
import requests

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
	return render_template('login.html')

@app.route('/gconnect')
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

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
	genres = session.query(Genre).order_by(asc(Genre.name))
	# return jsonify(songs = [i.serialize for i in songs])
	return render_template('songs.html', songs = songs, genres = genres)

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
	genres = session.query(Genre).order_by(asc(Genre.name))
	songs = session.query(Song).filter_by(genre_id = genre_id).all()
	return render_template('songs.html', songs = songs, genre = genre, genres = genres)

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
