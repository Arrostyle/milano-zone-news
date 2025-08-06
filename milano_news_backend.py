import requests
import sqlite3
import threading
import time
from datetime import datetime, timedelta
import os
import json

class MilanoNewsCollector:
    def __init__(self):
        self.api_key = os.getenv('NEWSDATA_API_KEY')
        self.db_path = 'milano_news.db'
        self.init_database()

        # 125+ synonyms for maximum news coverage of the 9 target zones
        self.target_zones = {
            'Navigli': [
                'navigli', 'naviglio', 'naviglio grande', 'naviglio pavese', 'zona navigli',
                'quartiere navigli', 'darsena navigli', 'alzaia naviglio grande',
                'alzaia naviglio pavese', 'ripa ticinese navigli', 'navigli milano',
                'aperitivo navigli', 'movida navigli', 'nightlife navigli'
            ],
            'Darsena': [
                'darsena', 'darsena milano', 'porta ticinese darsena', 'piazza xxiv maggio',
                'alzaia naviglio grande darsena', 'ponte di porta ticinese', 
                'colonne san lorenzo darsena', 'aperitivo darsena', 'eventi darsena',
                'mercato darsena', 'fontana darsena'
            ],
            'Porta Ticinese': [
                'porta ticinese', 'ticinese', 'ripa di porta ticinese', 'corso porta ticinese',
                'quartiere ticinese', 'zona ticinese', 'porta ticinese milano',
                'colonne san lorenzo', 'san lorenzo', 'basilica san lorenzo',
                'parco delle basiliche', 'movida porta ticinese'
            ],
            'Via Tortona': [
                'via tortona', 'tortona', 'zona tortona', 'quartiere tortona',
                'design district tortona', 'fuorisalone tortona', 'mudec tortona',
                'museo mudec', 'base milano tortona', 'via bergognone tortona',
                'eventi tortona', 'design week tortona', 'aperitivo tortona'
            ],
            'Via Cassala': [
                'via cassala', 'cassala', 'zona cassala', 'quartiere cassala',
                'naviglio pavese cassala', 'alzaia naviglio pavese cassala',
                'fermata cassala', 'metro cassala', 'ripa cassala',
                'ponte cassala', 'mercato cassala'
            ],
            'Via Bligny': [
                'via bligny', 'bligny', 'zona bligny', 'quartiere bligny',
                'corso lodi bligny', 'san gottardo bligny', 'ticinese bligny',
                'eventi bligny', 'locale bligny', 'ristorante bligny',
                'aperitivo bligny', 'negozi bligny'
            ],
            'Piazza Napoli': [
                'piazza napoli', 'napoli', 'zona piazza napoli', 'quartiere napoli',
                'fermata napoli', 'metro napoli', 'piazza napoli milano',
                'eventi piazza napoli', 'mercato napoli', 'ristoranti piazza napoli',
                'aperitivo piazza napoli', 'negozi piazza napoli'
            ],
            'Corso San Gottardo': [
                'corso san gottardo', 'san gottardo', 'via san gottardo', 'gottardo',
                'zona san gottardo', 'quartiere san gottardo', 'ticinese san gottardo',
                'navigli san gottardo', 'eventi san gottardo', 'locale san gottardo',
                'ristorante san gottardo', 'aperitivo san gottardo', 'negozi san gottardo'
            ],
            'Via Giuseppe Meda': [
                'via giuseppe meda', 'giuseppe meda', 'meda', 'via meda',
                'zona meda', 'quartiere meda', 'corso lodi meda', 'romana meda',
                'eventi meda', 'locale meda', 'ristorante meda', 'aperitivo meda',
                'negozi meda', 'fermata meda'
            ]
        }

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                url TEXT UNIQUE NOT NULL,
                published_date TEXT NOT NULL,
                zone TEXT NOT NULL,
                is_favorite INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def clean_old_news(self, days_to_keep=30):
        "Remove news older than specified days"
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM news 
            WHERE datetime(published_date) < datetime(?)
        ''', (cutoff_date.isoformat(),))

        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        return deleted_count

    def fetch_milan_news(self):
        "Fetch news from NewsData.io API"
        if not self.api_key:
            print("Error: NEWSDATA_API_KEY not found in environment variables")
            return []

        url = "https://newsdata.io/api/1/news"

        # Search for Milan-related news in Italian and English
        params = {
            'apikey': self.api_key,
            'country': 'it',
            'language': 'it,en',
            'q': 'Milano OR Milan',
            'size': 50
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            if data['status'] == 'success':
                return data.get('results', [])
            else:
                print(f"API Error: {data}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return []

    def is_relevant_news(self, article):
        "Check if article is relevant to target zones using comprehensive synonyms"
        if not article:
            return False, None

        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        content = f"{title} {description}"

        # Check each zone and its synonyms
        for zone, synonyms in self.target_zones.items():
            for synonym in synonyms:
                if synonym.lower() in content:
                    return True, zone

        return False, None

    def save_news(self, articles):
        "Save relevant news to database"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        new_articles = 0

        for article in articles:
            is_relevant, zone = self.is_relevant_news(article)

            if is_relevant and article.get('link'):
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO news 
                        (title, description, url, published_date, zone)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        article.get('title', ''),
                        article.get('description', ''),
                        article['link'],
                        article.get('pubDate', datetime.now().isoformat()),
                        zone
                    ))

                    if cursor.rowcount > 0:
                        new_articles += 1

                except sqlite3.Error as e:
                    print(f"Database error: {e}")
                    continue

        conn.commit()
        conn.close()

        return new_articles

    def get_news(self, zone=None, date=None, favorite_only=False):
        "Retrieve news from database with filtering"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM news WHERE 1=1"
        params = []

        if zone and zone != 'all':
            query += " AND zone = ?"
            params.append(zone)

        if date:
            query += " AND date(published_date) = date(?)"
            params.append(date)

        if favorite_only:
            query += " AND is_favorite = 1"

        query += " ORDER BY datetime(published_date) DESC"

        cursor.execute(query, params)

        columns = [desc[0] for desc in cursor.description]
        results = []

        for row in cursor.fetchall():
            article = dict(zip(columns, row))
            results.append(article)

        conn.close()
        return results

    def get_available_dates(self):
        "Get list of dates with news"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT DISTINCT date(published_date) as date 
            FROM news 
            ORDER BY date DESC
        ''')

        dates = [row[0] for row in cursor.fetchall()]
        conn.close()

        return dates

    def get_zones_with_counts(self):
        "Get zones with news count"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT zone, COUNT(*) as count 
            FROM news 
            GROUP BY zone 
            ORDER BY count DESC
        ''')

        results = {}
        for row in cursor.fetchall():
            results[row[0]] = row[1]

        conn.close()
        return results

    def toggle_favorite(self, news_id):
        "Toggle favorite status of a news article"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get current favorite status
        cursor.execute("SELECT is_favorite FROM news WHERE id = ?", (news_id,))
        result = cursor.fetchone()

        if result:
            new_status = 1 if result[0] == 0 else 0
            cursor.execute(
                "UPDATE news SET is_favorite = ? WHERE id = ?", 
                (new_status, news_id)
            )
            conn.commit()
            conn.close()
            return new_status

        conn.close()
        return None

    def get_stats(self):
        "Get statistics about collected news"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total news count
        cursor.execute("SELECT COUNT(*) FROM news")
        total_news = cursor.fetchone()[0]

        # Favorites count
        cursor.execute("SELECT COUNT(*) FROM news WHERE is_favorite = 1")
        favorites = cursor.fetchone()[0]

        # News by zone
        cursor.execute('''
            SELECT zone, COUNT(*) as count 
            FROM news 
            GROUP BY zone 
            ORDER BY count DESC
        ''')
        zones = dict(cursor.fetchall())

        # Latest update
        cursor.execute("SELECT MAX(created_at) FROM news")
        latest_update = cursor.fetchone()[0]

        conn.close()

        return {
            'total_news': total_news,
            'favorites': favorites,
            'zones': zones,
            'latest_update': latest_update
        }

    def update_news(self):
        "Fetch and save new news"
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting news update...")

        try:
            articles = self.fetch_milan_news()
            if articles:
                new_count = self.save_news(articles)
                cleaned = self.clean_old_news()
                print(f"News update completed: {new_count} new articles, {cleaned} old articles cleaned")
                return new_count
            else:
                print("No articles fetched")
                return 0
        except Exception as e:
            print(f"Error during news update: {e}")
            return 0
