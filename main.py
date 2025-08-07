#!/usr/bin/env python3
"""
Terry the Tube - AI-powered Beer Dispensing System
Main entry point for the application

A sarcastic beer-dispensing tube that interacts with users through voice,
requires them to answer questions before dispensing beer, and uses 
advanced TTS and STT capabilities.
"""
import sys
import argparse
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.terry_app import TerryTubeApp


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Terry the Tube - AI Beer Dispenser',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run with web interface (default)
  python main.py --mode web         # Run with web interface  
  python main.py --mode terminal    # Run in terminal-only mode
  python main.py --info             # Show system information
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['web', 'terminal'], 
        default='web',
        help='Interface mode: web (GUI) or terminal (default: web)'
    )
    
    parser.add_argument(
        '--info', 
        action='store_true',
        help='Show system information and exit'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize the application
        app = TerryTubeApp(use_web_gui=(args.mode == 'web'))
        
        if args.info:
            # Show system information
            info = app.get_system_info()
            print("\n" + "="*50)
            print("TERRY THE TUBE - SYSTEM INFORMATION")
            print("="*50)
            print(f"Web Mode: {info['web_mode']}")
            print(f"AI Available: {info['ai_available']}")
            print(f"TTS Model: {info['audio']['tts_model']}")
            print(f"TTS Available: {info['audio']['tts_available']}")
            print(f"STT Model: {info['audio']['stt_model']['model']}")
            print(f"STT Available: {info['audio']['stt_available']}")
            print("="*50 + "\n")
            return
        
        # Run the application
        if args.mode == 'terminal':
            app.run_terminal_mode()
        else:
            app.run_web_mode()
            
    except KeyboardInterrupt:
        print("\nShutting down Terry the Tube...")
    except Exception as e:
        print(f"Fatal error: {e}")
        print("Please check that all dependencies are installed and Ollama is running.")
        sys.exit(1)


if __name__ == "__main__":
    main()