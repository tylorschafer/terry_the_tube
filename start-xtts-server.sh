#!/bin/bash
# XTTS API Server for ARM64 Mac
# Installs Python 3.10 for compatibility with xtts-api-server

echo "🍎 Setting up XTTS API Server for Apple Silicon..."

# Check if Python 3.10 is available
if command -v python3.10 &> /dev/null; then
    echo "✅ Python 3.10 found"
    PYTHON_CMD="python3.10"
elif [[ -f "/opt/homebrew/bin/python3.10" ]]; then
    echo "✅ Homebrew Python 3.10 found"
    PYTHON_CMD="/opt/homebrew/bin/python3.10"
else
    echo "❌ Python 3.10 not found. Installing via Homebrew..."
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "📦 Installing Homebrew first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH for current session
        if [[ -f "/opt/homebrew/bin/brew" ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
    fi
    
    echo "🐍 Installing Python 3.10..."
    brew install python@3.10
    
    # Set Python command
    PYTHON_CMD="/opt/homebrew/bin/python3.10"
fi

echo "🐍 Using Python: $($PYTHON_CMD --version)"

# Clean up any problematic existing environment
if [[ -d "xtts_server_env" ]]; then
    echo "🧹 Removing existing environment to fix compatibility issues..."
    rm -rf xtts_server_env
fi

# Create fresh environment with Python 3.10
echo "🔄 Creating fresh virtual environment with Python 3.10..."
$PYTHON_CMD -m venv xtts_server_env

# Activate and install
source xtts_server_env/bin/activate

# Set environment variables to fix encoding issues
export PYTHONIOENCODING=utf-8
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

echo "📦 Installing XTTS API server with compatible versions..."

# Upgrade pip first
pip install --upgrade pip

# Install PyTorch for Apple Silicon
echo "🧠 Installing PyTorch for Apple Silicon..."
pip install --no-cache-dir torch torchvision torchaudio

# Install XTTS API server with environment fixes
echo "🎙️ Installing XTTS API server..."
PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir xtts-api-server

# Create voice clones directory
mkdir -p voice_clones

echo ""
echo "🎉 Installation complete!"
echo "🎙️ Starting XTTS API Server on port 8020..."
echo "🔗 Available at: http://localhost:8020"
echo "📁 Voice clones: $(pwd)/voice_clones"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Start server using full path to avoid PATH issues
if [[ -f "xtts_server_env/bin/xtts-api-server" ]]; then
    ./xtts_server_env/bin/xtts-api-server --port 8020 --device cpu
elif command -v xtts-api-server &> /dev/null; then
    xtts-api-server --port 8020 --device cpu
else
    echo "❌ xtts-api-server not found. Let's debug this..."
    echo "🔍 Checking installation..."
    pip show xtts-api-server
    echo "🔍 Looking for executable..."
    find xtts_server_env -name "*xtts*" -type f 2>/dev/null
    echo "🔍 Trying python -m approach..."
    python -m xtts_api_server --port 8020 --device cpu
fi