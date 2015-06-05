from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import session

app = Flask(__name__)

#Connect to Database and create database session
engine = create_engine('sqlite:///musicdump.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def HelloWorld():
	return "Hello World"

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)