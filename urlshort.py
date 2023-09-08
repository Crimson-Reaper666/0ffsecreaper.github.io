from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import random
import string

app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///url_shortener.db'
db = SQLAlchemy(app)

class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(512), nullable=False, unique=True)
    short_url = db.Column(db.String(6), nullable=False, unique=True)

@app.route('/')
def index():
    return render_template('index.html')

# Short URL generate
def generate_short_url():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

@app.route('/shorten', methods=['POST'])
def shorten_url():
    long_url = request.form.get('long_url')
    existing_url = Url.query.filter_by(long_url=long_url).first()

    if existing_url:
        return f'Shortened Url: {request.url_root}{existing_url.short_url}'

    short_url = generate_short_url()
    new_url = Url(long_url=long_url, short_url=short_url)

    # Use a context manager to work within the application context
    with app.app_context():
        db.session.add(new_url)
        db.session.commit()

    return f'Shortened Url: {request.url_root}{short_url}'

@app.route('/<short_url>')
def redirect_to_long_url(short_url):
    url_entry = Url.query.filter_by(short_url=short_url).first()
    if url_entry:
        return redirect(url_entry.long_url)
    return "URL not found"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
