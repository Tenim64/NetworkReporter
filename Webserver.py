from flask import Flask, jsonify, render_template
import sqlite3
import plotly.graph_objs as go
import plotly.io as pio
from datetime import datetime

app = Flask(__name__)

# Function to fetch data from the SQLite database
def fetch_ping_data():
    conn = sqlite3.connect('network_stats.db')
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, ping, packet_loss FROM ping_stats ORDER BY id DESC")
    data = cursor.fetchall()
    conn.close()
    return data

def fetch_speed_data():
    conn = sqlite3.connect('network_stats.db')
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, download_speed, upload_speed FROM speed_stats ORDER BY id DESC")
    data = cursor.fetchall()
    conn.close()
    return data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/earliest_timestamp', methods=['GET'])
def earliest_timestamp():
    conn = sqlite3.connect('network_stats.db')
    cursor = conn.cursor()
    
    # Query to get the minimum timestamp from all relevant tables
    cursor.execute("SELECT MIN(timestamp) FROM ping_stats")
    earliest_ping = cursor.fetchone()[0]

    cursor.execute("SELECT MIN(timestamp) FROM speed_stats")
    earliest_speed = cursor.fetchone()[0]

    conn.close()

    if earliest_ping is None and earliest_speed is None:
        return jsonify({"earliest_timestamp": None})
    
    if earliest_ping is None:
        return jsonify({"earliest_timestamp": earliest_speed})
    
    if earliest_speed is None:
        return jsonify({"earliest_timestamp": earliest_ping})

    # Return the earliest timestamp in ISO format
    earliest = min(earliest_ping, earliest_speed)
    return jsonify({"earliest_timestamp": earliest})

@app.route('/ping_data')
def ping_data():
    data = fetch_ping_data()
    return jsonify(data)

@app.route('/speed_data')
def speed_data():
    data = fetch_speed_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
