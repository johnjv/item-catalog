from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import session

app = Flask(__name__)

@app.route('/')
def HelloWorld():
	return "Hello World"

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)