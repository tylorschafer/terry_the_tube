#!/usr/bin/env python3
"""
Build script for Terry the Tube TypeScript web interface
Compiles TypeScript files to JavaScript before starting the server
"""

import subprocess
import sys
import os
from pathlib import Path

def build_typescript():
    """Compile TypeScript files to JavaScript"""
    print("🔨 Building TypeScript web interface...")
    
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    try:
        # Check if npm and typescript are available
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ npm not found. Please install Node.js")
            return False
            
        # Install dependencies if needed
        if not (project_root / 'node_modules').exists():
            print("📦 Installing TypeScript dependencies...")
            result = subprocess.run(['npm', 'install'], check=True)
        
        # Compile TypeScript
        print("🔄 Compiling TypeScript...")
        result = subprocess.run(['npm', 'run', 'build'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ TypeScript compilation successful!")
            return True
        else:
            print("❌ TypeScript compilation failed:")
            print(result.stderr)
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js and npm")
        return False

if __name__ == "__main__":
    success = build_typescript()
    sys.exit(0 if success else 1)