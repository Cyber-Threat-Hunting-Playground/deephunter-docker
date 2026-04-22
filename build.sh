#!/bin/bash
# Enhanced build script with versioning and optimization

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Load .env if present (provides GITHUB_REPO, DEEPHUNTER_VERSION, etc.)
if [ -f .env ]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
fi

# Configuration
IMAGE_NAME="deephunter"
VERSION="${VERSION:-latest}"
GITHUB_REPO="${GITHUB_REPO:-cyber-threat-hunting-playground/deephunter}"
DEEPHUNTER_VERSION="${DEEPHUNTER_VERSION:-2.5}"
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

echo -e "${BLUE}==================================="
echo "DeepHunter Docker Build Script"
echo -e "===================================${NC}"
echo ""
echo "Image: ${IMAGE_NAME}:${VERSION}"
echo "Repo:  ${GITHUB_REPO} @ v${DEEPHUNTER_VERSION}"
echo "Build Date: ${BUILD_DATE}"
echo "VCS Ref: ${VCS_REF}"
echo ""

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Bundle source on the host so the image build does not need GitHub (proxies/firewalls often block container egress).
DEEPHUNTER_TARBALL="resources/v${DEEPHUNTER_VERSION}.tar.gz"
DEEPHUNTER_URL="https://github.com/${GITHUB_REPO}/archive/refs/tags/v${DEEPHUNTER_VERSION}.tar.gz"
LOCAL_DEEPHUNTER_DIR="../deephunter"
mkdir -p resources

if [ -d "${LOCAL_DEEPHUNTER_DIR}" ]; then
    echo -e "${BLUE}Local deephunter repo found at ${LOCAL_DEEPHUNTER_DIR} — bundling fresh tarball...${NC}"
    tar czf "${DEEPHUNTER_TARBALL}" -C "$(dirname "${LOCAL_DEEPHUNTER_DIR}")" "$(basename "${LOCAL_DEEPHUNTER_DIR}")"
    echo -e "${GREEN}Source bundled from local repo into ${DEEPHUNTER_TARBALL}${NC}"
elif [ ! -f "${DEEPHUNTER_TARBALL}" ]; then
    echo -e "${YELLOW}${DEEPHUNTER_TARBALL} not found — downloading on host...${NC}"
    if command -v curl &> /dev/null; then
        curl -fL -o "${DEEPHUNTER_TARBALL}" "${DEEPHUNTER_URL}"
    elif command -v wget &> /dev/null; then
        wget -O "${DEEPHUNTER_TARBALL}" "${DEEPHUNTER_URL}"
    else
        echo -e "${RED}Need curl or wget to fetch DeepHunter source, or place ${DEEPHUNTER_TARBALL} manually.${NC}"
        echo "  make download-deephunter"
        exit 1
    fi
    echo -e "${GREEN}Source saved to ${DEEPHUNTER_TARBALL}${NC}"
fi

# Build the image
echo -e "${BLUE}Building Docker image...${NC}"
if docker build \
    --build-arg GITHUB_REPO="${GITHUB_REPO}" \
    --build-arg DEEPHUNTER_VERSION="${DEEPHUNTER_VERSION}" \
    --build-arg BUILD_DATE="${BUILD_DATE}" \
    --build-arg VCS_REF="${VCS_REF}" \
    --tag "${IMAGE_NAME}:${VERSION}" \
    --tag "${IMAGE_NAME}:${DEEPHUNTER_VERSION}" \
    ./; then
    echo ""
    echo -e "${GREEN}==================================="
    echo "Build completed successfully!"
    echo -e "===================================${NC}"
    echo ""
    echo "Images created:"
    docker images | grep "${IMAGE_NAME}" | head -n 2
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Configure .env file: cp .env.example .env"
    echo "2. Start services: make up"
    echo "3. Initialize application: make init"
    echo ""
else
    echo -e "${RED}Build failed!${NC}"
    exit 1
fi
