from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from milano_news_backend import MilanoNewsCollector
import threading
import time

app = Flask(__name__)
CORS(app)

# Global collector instance
collector = MilanoNewsCollector()

def background_update():
    """Background thread for hourly news updates"""
    while True:
        try:
            collector.update_news()
            time.sleep(3600)  # Wait 1 hour
        except Exception as e:
            print(f"Background update error: {e}")
            time.sleep(300)  # Wait 5 minutes on error

def start_background_updates(collector_instance):
    """Start background update thread"""
    global collector
    collector = collector_instance

    # Initial news fetch
    collector.update_news()

    # Start background thread
    update_thread = threading.Thread(target=background_update, daemon=True)
    update_thread.start()
    print("Background updates started - news will update hourly")

@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')

@app.route('/api/news')
def get_news():
    """Get news with optional filtering"""
    zone = request.args.get('zone', 'all')
    date = request.args.get('date')
    favorites_only = request.args.get('favorites') == 'true'

    try:
        news = collector.get_news(zone=zone, date=date, favorite_only=favorites_only)
        return jsonify({
            'status': 'success',
            'news': news,
            'count': len(news)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/zones')
def get_zones():
    """Get available zones with news counts"""
    try:
        zones = collector.get_zones_with_counts()
        return jsonify({
            'status': 'success',
            'zones': zones
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/dates')
def get_dates():
    """Get available dates with news"""
    try:
        dates = collector.get_available_dates()
        return jsonify({
            'status': 'success',
            'dates': dates
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/favorite', methods=['POST'])
def toggle_favorite():
    """Toggle favorite status of news article"""
    try:
        data = request.get_json()
        news_id = data.get('id')

        if not news_id:
            return jsonify({
                'status': 'error',
                'message': 'Missing news ID'
            }), 400

        new_status = collector.toggle_favorite(news_id)

        if new_status is not None:
            return jsonify({
                'status': 'success',
                'is_favorite': new_status == 1
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'News not found'
            }), 404

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/stats')
def get_stats():
    """Get news statistics"""
    try:
        stats = collector.get_stats()
        return jsonify({
            'status': 'success',
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/update', methods=['POST'])
def manual_update():
    """Manually trigger news update"""
    try:
        new_count = collector.update_news()
        return jsonify({
            'status': 'success',
            'message': f'Update completed: {new_count} new articles',
            'new_articles': new_count
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    start_background_updates(collector)
    app.run(debug=True, host='0.0.0.0', port=5000)
