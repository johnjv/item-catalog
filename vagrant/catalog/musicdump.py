from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Restaurant, Base, MenuItem
 
engine = create_engine('sqlite:///restaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Looping genre music dump
loopingGenre = Genre(name = "looping")

session.add(loopingGenre)
session.commit()

song1 = Song(name = "",
			band_name = "",
			country = "",
			youtube_url = "",
			genre = loopingGenre)
session.add(song1)
session.commit()

song2 = Song(name = "",
			band_name = "",
			country = "",
			youtube_url = "",
			genre = loopingGenre)
session.add(song2)
session.commit()

song3 = Song(name = "",
			band_name = "",
			country = "",
			youtube_url = "",
			genre = loopingGenre)
session.add(song3)
session.commit()

song4 = Song(name = "",
			band_name = "",
			country = "",
			youtube_url = "",
			genre = loopingGenre)
session.add(song4)
session.commit()


# Video games genre music dump
videoGameGenre = Genre(name = "video game")

song1 = Song(name = "",
			band_name = "",
			country = "",
			youtube_url = "",
			genre = videoGameGenre)
session.add(song1)
session.commit()

song2 = Song(name = "",
			band_name = "",
			country = "",
			youtube_url = "",
			genre = videoGameGenre)
session.add(song2)
session.commit()

song3 = Song(name = "",
			band_name = "",
			country = "",
			youtube_url = "",
			genre = videoGameGenre)
session.add(song3)
session.commit()

song4 = Song(name = "",
			band_name = "",
			country = "",
			youtube_url = "",
			genre = videoGameGenre)
session.add(song4)
session.commit()

# Mathematical genre music dump
mathematicalGenre = Genre(name = "mathematical")

song1 = Song(name = "",
			band_name = "",
			country = "",
			youtube_url = "",
			genre = mathematicalGenre)
session.add(song1)
session.commit()

song2 = Song(name = "",
			band_name = "",
			country = "",
			youtube_url = "",
			genre = mathematicalGenre)
session.add(song2)
session.commit()

song3 = Song(name = "",
			band_name = "",
			country = "",
			youtube_url = "",
			genre = mathematicalGenre)
session.add(song3)
session.commit()

song4 = Song(name = "",
			band_name = "",
			country = "",
			youtube_url = "",
			genre = mathematicalGenre)
session.add(song4)
session.commit()


