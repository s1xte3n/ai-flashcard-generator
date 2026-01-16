#!/usr/bin/env bash
set -e

echo "🚀 Bootstrapping Vibe Coder Template repository..."

# -----------------------------
# Preconditions
# -----------------------------
if ! command -v gh &>/dev/null; then
  echo "❌ GitHub CLI (gh) is not installed."
  echo "👉 Install from: https://cli.github.com/"
  exit 1
fi

if ! gh auth status &>/dev/null; then
  echo "❌ GitHub CLI is not authenticated."
  echo "👉 Run: gh auth login"
  exit 1
fi

if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  echo "❌ Not inside a git repository."
  exit 1
fi

# -----------------------------
# Repo Info
# -----------------------------
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
OWNER_TYPE=$(gh repo view "$REPO" --json owner -q '.owner.__typename')

echo "📦 Repo: $REPO"
echo "👤 Owner type: $OWNER_TYPE"

# -----------------------------
# Ensure develop branch exists
# -----------------------------
echo "🔀 Ensuring 'develop' branch exists..."
if git show-ref --quiet refs/heads/develop; then
  git checkout develop
else
  git checkout -b develop
fi

git push -u origin develop || true

# -----------------------------
# Set default branch
# -----------------------------
echo "⭐ Setting default branch to 'develop'..."
gh repo edit "$REPO" --default-branch develop

# -----------------------------
# Enable repository features
# -----------------------------
echo "🧩 Enabling repository features..."
gh repo edit "$REPO" \
  --enable-issues=true \
  --enable-projects=true \
  --enable-wiki=false

# -----------------------------
# Enable security features
# -----------------------------
echo "🔐 Enabling security features (where available)..."
gh api -X PUT "repos/$REPO/vulnerability-alerts" >/dev/null 2>&1 || true
gh api -X PUT "repos/$REPO/automated-security-fixes" >/dev/null 2>&1 || true

# -----------------------------
# Add badges & banner to README
# -----------------------------
echo "🏷 Adding default badges & banner to README..."
README_FILE="README.md"

if ! grep -q "actions/workflows/ci.yml" "$README_FILE"; then
  echo -e "\n![CI](https://github.com/$REPO/actions/workflows/ci.yml/badge.svg)" >> "$README_FILE"
fi

if ! grep -qi "license" "$README_FILE"; then
  echo -e "\n![License](https://img.shields.io/badge/license-MIT-green.svg)" >> "$README_FILE"
fi

if ! grep -q "vibe-coder-banner" "$README_FILE"; then
  echo -e "\n![Vibe Coder Banner](https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif)" >> "$README_FILE"
fi

if git diff --quiet "$README_FILE"; then
  echo "ℹ️  No README changes to commit"
else
  git add "$README_FILE"
  git commit -m "chore: add default badges & banner to README"
  git push origin develop
fi

# -----------------------------
# Branch protection (schema-safe)
# -----------------------------
if [ "$OWNER_TYPE" = "Organization" ]; then
  RESTRICTIONS='{"users":[],"teams":[],"apps":[]}'
else
  RESTRICTIONS='null'
fi

echo "🔒 Protecting 'develop' branch..."
gh api -X PUT "repos/$REPO/branches/develop/protection" \
  -H "Accept: application/vnd.github+json" \
  --input - <<EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["ci"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": false,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 0
  },
  "restrictions": $RESTRICTIONS,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF

echo "🔒 Protecting 'main' branch..."
gh api -X PUT "repos/$REPO/branches/main/protection" \
  -H "Accept: application/vnd.github+json" \
  --input - <<EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["ci"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1
  },
  "restrictions": $RESTRICTIONS,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF

# -----------------------------
# Final message
# -----------------------------
echo ""
echo "✅ Vibe Coder Template bootstrap complete!"
echo ""
echo "Next steps:"
echo "• Create a feature branch"
echo "• Open a PR into develop"
echo "• Let CI enforce quality"
echo ""
echo "🧠 Remember: automate early, commit often, ship calmly."
