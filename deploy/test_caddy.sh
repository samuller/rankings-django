#
# Test that Caddy routing is working correctly.
#
set -e

# https://stackoverflow.com/questions/64786/error-handling-in-bash
error() {
  local last_exit_status="$?"
  local parent_lineno="$1"
  local message="${2:-(no message ($last_exit_status))}"
  local code="${3:-$last_exit_status}"
  if [[ -n "$message" ]] ; then
    echo "Error on or near line ${parent_lineno}: ${message}; exiting with status ${code}"
  else
    echo "Error on or near line ${parent_lineno}; exiting with status ${code}"
  fi
  exit "${code}"
}
trap 'error ${LINENO}' ERR
shopt -s extdebug

# For debugging a variable, print binary/non-printing characters with either of these commands:
#     printf %s "$result" | od -vtc -to1
#     echo $result | cat -v

html_urls=( \
    # Test access via IP and hostname
    # SPA
    127.0.0.1:8080 127.0.0.1:8080/about 127.0.0.1:8080/foosball 127.0.0.1:8080/invalid_name \
    localhost:8080 localhost:8080/about localhost:8080/foosball localhost:8080/invalid_name \
    # API
    127.0.0.1:8080/api 127.0.0.1:8080/api/docs \
    localhost:8080/api localhost:8080/api/docs \
    # Admin
    127.0.0.1:8080/admin \
    localhost:8080/admin \
    # SSR
    127.0.0.1:8080/ssr 127.0.0.1:8080/ssr/about \
    localhost:8080/ssr localhost:8080/ssr/about \
)
for url in "${html_urls[@]}"
do
  result="$(curl -s -i $url)"
  test "$(echo "$result" | head -n1 | tr -d '\n\r')" = "HTTP/1.1 200 OK"
  echo "$result" | grep "<!DOCTYPE html>" 1> /dev/null
#   echo "$result" | grep '<script type="text/javascript">$(document).foundation();</script>' 1> /dev/null
done

json_urls=(
    127.0.0.1:8080/api/openapi.json \
    localhost:8080/api/openapi.json \
)
for url in "${json_urls[@]}"
do
  result="$(curl -s -i $url)"
  test "$(echo "$result" | head -n1 | tr -d '\n\r')" = "HTTP/1.1 200 OK"
  echo "$result" | grep "Content-Type: application/vnd.oai.openapi+json" 1> /dev/null
  echo "$result" | grep '"title": "rankings-django",' 1> /dev/null
done

spa_urls=()
for url in "${spa_urls[@]}"
do
  result="$(curl -s -i $url)"
  test "$(echo "$result" | head -n1 | tr -d '\n\r')" = "HTTP/1.1 200 OK"
  echo "$result" | grep "<!DOCTYPE html>" 1> /dev/null
done
