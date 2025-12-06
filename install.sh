#!/bin/bash
# forkstack installer
# Usage: curl -LsSf https://forkstack.xyz/install.sh | sh

set -e

REPO="russellromney/forkstack"
INSTALL_DIR="${FORKS_INSTALL_DIR:-$HOME/.forkstack}"
BIN_DIR="${FORKS_BIN_DIR:-$INSTALL_DIR/bin}"

# Detect platform
detect_platform() {
    local os arch

    os="$(uname -s)"
    arch="$(uname -m)"

    case "$os" in
        Linux)  os="linux" ;;
        Darwin) os="macos" ;;
        *)      echo "Unsupported OS: $os" && exit 1 ;;
    esac

    case "$arch" in
        x86_64)  arch="x86_64" ;;
        aarch64) arch="aarch64" ;;
        arm64)   arch="aarch64" ;;
        *)       echo "Unsupported architecture: $arch" && exit 1 ;;
    esac

    echo "${os}-${arch}"
}

# Get latest release version
get_latest_version() {
    curl -sL "https://api.github.com/repos/${REPO}/releases/latest" | \
        grep '"tag_name":' | \
        sed -E 's/.*"([^"]+)".*/\1/'
}

main() {
    echo "Installing forkstack..."

    local platform version download_url archive

    platform="$(detect_platform)"
    version="$(get_latest_version)"

    if [ -z "$version" ]; then
        echo "Could not determine latest version. Using 'latest'."
        version="latest"
    fi

    echo "  Platform: $platform"
    echo "  Version:  $version"

    # Create directories
    mkdir -p "$BIN_DIR"

    # Download binary
    archive="forks-${platform}.tar.gz"
    download_url="https://github.com/${REPO}/releases/download/${version}/${archive}"

    echo "  Downloading from: $download_url"

    curl -LsSf "$download_url" | tar xz -C "$BIN_DIR"

    # Make executable
    chmod +x "$BIN_DIR/forks"

    echo ""
    echo "forkstack installed to: $BIN_DIR/forks"
    echo ""

    # Check if bin dir is in PATH
    case ":$PATH:" in
        *":$BIN_DIR:"*)
            echo "Run 'fks --help' to get started!"
            ;;
        *)
            echo "Add the following to your shell config (.bashrc, .zshrc, etc.):"
            echo ""
            echo "  export PATH=\"$BIN_DIR:\$PATH\""
            echo ""
            echo "Then run 'fks --help' to get started!"
            ;;
    esac
}

main
