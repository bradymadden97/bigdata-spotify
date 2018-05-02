from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
import time
import generate


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('lyricgen.html')
	
@app.route('/generate')
def generate_lyrics():
	genre = request.args.get('g')
	if not genre:
		return jsonify({'err': 1})
	
	lyrics, err = generate.lyrics(genre)
	
	r = {'lyrics': lyrics, 'err': err}
	return jsonify(r)