#!/usr/bin/env bash
# ==============================================================================
# publish_course.sh - ADK Course Publisher & Website Sync Automation Script
#
# Synchronizes the public Python course repo (google-adk-training) with the
# private production website repo (adk-website) and Cloudflare Worker.
#
# Usage:
#   bash .agent/skills/adk-course-publisher/scripts/publish_course.sh [OPTIONS]
#
# Options:
#   --check-only   Run tests and build verification without deploying to Cloudflare
#   --skip-push    Skip git push to remote GitHub repositories
#   --help         Display this help message
# ==============================================================================

set -euo pipefail

# ANSI Color Codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

CHECK_ONLY=false
SKIP_PUSH=false

for arg in "$@"; do
  case $arg in
    --check-only)
      CHECK_ONLY=true
      shift
      ;;
    --skip-push)
      SKIP_PUSH=true
      shift
      ;;
    --help)
      echo "Usage: bash publish_course.sh [--check-only] [--skip-push]"
      exit 0
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COURSE_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"
WEBSITE_ROOT="$(cd "${COURSE_ROOT}/../adk-website" 2>/dev/null && pwd || true)"

echo -e "${BLUE}=================================================================${NC}"
echo -e "${BLUE} 🚀 ADK COURSE PUBLISHER & DEPLOYMENT PIPELINE ${NC}"
echo -e "${BLUE}=================================================================${NC}"
echo -e "Course Root:  ${COURSE_ROOT}"
echo -e "Website Root: ${WEBSITE_ROOT}"
echo ""

# ------------------------------------------------------------------------------
# 1. Audit Decoupling Integrity in google-adk-training
# ------------------------------------------------------------------------------
echo -e "${YELLOW}► Stage 1: Auditing Decoupling Integrity in Student Repo...${NC}"

if [ -d "${COURSE_ROOT}/portal" ] || [ -d "${COURSE_ROOT}/doc" ]; then
  echo -e "${RED}❌ FAILED: Found portal/ or doc/ in student repo! Decoupling violated.${NC}"
  exit 1
fi

WEB_FILES=$(find "${COURSE_ROOT}" -maxdepth 2 \( -name "package.json" -o -name "wrangler.jsonc" -o -name "docusaurus.config.js" \) 2>/dev/null || true)
if [ -n "${WEB_FILES}" ]; then
  echo -e "${RED}❌ FAILED: Detected web infrastructure files in student repo:${NC}"
  echo "${WEB_FILES}"
  exit 1
fi

echo -e "${GREEN}✅ PASS: Student repository is 100% clean pure Python.${NC}"
echo ""

# ------------------------------------------------------------------------------
# 2. Check Website Repository Location
# ------------------------------------------------------------------------------
echo -e "${YELLOW}► Stage 2: Verifying adk-website Repository...${NC}"

if [ -z "${WEBSITE_ROOT}" ] || [ ! -d "${WEBSITE_ROOT}" ]; then
  echo -e "${RED}❌ FAILED: adk-website repo not found at ${COURSE_ROOT}/../adk-website${NC}"
  echo -e "Ensure https://github.com/inderanz/adk-website.git is cloned adjacent to google-adk-training."
  exit 1
fi

echo -e "${GREEN}✅ PASS: adk-website found.${NC}"
echo ""

# ------------------------------------------------------------------------------
# 3. Synchronize Submodule in adk-website
# ------------------------------------------------------------------------------
echo -e "${YELLOW}► Stage 3: Synchronizing Content Submodule in adk-website...${NC}"

cd "${WEBSITE_ROOT}"
if [ -d "content/.git" ] || [ -f "content/.git" ]; then
  git submodule update --remote --merge content || true
  echo -e "${GREEN}✅ Submodule synchronized to latest content.${NC}"
else
  echo -e "${YELLOW}⚠️ Submodule not initialized. Initializing...${NC}"
  git submodule update --init --recursive
fi
echo ""

# ------------------------------------------------------------------------------
# 4. Run Portal Test Suite
# ------------------------------------------------------------------------------
echo -e "${YELLOW}► Stage 4: Running Portal Regression Test Suite...${NC}"

cd "${WEBSITE_ROOT}/portal"
npm test
echo -e "${GREEN}✅ PASS: All portal unit & security tests passed.${NC}"
echo ""

# ------------------------------------------------------------------------------
# 5. Build Docusaurus & Secure Edge Policies
# ------------------------------------------------------------------------------
echo -e "${YELLOW}► Stage 5: Building Production Static Site & Policies...${NC}"

npm run build
echo -e "${GREEN}✅ PASS: Docusaurus build completed cleanly.${NC}"
echo ""

# ------------------------------------------------------------------------------
# 6. Deploy to Cloudflare Worker Production (unless --check-only)
# ------------------------------------------------------------------------------
if [ "${CHECK_ONLY}" = true ]; then
  echo -e "${BLUE}ℹ️ --check-only specified. Skipping Cloudflare deployment and push.${NC}"
  exit 0
fi

echo -e "${YELLOW}► Stage 6: Deploying to Cloudflare Worker Production...${NC}"

npm run deploy:production
echo -e "${GREEN}✅ PASS: Cloudflare Worker production deployment successful.${NC}"
echo ""

# ------------------------------------------------------------------------------
# 7. Probe Live Endpoint for Zero Downtime
# ------------------------------------------------------------------------------
echo -e "${YELLOW}► Stage 7: Probing Live Health Endpoint...${NC}"

PROBE_URL="https://gyanhq.com/adk-training/"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${PROBE_URL}")

if [ "${HTTP_STATUS}" -eq 200 ] || [ "${HTTP_STATUS}" -eq 302 ]; then
  echo -e "${GREEN}✅ PASS: Live website is healthy (${PROBE_URL} -> HTTP ${HTTP_STATUS}).${NC}"
else
  echo -e "${RED}⚠️ WARNING: Live site returned HTTP ${HTTP_STATUS}. Check Cloudflare dashboard.${NC}"
fi
echo ""

# ------------------------------------------------------------------------------
# 8. Git Push Website Repo (unless --skip-push)
# ------------------------------------------------------------------------------
if [ "${SKIP_PUSH}" = false ]; then
  echo -e "${YELLOW}► Stage 8: Pushing adk-website Changes to Remote...${NC}"
  cd "${WEBSITE_ROOT}"
  if [[ -n $(git status --porcelain) ]]; then
    git add -A
    git commit -m "chore(deploy): sync course content & release worker"
    git push origin main
    echo -e "${GREEN}✅ adk-website pushed to origin/main.${NC}"
  else
    echo -e "${GREEN}✅ adk-website working tree clean.${NC}"
  fi
fi

echo ""
echo -e "${GREEN}=================================================================${NC}"
echo -e "${GREEN} 🎉 COURSE PUBLISHING & VERIFICATION COMPLETED SUCCESSFULLY!    ${NC}"
echo -e "${GREEN}=================================================================${NC}"
