import os
import sys
import urllib.error
import urllib.request

jenkins_url = os.getenv(
    "JENKINS_URL", 
    "http://localhost:8080"
).rstrip("/")

url = f"{jenkins_url}/login"

print(f"Checking Jenkins URL: {url}")

try: 
    with urllib.request.urlopen(url, timeout=5) as response:
        print(f"HTTP status: {response.status}")