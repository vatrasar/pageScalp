#!/usr/bin/env bash
set -e

# PageScalp Installation Script
# Installs PageScalp to ~/.local/share/pageScalp and creates a launcher in ~/.local/bin/pagescalp

APP_NAME="pageScalp"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
BIN_DIR="$HOME/.local/bin"
WRAPPER_SCRIPT="$BIN_DIR/pagescalp"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "   Installing PageScalp for Linux CLI     "
echo "=========================================="

echo "[1/4] Creating application directory at $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

echo "[2/4] Copying application files..."
cp -rf "$SCRIPT_DIR/Src" "$INSTALL_DIR/"
cp -f "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"

echo "[3/4] Creating dedicated virtual environment and installing dependencies..."
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip --quiet
"$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt" --quiet

echo "[4/4] Creating command wrapper at $WRAPPER_SCRIPT..."
cat << 'EOF' > "$WRAPPER_SCRIPT"
#!/usr/bin/env bash
APP_DIR="$HOME/.local/share/pageScalp"
PYTHONPATH="$APP_DIR" "$APP_DIR/venv/bin/python3" "$APP_DIR/Src/main.py" "$@"
EOF

chmod +x "$WRAPPER_SCRIPT"

echo "=========================================="
echo "✔ Installation complete!"
echo "You can now run 'pagescalp' directly from your terminal."
echo ""
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "Notice: $HOME/.local/bin is not currently in your PATH."
    echo "To access 'pagescalp' globally, add this to your ~/.bashrc or ~/.zshrc:"
    echo '  export PATH="$HOME/.local/bin:$PATH"'
fi
echo "=========================================="
