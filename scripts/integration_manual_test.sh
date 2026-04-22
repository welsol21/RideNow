#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${RIDENOW_BASE_URL:-http://127.0.0.1:8001}"
POLL_ATTEMPTS="${RIDENOW_POLL_ATTEMPTS:-20}"
POLL_INTERVAL_SECONDS="${RIDENOW_POLL_INTERVAL_SECONDS:-1}"

if command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  echo "python or python3 is required" >&2
  exit 1
fi

pretty_json() {
  printf '%s\n' "$1" | "$PYTHON_BIN" -m json.tool
}

json_field() {
  local payload="$1"
  local field="$2"
  JSON_PAYLOAD="$payload" "$PYTHON_BIN" - "$field" <<'PY'
import json
import os
import sys

field_path = sys.argv[1].split(".")
value = json.loads(os.environ["JSON_PAYLOAD"])
for part in field_path:
    value = value[part]
if isinstance(value, (dict, list)):
    print(json.dumps(value))
else:
    print(value)
PY
}

json_request_ride_payload() {
  local customer_id="$1"
  cat <<EOF
{"customer_id":"$customer_id","pickup":{"lat":53.3498,"lon":-6.2603},"dropoff":{"lat":53.3440,"lon":-6.2672}}
EOF
}

print_section() {
  local title="$1"
  printf '\n== %s ==\n' "$title" >&2
}

run_health() {
  print_section "GET /health"
  local health_response
  health_response="$(curl -sS "$BASE_URL/health")"
  pretty_json "$health_response"

  print_section "GET /ready"
  local ready_response
  ready_response="$(curl -sS "$BASE_URL/ready")"
  pretty_json "$ready_response"
}

request_ride() {
  local customer_id="$1"
  local payload
  payload="$(json_request_ride_payload "$customer_id")"

  print_section "POST /rides"
  echo "Request:" >&2
  pretty_json "$payload" >&2

  local response
  response="$(curl -sS -X POST "$BASE_URL/rides" \
    -H "Content-Type: application/json" \
    -d "$payload")"

  echo "Response:" >&2
  pretty_json "$response" >&2
  printf '%s\n' "$response"
}

poll_ride_until() {
  local ride_id="$1"
  local expected_status="$2"

  local attempt
  for ((attempt = 1; attempt <= POLL_ATTEMPTS; attempt += 1)); do
    local response
    response="$(curl -sS "$BASE_URL/rides/$ride_id")"
    local status
    status="$(json_field "$response" "status")"
    printf '[%02d/%02d] %s -> %s\n' "$attempt" "$POLL_ATTEMPTS" "$ride_id" "$status" >&2
    if [[ "$status" == "$expected_status" ]]; then
      print_section "Final GET /rides/$ride_id"
      pretty_json "$response" >&2
      return 0
    fi
    sleep "$POLL_INTERVAL_SECONDS"
  done

  echo "Ride $ride_id did not reach expected status '$expected_status'." >&2
  return 1
}

run_scenario() {
  local scenario_name="$1"
  local customer_id="$2"
  local expected_status="$3"

  print_section "Scenario: $scenario_name"
  local initial_response
  initial_response="$(request_ride "$customer_id" | tail -n 1)"
  local ride_id
  ride_id="$(json_field "$initial_response" "ride_id")"
  echo "Tracking ride_id: $ride_id" >&2
  poll_ride_until "$ride_id" "$expected_status"
  printf '%s\n' "$ride_id"
}

submit_issue() {
  local ride_id="$1"
  local payload
  payload=$(cat <<EOF
{"ride_id":"$ride_id","customer_id":"customer-demo","category":"payment","description":"Manual integration test follow-up."}
EOF
)

  print_section "POST /issues"
  echo "Request:" >&2
  pretty_json "$payload" >&2

  local response
  response="$(curl -sS -X POST "$BASE_URL/issues" \
    -H "Content-Type: application/json" \
    -d "$payload")"
  echo "Response:" >&2
  pretty_json "$response" >&2
}

print_usage() {
  cat <<EOF
Usage:
  ./scripts/integration_manual_test.sh health
  ./scripts/integration_manual_test.sh happy
  ./scripts/integration_manual_test.sh no-driver
  ./scripts/integration_manual_test.sh payment-fail
  ./scripts/integration_manual_test.sh issue <ride_id>
  ./scripts/integration_manual_test.sh all

Environment overrides:
  RIDENOW_BASE_URL=http://127.0.0.1:8001
  RIDENOW_POLL_ATTEMPTS=20
  RIDENOW_POLL_INTERVAL_SECONDS=1
EOF
}

main() {
  local command="${1:-}"

  case "$command" in
    health)
      run_health
      ;;
    happy)
      run_scenario "happy path" "customer-demo" "payment-confirmed"
      ;;
    no-driver)
      run_scenario "no-driver-available" "customer-no-driver" "no-driver-available"
      ;;
    payment-fail)
      run_scenario "payment-failed" "customer-payment-fail" "payment-failed"
      ;;
    issue)
      if [[ $# -lt 2 ]]; then
        echo "ride_id is required for the issue command" >&2
        exit 1
      fi
      submit_issue "$2"
      ;;
    all)
      run_health
      local happy_ride_id
      happy_ride_id="$(run_scenario "happy path" "customer-demo" "payment-confirmed" | tail -n 1)"
      run_scenario "no-driver-available" "customer-no-driver" "no-driver-available" >/dev/null
      run_scenario "payment-failed" "customer-payment-fail" "payment-failed" >/dev/null
      submit_issue "$happy_ride_id"
      ;;
    *)
      print_usage
      exit 1
      ;;
  esac
}

main "$@"
