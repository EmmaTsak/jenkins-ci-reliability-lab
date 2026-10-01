import base64
import json
import os
import shutil
import urllib.error
import urllib.request

JENKINS_URL = os.getenv("JENKINS_URL", "http://localhost:8080").rstrip("/")
JENKINS_USER = os.getenv("JENKINS_USER")
JENKINS_API_TOKEN = os.getenv("JENKINS_API_TOKEN")

JOB_NAME = "jenkins-ci-reliability-lab"


def api_get(path):
    url = f"{JENKINS_URL}{path}"

    request = urllib.request.Request(url)

    if JENKINS_USER and JENKINS_API_TOKEN:
        credentials = f"{JENKINS_USER}:{JENKINS_API_TOKEN}"
        encoded = base64.b64encode(credentials.encode()).decode()
        request.add_header("Authorization", f"Basic {encoded}")

    with urllib.request.urlopen(request, timeout=5) as response:
        return json.load(response)


def disk_usage():
    total, used, free = shutil.disk_usage("/")
    return round((used / total) * 100, 1)


def main():
    print("=" * 45)
    print(" Jenkins CI Reliability Dashboard")
    print("=" * 45)

    try:
        api_get("/api/json")
        print("Jenkins status: ONLINE")
    except urllib.error.URLError as error:
        print("Jenkins status: OFFLINE")
        print(f"Error: {error}")
        return

    computers = api_get("/computer/api/json")["computer"]

    online = [
        computer["displayName"]
        for computer in computers
        if not computer["offline"]
    ]

    offline = [
        computer["displayName"]
        for computer in computers
        if computer["offline"]
    ]

    queue = api_get("/queue/api/json")["items"]

    job = api_get(
        f"/job/{JOB_NAME}/api/json"
        "?tree=builds[number,result,duration]{0,10}"
    )

    builds = job["builds"]

    failed = [
        build for build in builds
        if build["result"] == "FAILURE"
    ]

    completed_durations = [
        build["duration"]
        for build in builds
        if build["duration"] > 0
    ]

    if completed_durations:
        average_duration = (
            sum(completed_durations)
            / len(completed_durations)
            / 1000
        )
    else:
        average_duration = 0

    print()
    print(f"Online agents:  {len(online)}")
    for agent in online:
        print(f"  + {agent}")

    print()
    print(f"Offline agents: {len(offline)}")
    for agent in offline:
        print(f"  - {agent}")

    print()
    print(f"Queue size: {len(queue)}")
    print(f"Recent builds: {len(builds)}")
    print(f"Failed builds: {len(failed)}")
    print(f"Average duration: {average_duration:.1f}s")
    print(f"Disk usage: {disk_usage()}%")

    print()
    print("Recent build results:")

    for build in builds[:5]:
        print(
            f"  #{build['number']}: "
            f"{build['result'] or 'RUNNING'}"
        )


if __name__ == "__main__":
    main()