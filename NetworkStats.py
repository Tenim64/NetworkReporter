import subprocess
import sqlite3
import time
from datetime import datetime
import speedtest
import re

# Initialize SQLite database (persistent storage)
conn = sqlite3.connect('network_stats.db')
cursor = conn.cursor()

# Create tables to store ping/packet loss and speed test statistics
cursor.execute('''
CREATE TABLE IF NOT EXISTS ping_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    ping REAL,
    packet_loss REAL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS speed_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    download_speed REAL,
    upload_speed REAL
)
''')
conn.commit()

def get_ping_statistics():
    """Ping a host and extract ping latency and packet loss."""
    # print("Getting ping statistics...")
    try:
        # Use '-c 4' to send 4 pings and '-w' to set an overall timeout in seconds
        result = subprocess.run(
            ["ping", "-c", "4", "-w", "5", "8.8.8.8"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Process the output using regular expressions
        output = result.stdout
        times = re.findall(r"time=(\d+\.?\d*) ms", output)
        packet_loss = re.search(r"(\d+)% packet loss", output)

        # Calculate average ping time if available
        avg_ping_time = sum(map(float, times)) / len(times) if times else None
        packet_loss_percentage = int(packet_loss.group(1)) if packet_loss else None

        return avg_ping_time, packet_loss_percentage

    except subprocess.CalledProcessError as e:
        print("Ping command failed:", e)
        return None, None

    except subprocess.TimeoutExpired:
        print("Ping command timed out.")
        return None, None

def store_ping_statistics():
    """Store ping and packet loss into the database."""
    ping, packet_loss = get_ping_statistics()

    if ping is not None and packet_loss is not None:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
        INSERT INTO ping_stats (timestamp, ping, packet_loss)
        VALUES (?, ?, ?)
        ''', (timestamp, ping, packet_loss))
        conn.commit()

def get_speed_statistics():
    """Run speed test and return download and upload speeds."""
    # print("Getting speed statistics...")

    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1_000_000
        upload_speed = st.upload() / 1_000_000
        return download_speed, upload_speed
    except Exception as e:
        print(f"Error occurred during speed test: {e}")
        return None, None

def store_speed_statistics():
    """Store download and upload speeds into the database."""
    download_speed, upload_speed = get_speed_statistics()

    if download_speed is not None and upload_speed is not None:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
        INSERT INTO speed_stats (timestamp, download_speed, upload_speed)
        VALUES (?, ?, ?)
        ''', (timestamp, download_speed, upload_speed))
        conn.commit()

def run_network_tests(speed_test_interval=60, ping_test_interval=5):
    """Continuously run network tests and store data."""
    # print("Running network tests...")

    speed_test_interval = 300  # Run speed test every 300 seconds (5 minute)
    ping_test_interval = 5    # Run ping test every 5 seconds
    last_speed_test_time = time.time()

    while True:
        current_time = time.time()

        store_ping_statistics()
        time.sleep(ping_test_interval)

        if current_time - last_speed_test_time >= speed_test_interval:
            store_speed_statistics()
            last_speed_test_time = current_time


run_network_tests()