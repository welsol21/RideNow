#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${RIDENOW_BASE_URL:-http://127.0.0.1:8001}"
POLL_ATTEMPTS="${RIDENOW_POLL_ATTEMPTS:-20}"
POLL_INTERVAL_SECONDS="${RIDENOW_POLL_INTERVAL_SECONDS:-1}"
TRACE_POLL_ATTEMPTS="${RIDENOW_TRACE_POLL_ATTEMPTS:-50}"
TRACE_POLL_INTERVAL_SECONDS="${RIDENOW_TRACE_POLL_INTERVAL_SECONDS:-0.2}"

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

join_by() {
  local delimiter="$1"
  shift
  local first="${1:-}"
  shift || true
  printf '%s' "$first"
  for item in "$@"; do
    printf '%s%s' "$delimiter" "$item"
  done
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
  local poll_mode="${3:-standard}"
  local max_attempts="$POLL_ATTEMPTS"
  local interval_seconds="$POLL_INTERVAL_SECONDS"
  local -a observed_statuses=()
  local latest_response=""

  if [[ "$poll_mode" == "trace" ]]; then
    max_attempts="$TRACE_POLL_ATTEMPTS"
    interval_seconds="$TRACE_POLL_INTERVAL_SECONDS"
  fi

  local attempt
  for ((attempt = 1; attempt <= max_attempts; attempt += 1)); do
    local response
    response="$(curl -sS "$BASE_URL/rides/$ride_id")"
    latest_response="$response"
    local status
    status="$(json_field "$response" "status")"
    printf '[%02d/%02d] %s -> %s\n' "$attempt" "$max_attempts" "$ride_id" "$status" >&2

    if [[ ${#observed_statuses[@]} -eq 0 ]]; then
      observed_statuses+=("$status")
      if [[ "$poll_mode" == "trace" ]]; then
        pretty_json "$response" >&2
      fi
    else
      local last_index=$(( ${#observed_statuses[@]} - 1 ))
      if [[ "${observed_statuses[$last_index]}" != "$status" ]]; then
        observed_statuses+=("$status")
        if [[ "$poll_mode" == "trace" ]]; then
          pretty_json "$response" >&2
        fi
      fi
    fi

    if [[ "$status" == "$expected_status" ]]; then
      if [[ "$poll_mode" == "trace" ]]; then
        print_section "Observed status path"
        printf '%s\n' "$(join_by ' -> ' "${observed_statuses[@]}")" >&2
      fi
      print_section "Final GET /rides/$ride_id"
      pretty_json "$response" >&2
      return 0
    fi
    sleep "$interval_seconds"
  done

  if [[ "$poll_mode" == "trace" && ${#observed_statuses[@]} -gt 0 ]]; then
    print_section "Observed status path"
    printf '%s\n' "$(join_by ' -> ' "${observed_statuses[@]}")" >&2
  fi
  if [[ -n "$latest_response" ]]; then
    print_section "Last observed GET /rides/$ride_id"
    pretty_json "$latest_response" >&2
  fi
  echo "Ride $ride_id did not reach expected status '$expected_status'." >&2
  return 1
}

run_scenario() {
  local scenario_name="$1"
  local customer_id="$2"
  local expected_status="$3"
  local poll_mode="${4:-standard}"

  print_section "Scenario: $scenario_name"
  local initial_response
  initial_response="$(request_ride "$customer_id" | tail -n 1)"
  local ride_id
  ride_id="$(json_field "$initial_response" "ride_id")"
  echo "Tracking ride_id: $ride_id" >&2
  poll_ride_until "$ride_id" "$expected_status" "$poll_mode"
  printf '%s\n' "$ride_id"
}

run_named_scenario() {
  local scenario_key="$1"
  local poll_mode="${2:-standard}"
  local scenario_name
  local customer_id
  local expected_status

  case "$scenario_key" in
    happy)
      scenario_name="happy path"
      customer_id="customer-demo"
      expected_status="payment-confirmed"
      ;;
    no-driver)
      scenario_name="no-driver-available"
      customer_id="customer-no-driver"
      expected_status="no-driver-available"
      ;;
    payment-fail)
      scenario_name="payment-failed"
      customer_id="customer-payment-fail"
      expected_status="payment-failed"
      ;;
    *)
      echo "Unsupported scenario: $scenario_key" >&2
      exit 1
      ;;
  esac

  run_scenario "$scenario_name" "$customer_id" "$expected_status" "$poll_mode"
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
  ./scripts/integration_manual_test.sh trace happy
  ./scripts/integration_manual_test.sh trace no-driver
  ./scripts/integration_manual_test.sh trace payment-fail
  ./scripts/integration_manual_test.sh issue <ride_id>
  ./scripts/integration_manual_test.sh all

Environment overrides:
  RIDENOW_BASE_URL=http://127.0.0.1:8001
  RIDENOW_POLL_ATTEMPTS=20
  RIDENOW_POLL_INTERVAL_SECONDS=1
  RIDENOW_TRACE_POLL_ATTEMPTS=50
  RIDENOW_TRACE_POLL_INTERVAL_SECONDS=0.2
EOF
}

main() {
  local command="${1:-}"

  case "$command" in
    health)
      run_health
      ;;
    happy)
      run_named_scenario "happy"
      ;;
    no-driver)
      run_named_scenario "no-driver"
      ;;
    payment-fail)
      run_named_scenario "payment-fail"
      ;;
    trace)
      if [[ $# -lt 2 ]]; then
        echo "trace requires a scenario: happy, no-driver, or payment-fail" >&2
        exit 1
      fi
      run_named_scenario "$2" "trace"
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
      happy_ride_id="$(run_named_scenario "happy" | tail -n 1)"
      run_named_scenario "no-driver" >/dev/null
      run_named_scenario "payment-fail" >/dev/null
      submit_issue "$happy_ride_id"
      ;;
    *)
      print_usage
      exit 1
      ;;
  esac
}

main "$@"
