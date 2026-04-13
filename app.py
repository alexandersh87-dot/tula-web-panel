# app.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, jsonify
import asyncio

# Импортируем функции напрямую
from core.digests import get_digest_text
from core.ticker import get_ticker_text
from core.dictors import get_dictors_text
from core.schedule import get_schedule_text
from core.shootings import get_shootings_text
from core.weather import get_weather_response

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/digest')
def api_digest():
    try:
        text = get_digest_text()
        return jsonify({"status": "ok", "data": text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/ticker')
def api_ticker():
    try:
        text = get_ticker_text()
        return jsonify({"status": "ok", "data": text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/dictors')
def api_dictors():
    try:
        text = get_dictors_text()
        return jsonify({"status": "ok", "data": text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/schedule/<period>')
def api_schedule(period):
    try:
        text = get_schedule_text(period)
        return jsonify({"status": "ok", "data": text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/shootings/<period>')
def api_shootings(period):
    try:
        text = get_shootings_text(period)
        return jsonify({"status": "ok", "data": text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/weather/<mode>')
def api_weather(mode):
    try:
        text = asyncio.run(get_weather_response(mode))
        return jsonify({"status": "ok", "data": text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)