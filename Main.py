import threading
import subprocess
import time

def run_network_stats():
    """Run the NetworkStats.py script."""
    subprocess.run(["python", "NetworkStats.py"])

def run_webserver():
    """Run the Webserver.py script."""
    subprocess.run(["python", "Webserver.py"])

if __name__ == '__main__':
    # Start the network statistics collection in a separate thread
    network_stats_thread = threading.Thread(target=run_network_stats)
    network_stats_thread.start()

    # Give it some time to start collecting data
    time.sleep(5)

    # Start the webserver in another thread
    webserver_thread = threading.Thread(target=run_webserver)
    webserver_thread.start()

    # Keep the main script running
    network_stats_thread.join()
    webserver_thread.join()
