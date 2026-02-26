#!/bin/bash

#################################
# Configuração
#################################

VERSION=1
SITE_URL="http://localhost"
TIMEOUT=10

#################################
# Timestamp
#################################

timestamp=$(date +%s)

#################################
# CPU %
#################################

cpu_percent=$(top -bn1 | grep "Cpu(s)" | awk '{print $2+$4}')
cpu_percent=$(printf "%.1f" "${cpu_percent:-0}")

#################################
# RAM %
#################################

ram_total=$(free | awk '/Mem:/ {print $2}')
ram_available=$(free | awk '/Mem:/ {print $7}')

if [ -z "$ram_total" ] || [ "$ram_total" -eq 0 ]; then
    ram_free_percent=0
else
    ram_free_percent=$(awk "BEGIN {printf \"%.1f\", ($ram_available/$ram_total)*100}")
fi

#################################
# Disco %
#################################

disk_percent=$(df -P / | awk 'END {print $5}' | tr -d '%')

if [ -z "$disk_percent" ]; then
    disk_percent=0
fi

#################################
# Swap %
#################################

swap_total=$(free | awk '/Swap:/ {print $2}')
swap_used=$(free | awk '/Swap:/ {print $3}')

if [ -z "$swap_total" ] || [ "$swap_total" -eq 0 ]; then
    swap_percent=0
else
    swap_percent=$(awk "BEGIN {printf \"%.1f\", ($swap_used/$swap_total)*100}")
fi

#################################
# Apache status
#################################

apache_raw=$(systemctl is-active apache2 2>/dev/null)

case "$apache_raw" in
    active)
        apache_status="running"
        ;;
    *)
        apache_status="stopped"
        ;;
esac

#################################
# MySQL status
#################################

mysql_raw=$(systemctl is-active mariadb 2>/dev/null || systemctl is-active mysql 2>/dev/null)

case "$mysql_raw" in
    active)
        mysql_status="running"
        ;;
    *)
        mysql_status="stopped"
        ;;
esac

#################################
# HTTP status + response time
#################################

curl_result=$(curl \
    -m $TIMEOUT \
    -o /dev/null \
    -s \
    -w "%{http_code} %{time_total}" \
    $SITE_URL)

http_status=$(echo "$curl_result" | awk '{print $1}')
response_time=$(echo "$curl_result" | awk '{print $2}')

if [ -z "$http_status" ]; then
    http_status=-1
fi

if [ -z "$response_time" ]; then
    response_time=-1
fi

#################################
# JSON output
#################################

cat <<EOF > /tmp/sentinel_status.json
{
 "version": $VERSION,
 "timestamp": $timestamp,
 "cpu_percent": $cpu_percent,
 "ram_free_percent": $ram_free_percent,
 "disk_percent": $disk_percent,
 "swap_percent": $swap_percent,
 "apache": "$apache_status",
 "mysql": "$mysql_status",
 "http_status": $http_status,
 "response_time": $response_time
}
EOF
