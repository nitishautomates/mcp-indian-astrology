#!/bin/bash
# ═══════════════════════════════════════════════════════════
# Divine API — MCP Deployment Script
# Run this after making code changes to any MCP server
# ═══════════════════════════════════════════════════════════

set -e

# Directory this script lives in — used as the local source for the
# co-located MCP (Indian Astrology). Other MCPs live in their own repos;
# pass their local path via the LOCAL_DIR argument to deploy_mcp, or leave
# empty to treat the VPS copy as the source of truth.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ─── Secrets ───────────────────────────────────────────────
# Do NOT hardcode credentials here. Provide them via environment
# variables, or via a local, git-ignored secrets file. To set up:
#   cp mcp-deploy.env.example mcp-deploy.env   # then fill in real values
# mcp-deploy.env is listed in .gitignore and never committed.
if [ -f "$SCRIPT_DIR/mcp-deploy.env" ]; then
    set -a
    . "$SCRIPT_DIR/mcp-deploy.env"
    set +a
fi

: "${VPS_USER:?Missing VPS_USER — set it in $SCRIPT_DIR/mcp-deploy.env or the environment}"
: "${VPS_HOST:?Missing VPS_HOST — set it in $SCRIPT_DIR/mcp-deploy.env or the environment}"
: "${VPS_PASS:?Missing VPS_PASS — set it in $SCRIPT_DIR/mcp-deploy.env or the environment}"
PYPI_TOKEN="${PYPI_TOKEN:-}"   # optional; only required for the PyPI publish step

echo "═══════════════════════════════════════════"
echo "  Divine API — MCP Deployment"
echo "═══════════════════════════════════════════"
echo ""
echo "Which MCP do you want to deploy?"
echo "  1) Indian Astrology"
echo "  2) Western Astrology"
echo "  3) Horoscope & Numerology"
echo "  4) All three"
echo ""
read -p "Enter choice (1-4): " CHOICE

