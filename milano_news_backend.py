import os
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
import requests
import time
import threading
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Configurazione API NewsData.io
NEWSDATA_API_KEY = os.environ.get('NEWSDATA_API_KEY')
NEWSDATA_URL = "https://newsdata.io/api/1/news"

# Zone di Milano con sinonimi estesi
MILANO_ZONES = {
    'navigli': ['navigli', 'naviglio', 'canale', 'alzaia', 'ripa ticinese', 'porta genova', 'darsena navigli'],
    'darsena': ['darsena', 'porta ticinese sud', 'zona darsena', 'ripa porta ticinese'],
    'porta_ticinese': ['porta ticinese', 'ticinese', 'colonne san lorenzo', 'san lorenzo', 'corso ticinese'],
    'via_tortona': ['via tortona', 'tortona', 'zona tortona', 'superstudio'],
    'via_cassala': ['via cassala', 'cassala', 'zona cassala'],
    'via_bligny': ['via bligny', 'bligny', 'zona bligny'],
    'piazza_napoli': ['piazza napoli', 'p.za napoli', 'zona napoli'],
    'corso_san_gottardo': ['corso san gottardo', 'san gottardo', 'zona san gottardo'],
    'via_giuseppe_meda': ['via giuseppe meda', 'giuseppe meda', 'via meda', 'meda']
}

def init_db():
    """Inizializza il database SQLite"""
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS news
                 (id INTEGER PRIMARY KEY, title TEXT, description TEXT, 
                  link TEXT UNIQUE, published_at TEXT, zone TEXT, 
                  created_at TEXT)''')
    conn.commit()
    conn.close()

def fetch_news():
    """Raccoglie notizie dalle API per tutte le zone"""
    if not NEWSDATA_API_KEY:
        print("API Key non configurata!")
        return
    
    try:
        # Query generale per Milano
        params = {
            'apikey': NEWSDATA_API_KEY,
            'country': 'it',
            'language': 'it',
            'q': 'Milano',
            'size': 50
        }
        
        response = requests.get(NEWSDATA_URL, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('results', [])
            
            conn = sqlite3.connect('news.db')
            c = conn.cursor()
            
            for article in articles:
                # Classifica l'articolo per zona
                zone = classify_article(article)
                if zone:
                    try:
                        c.execute('''INSERT OR IGNORE INTO news 
                                   (title, description, link, published_at, zone, created_at)
                                   VALUES (?, ?, ?, ?, ?, ?)''',
                                (article.get('title', ''),
                                 article.get('description', ''),
                                 article.get('link', ''),
                                 article.get('pubDate', ''),
                                 zone,
                                 datetime.now().isoformat()))
                    except:
                        continue
            
            conn.commit()
            conn.close()
            print(f"Raccolte {len(articles)} notizie")
        
    except Exception as e:
        print(f"Errore raccolta notizie: {e}")

def classify_article(article):
    """Classifica un articolo basandosi sui sinonimi delle zone"""
    title = (article.get('title', '') + ' ' + article.get('description', '')).lower()
    
    for zone, keywords in MILANO_ZONES.items():
        for keyword in keywords:
            if keyword.lower() in title:
                return zone
    return None

@app.route('/')
def index():
    """Pagina principale"""
    return render_template('index.html')

@app.route('/api/news')
def get_news():
    """API per ottenere le notizie"""
    zone = request.args.get('zone', 'all')
    
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    
    if zone == 'all':
        c.execute('SELECT * FROM news ORDER BY published_at DESC LIMIT 100')
    else:
        c.execute('SELECT * FROM news WHERE zone = ? ORDER BY published_at DESC LIMIT 50', (zone,))
    
    news_data = []
    for row in c.fetchall():
        news_data.append({
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'link': row[3],
            'published_at': row[4],
            'zone': row[5]
        })
    
    conn.close()
    return jsonify({'news': news_data})

if __name__ == '__main__':
    # Inizializza database
    init_db()
    
    # Scheduler per raccolta automatica notizie
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_news, 'interval', hours=1)
    scheduler.start()
    
    # Raccolta iniziale
    fetch_news()
    
    # Avvia server con configurazione Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
