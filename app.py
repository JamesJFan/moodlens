import nltk

# Download the VADER lexicon
nltk.download('vader_lexicon')

from flask import Flask, render_template, request, g
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if request.method == 'POST':
        text = request.form['text']

        # Sentiment Analysis using NLTK
        sia = SentimentIntensityAnalyzer()
        sentiment_score = sia.polarity_scores(text)['compound']

        # Determine sentiment
        if sentiment_score >= 0.05:
            sentiment = 'Positive'
        elif sentiment_score <= -0.05:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'

        return render_template('result.html', text=text, sentiment=sentiment)

if __name__ == '__main__':
    app.run(debug=True)

#Sentiment Analysis Section

app = Flask(__name__)
app.config['DATABASE'] = 'sentiments.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
    return g.db

@app.route('/')
def index():
    # Retrieve entries from the database
    db = get_db()
    cursor = db.execute('SELECT text, sentiment FROM entries ORDER BY id DESC')
    entries = cursor.fetchall()
    return render_template('index.html', entries=entries)

@app.route('/analyze', methods=['POST'])
def analyze():
    if request.method == 'POST':
        text = request.form['text']

        # Sentiment Analysis using TextBlob
        blob = TextBlob(text)
        sentiment_score = blob.sentiment.polarity

        # Determine sentiment
        if sentiment_score > 0:
            sentiment = 'Positive'
        elif sentiment_score < 0:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'

        # Store entry in the database
        db = get_db()
        db.execute('INSERT INTO entries (text, sentiment) VALUES (?, ?)', (text, sentiment))
        db.commit()

        return render_template('result.html', text=text, sentiment=sentiment)

@app.teardown_appcontext
def close_db(error):
    if 'db' in g:
        g.db.close()

if __name__ == '__main__':
    # Create the database schema
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

    app.run(debug=True)
