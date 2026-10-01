#!/bin/sh

THRESHOLD=${DISK_THRESHOLD:-90}

USAGE=$(df -P / | awk 'NR==2 {print $5}' | tr -d '%')

echo "Disk usage: ${USAGE}%"
echo "Threshold: ${THRESHOLD}%"

if [ "$USAGE" -ge "$THRESHOLD" ]; then
    echo "ERROR: Disk usage exceeds threshold of ${THRESHOLD}%"
    exit 1
fi

echo "Disk capacity OK"