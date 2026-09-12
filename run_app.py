#!/usr/bin/env python3
"""
KalaConnect AI - Customer Marketplace & AI Space Recommendation Studio
Launcher Script for Member 5
Starts a local HTTP server and opens the browser automatically.
"""

import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8000

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS and caching headers for smooth local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

def run_server():
    # Set current working directory to this script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    handler = CustomHandler
    
    # Try preferred port, or fall back to an available one
    global PORT
    for attempt_port in range(PORT, PORT + 10):
        try:
            with socketserver.TCPServer(("", attempt_port), handler) as httpd:
                url = f"http://localhost:{attempt_port}"
                print("=" * 70)
                print("** KALACONNECT AI - CUSTOMER MARKETPLACE & AI SPACE STUDIO (MEMBER 5) **")
                print("=" * 70)
                print(f">> Server running at: {url}")
                print(f">> Root directory:   {script_dir}")
                print(f">> Press Ctrl+C to stop the server")
                print("=" * 70)
                
                # Open browser
                webbrowser.open(url)
                httpd.serve_forever()
        except OSError:
            continue

if __name__ == '__main__':
    try:
        run_server()
    except KeyboardInterrupt:
        print("\nServer stopped successfully.")
        sys.exit(0)
