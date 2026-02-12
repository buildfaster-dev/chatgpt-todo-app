#!/bin/bash
# MCP Server curl examples
# Usage: Start the server first with:
#   uvicorn src.server:app --host localhost --port 8000
# Then run: bash test-curl.sh

BASE="http://localhost:8000/mcp"
HEADERS=(-H "Content-Type: application/json" -H "Accept: application/json, text/event-stream")

echo "=== 1. Initialize session ==="
RESPONSE=$(curl -s -D - -X POST "$BASE" \
  "${HEADERS[@]}" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-03-26",
      "capabilities": {},
      "clientInfo": {"name": "curl-test", "version": "1.0"}
    }
  }')

SESSION_ID=$(echo "$RESPONSE" | grep -i "mcp-session-id" | tr -d '\r' | awk '{print $2}')
echo "$RESPONSE" | tail -1
echo ""
echo "Session ID: $SESSION_ID"
echo ""

HEADERS+=(-H "mcp-session-id: $SESSION_ID")

echo "=== 2. List tools ==="
curl -s -X POST "$BASE" "${HEADERS[@]}" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
echo -e "\n"

echo "=== 3. Add task ==="
curl -s -X POST "$BASE" "${HEADERS[@]}" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"add_task","arguments":{"title":"Buy groceries"}}}'
echo -e "\n"

echo "=== 4. Add another task ==="
curl -s -X POST "$BASE" "${HEADERS[@]}" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"add_task","arguments":{"title":"Clean the house"}}}'
echo -e "\n"

echo "=== 5. List all tasks ==="
curl -s -X POST "$BASE" "${HEADERS[@]}" \
  -d '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"list_tasks","arguments":{}}}'
echo -e "\n"

echo "=== 6. Complete task 1 ==="
curl -s -X POST "$BASE" "${HEADERS[@]}" \
  -d '{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"complete_task","arguments":{"task_id":1}}}'
echo -e "\n"

echo "=== 7. List completed tasks ==="
curl -s -X POST "$BASE" "${HEADERS[@]}" \
  -d '{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"list_tasks","arguments":{"filter":"complete"}}}'
echo -e "\n"

echo "=== 8. Decompose task 2 ==="
curl -s -X POST "$BASE" "${HEADERS[@]}" \
  -d '{"jsonrpc":"2.0","id":8,"method":"tools/call","params":{"name":"decompose_task","arguments":{"task_id":2,"subtask_titles":["Vacuum","Mop floors","Do dishes"]}}}'
echo -e "\n"

echo "=== 9. Delete task 1 ==="
curl -s -X POST "$BASE" "${HEADERS[@]}" \
  -d '{"jsonrpc":"2.0","id":9,"method":"tools/call","params":{"name":"delete_task","arguments":{"task_id":1}}}'
echo -e "\n"

echo "=== 10. Final task list ==="
curl -s -X POST "$BASE" "${HEADERS[@]}" \
  -d '{"jsonrpc":"2.0","id":10,"method":"tools/call","params":{"name":"list_tasks","arguments":{}}}'
echo -e "\n"