# ─── Set variables based on choice ───
deploy_mcp() {
    local NAME=$1
    local VPS_DIR=$2
    local PKG_DIR=$3
    local GITHUB_REPO=$4
    local PORT=$5
    local LOCAL_DIR=$6   # local source dir holding the updated server.py (optional)

    echo ""
    echo "───────────────────────────────────────"
    echo "  Deploying: $NAME"
    echo "───────────────────────────────────────"

    # Step 0: Upload local server.py to the VPS (the actual source of the change).
    # Without this, the deploy rebuilds from whatever server.py already sits on the
    # VPS — silently shipping stale code.
    echo ""
    echo "Step 0/6: Uploading local server.py to VPS..."
    if [ -n "$LOCAL_DIR" ] && [ -f "$LOCAL_DIR/server.py" ]; then
        # Fail fast on a syntax error before it ever reaches production.
        if ! python3 -c "import ast,sys; ast.parse(open('$LOCAL_DIR/server.py').read())"; then
            echo "  ✗ Local server.py has a syntax error — aborting deploy."
            return 1
        fi
        # Back up the remote copy, then upload.
        sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "
            cd /home/$VPS_USER/$VPS_DIR
            cp server.py server.py.bak.\$(date +%Y%m%d%H%M%S)
        "
        sshpass -p "$VPS_PASS" scp -o StrictHostKeyChecking=no "$LOCAL_DIR/server.py" $VPS_USER@$VPS_HOST:/home/$VPS_USER/$VPS_DIR/server.py
        echo "  ✓ Local server.py uploaded (remote backup created)"
    else
        echo "  ⊘ No local server.py for $NAME — using the VPS copy as source"
    fi

    # Step 1: Sync package server.py with root server.py
    echo ""
    echo "Step 1/6: Syncing server.py to package directory..."
    sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "
        cd /home/$VPS_USER/$VPS_DIR
        cp server.py $PKG_DIR/server.py
    "
    echo "  ✓ Package server.py synced"

    # Step 2: Rebuild and restart Docker container
    echo ""
    echo "Step 2/6: Rebuilding Docker container..."
    sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "
        cd /home/$VPS_USER/$VPS_DIR
        docker compose down && docker compose up -d --build
    " 2>&1 | tail -5
    echo "  ✓ Container rebuilt and running on port $PORT"

    # Step 3: Health check
    echo ""
    echo "Step 3/6: Health check..."
    sleep 3
    STATUS=$(sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "
        curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:$PORT/mcp
    ")
    if [ "$STATUS" = "401" ] || [ "$STATUS" = "200" ]; then
        echo "  ✓ Server responding (HTTP $STATUS)"
    else
        echo "  ✗ Server NOT responding (HTTP $STATUS) — check logs!"
        sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "
            cd /home/$VPS_USER/$VPS_DIR
            docker compose logs 2>&1 | tail -15
        "
        return 1
    fi

    # Step 4: Bump version in pyproject.toml
    echo ""
    echo "Step 4/6: Bumping version..."
    CURRENT_VERSION=$(sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "
        cd /home/$VPS_USER/$VPS_DIR
        grep 'version' pyproject.toml | head -1 | sed 's/.*\"\(.*\)\"/\1/'
    ")
    echo "  Current version: $CURRENT_VERSION"
    read -p "  New version (or press Enter to skip PyPI): " NEW_VERSION

    if [ -n "$NEW_VERSION" ]; then
        sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "
            cd /home/$VPS_USER/$VPS_DIR
            sed -i 's/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/' pyproject.toml
        "
        echo "  ✓ Version bumped to $NEW_VERSION"

        # Step 5: Build and publish to PyPI
        echo ""
        echo "Step 5/6: Publishing to PyPI..."
        TMPDIR=$(mktemp -d)
        sshpass -p "$VPS_PASS" scp -o StrictHostKeyChecking=no -r $VPS_USER@$VPS_HOST:/home/$VPS_USER/$VPS_DIR/* "$TMPDIR/"
        sshpass -p "$VPS_PASS" scp -o StrictHostKeyChecking=no -r $VPS_USER@$VPS_HOST:/home/$VPS_USER/$VPS_DIR/$PKG_DIR "$TMPDIR/"
        cd "$TMPDIR"
        rm -rf dist/
        python3 -m build 2>&1 | tail -3
        twine upload -u __token__ -p "$PYPI_TOKEN" dist/* 2>&1 | tail -3
        echo "  ✓ Published to PyPI"
        rm -rf "$TMPDIR"
    else
        echo "  ⊘ Skipping PyPI publish"
    fi

    # Step 6: Push to GitHub
    echo ""
    echo "Step 6/6: Pushing to GitHub..."
    TMPDIR=$(mktemp -d)
    cd "$TMPDIR"
    git clone "https://github.com/$GITHUB_REPO.git" repo 2>&1 | tail -2
    cd repo
    sshpass -p "$VPS_PASS" scp -o StrictHostKeyChecking=no -r $VPS_USER@$VPS_HOST:/home/$VPS_USER/$VPS_DIR/* .
    sshpass -p "$VPS_PASS" scp -o StrictHostKeyChecking=no -r $VPS_USER@$VPS_HOST:/home/$VPS_USER/$VPS_DIR/$PKG_DIR .
    git add -A
    if git diff --cached --quiet; then
        echo "  ⊘ No changes to push"
    else
        git config user.email 'admin@divineapi.com'
        git config user.name 'Divine API'
        read -p "  Commit message: " COMMIT_MSG
        git commit -m "$COMMIT_MSG"
        git push origin main 2>&1 | tail -3
        echo "  ✓ Pushed to GitHub"
    fi
    rm -rf "$TMPDIR"

    echo ""
    echo "  ✅ $NAME deployed successfully!"
}

# The 6th argument is the local source dir. Indian Astrology lives in this
# repo ($SCRIPT_DIR); the other two are maintained in their own repos, so they
# pass "" and fall back to the VPS copy. Set their paths here if you clone them
# locally and want this script to upload your edits.
case $CHOICE in
    1)
        deploy_mcp "Indian Astrology" "indian-astrology" "divineapi_indian_astrology_mcp" "DivineAPI/mcp-indian-astrology" "8001" "$SCRIPT_DIR"
        ;;
    2)
        deploy_mcp "Western Astrology" "western-astrology" "divineapi_western_astrology_mcp" "DivineAPI/mcp-western-astrology-" "8002" ""
        ;;
    3)
        deploy_mcp "Horoscope & Numerology" "horoscope-numerology" "divineapi_horoscope_numerology_mcp" "DivineAPI/mcp-horoscope-numerology" "8003" ""
        ;;
    4)
        deploy_mcp "Indian Astrology" "indian-astrology" "divineapi_indian_astrology_mcp" "DivineAPI/mcp-indian-astrology" "8001" "$SCRIPT_DIR"
        deploy_mcp "Western Astrology" "western-astrology" "divineapi_western_astrology_mcp" "DivineAPI/mcp-western-astrology-" "8002" ""
        deploy_mcp "Horoscope & Numerology" "horoscope-numerology" "divineapi_horoscope_numerology_mcp" "DivineAPI/mcp-horoscope-numerology" "8003" ""
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "═══════════════════════════════════════════"
echo "  Deployment Complete!"
echo "═══════════════════════════════════════════"
echo ""
echo "  Checklist:"
echo "  ─────────"
echo "  ✓ 0. local server.py uploaded to VPS (remote backup kept)"
echo "  ✓ 1. server.py synced to package dir"
echo "  ✓ 2. Docker container rebuilt"
echo "  ✓ 3. Health check passed"
echo "  ✓ 4. Version bumped"
echo "  ✓ 5. Published to PyPI"
echo "  ✓ 6. Pushed to GitHub"
echo ""
echo "  Manual (if needed):"
echo "  ───────────────────"
echo "  • Update Smithery description at smithery.ai"
echo "  • Update docs page at developers.divineapi.com/mcp"
echo ""
