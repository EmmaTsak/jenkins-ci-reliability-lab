import os
import sys
import urllib.error
import urllib.request

jenkins_url = os.getenv(
    "JENKINS_INTERNAL_URL",
    "http://jenkins-controller:8080",
).rstrip("/")

url = f"{jenkins_url}/login"

print(f"Checking Jenkins URL: {url}")

try:
    with urllib.request.urlopen(url, timeout=5) as response:
        print(f"HTTP status: {response.status}")

        if response.status == 200:
            print("Jenkins is reachable")
            sys.exit(0)

        print("ERROR: Unexpected Jenkins response")
        sys.exit(1)

except urllib.error.URLError as error:
    print(f"ERROR: Jenkins is unreachable: {error}")
    sys.exit(1)