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
from src.utils.display import display
from src.personalities import get_personality_names


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Terry the Tube - AI Beer Dispenser',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                    # Run with web interface (default)
  python main.py --mode web                         # Run with web interface  
  python main.py --mode terminal                    # Run in terminal-only mode
  python main.py --personality sarcastic_comedian  # Use specific personality
  python main.py --mode terminal --personality passive_aggressive_librarian
  python main.py --info                            # Show system information
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
    
    # Get available personalities for help text
    personalities = get_personality_names()
    personality_choices = [key for key, _ in personalities]
    personality_help = 'Personality type: ' + ', '.join([f'{key} ({name})' for key, name in personalities])
    
    parser.add_argument(
        '--personality', 
        choices=personality_choices,
        help=personality_help
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize the application
        app = TerryTubeApp(use_web_gui=(args.mode == 'web'), personality_key=args.personality)
        
        if args.info:
            # Show system information
            info = app.get_system_info()
            display.header("System Information")
            
            system_info = {
                "Web Mode": {"available": True, "value": info['web_mode']},
                "AI Available": {"available": info['ai_available'], "value": info['ai_available']},
                "Personality": {"available": bool(info['personality']), "value": info['personality']['name'] if info['personality'] else None},
                "TTS Model": {"available": info['audio']['tts_available'], "value": info['audio']['tts_model']},
                "STT Model": {"available": info['audio']['stt_available'], "value": info['audio']['stt_model']['model']}
            }
            
            display.system_info(system_info)
            return
        
        # Run the application
        if args.mode == 'terminal':
            app.run_terminal_mode()
        else:
            app.run_web_mode()
            
    except KeyboardInterrupt:
        display.warning("\nShutting down Terry the Tube...")
    except Exception as e:
        display.error(f"Fatal error: {e}")
        display.error("Please check that all dependencies are installed and Ollama is running.")
        sys.exit(1)


if __name__ == "__main__":
    main()