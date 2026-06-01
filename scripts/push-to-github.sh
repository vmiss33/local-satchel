#!/usr/bin/env bash
set -euo pipefail

REPO_NAME="local-satchel"
DESCRIPTION="Pack, run, and connect local AI models."
VISIBILITY="${VISIBILITY:-public}"

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "GITHUB_TOKEN is not set."
  echo "Create a GitHub classic PAT with repo scope, then run:"
  echo "  export GITHUB_TOKEN='PASTE_TOKEN_HERE'"
  echo "  VISIBILITY=public ./scripts/push-to-github.sh"
  exit 1
fi

if [[ "$VISIBILITY" != "public" && "$VISIBILITY" != "private" ]]; then
  echo "VISIBILITY must be public or private."
  exit 1
fi

GH_USER=$(curl -fsS -H "Authorization: token ${GITHUB_TOKEN}" https://api.github.com/user | python3 -c 'import sys,json; print(json.load(sys.stdin)["login"])')

echo "GitHub user: ${GH_USER}"
echo "Repository: ${GH_USER}/${REPO_NAME} (${VISIBILITY})"

HTTP_CODE=$(curl -sS -o /tmp/local-satchel-create-repo.json -w '%{http_code}' \
  -X POST \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d "{\"name\":\"${REPO_NAME}\",\"description\":\"${DESCRIPTION}\",\"private\":$([[ \"$VISIBILITY\" == \"private\" ]] && echo true || echo false),\"has_issues\":true,\"has_projects\":true,\"has_wiki\":false}")

if [[ "$HTTP_CODE" == "201" ]]; then
  echo "Created repository."
elif [[ "$HTTP_CODE" == "422" ]] && grep -q 'name already exists' /tmp/local-satchel-create-repo.json; then
  echo "Repository already exists; continuing."
else
  echo "GitHub API returned HTTP ${HTTP_CODE}:"
  python3 -m json.tool /tmp/local-satchel-create-repo.json || cat /tmp/local-satchel-create-repo.json
  exit 1
fi

git remote remove origin 2>/dev/null || true
git remote add origin "https://${GH_USER}:${GITHUB_TOKEN}@github.com/${GH_USER}/${REPO_NAME}.git"
git push -u origin main
# Replace token-bearing remote with a safe URL after push.
git remote set-url origin "https://github.com/${GH_USER}/${REPO_NAME}.git"

echo "Pushed: https://github.com/${GH_USER}/${REPO_NAME}"
