# Terry the Tube 🍺

Terry the Tube is an AI-powered beer dispensing system that combines speech recognition, text-to-speech, and conversational AI. The system acts as a sarcastic beer-dispensing tube that interacts with users through voice, requires them to answer questions before dispensing beer, and uses advanced TTS for natural-sounding speech synthesis.

## Features

- **Multiple AI Personalities**: Choose from 'Sarcastic Comedian' to 'Passive Aggressive Librarian'
- **Voice Interaction**: Speech-to-text input and text-to-speech responses
- **Question-Based Beer Dispensing**: Users must answer 3 questions
- **Dual Interface**: Both terminal and web modes available
- **High-Quality Audio**: Advanced TTS with multiple model support
- **Real-time Processing**: Live audio transcription and response generation
- **Modern Frontend**: TypeScript-based web interface with reactive state management

## Interface Modes

### Web Interface (Default)
The web interface provides a modern, user-friendly experience with:
- Real-time chat interface with Terry powered by WebSockets
- "Hold to Talk" button for voice input
- Visual status indicators and loading states
- Responsive design for desktop and mobile
- Modern TypeScript architecture with reactive state management

### Terminal Mode
The terminal mode offers a classic command-line experience with:
- Direct terminal output with colored text
- Spacebar-triggered voice recording
- Real-time processing feedback
- Session logging and timestamps

## Installation

#### Prerequisites
- **OpenAI API Key** set as `OPENAI_API_KEY` environment variable (for TTS and Chat)
- [Download and install Ollama locally](https://ollama.com/download) for fallback AI
- Once Ollama is installed, run: `ollama run mistral-small:24b`
- Python 3.9.4 or higher
- macOS system with `afplay`, `say`, and `rec` commands

#### Setup
1. Clone this repository and navigate to the directory
2. Install dependencies:
   ```bash
   pip install openai>=1.0.0
   pip install langchain-ollama langchain-core
   pip install openai-whisper
   pip install keyboard
   pip install requests
   pip install python-dotenv
   pip install websockets
   ```
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
4. Run the application:
   ```bash
   python main.py                    # Web interface (default)
   python main.py --mode terminal    # Terminal mode
   python main.py --info             # Show system information
   ```

## How It Works

1. **Voice Input**: Users press and hold spacebar (terminal) or the talk button (web) to record
2. **Speech Recognition**: OpenAI Whisper transcribes audio to text
3. **AI Response**: OpenAI GPT-4.1-mini (primary) or Ollama (fallback) generates personality-appropriate responses
4. **Text-to-Speech**: OpenAI TTS API synthesizes natural-sounding audio responses with personality-specific voice instructions
5. **Beer Dispensing**: After answering 3 questions correctly, Terry dispenses beer with "BEER HERE!"

## Screenshots

### Web Interface
The modern web interface provides an intuitive chat experience with Terry:

![Web Interface](https://github.com/user-attachments/assets/terry-web-interface.png)

*Features: Real-time chat, hold-to-talk button, status indicators, and responsive design*

### Terminal Mode
The classic terminal interface shows detailed processing information:

![Terminal Interface](https://github.com/user-attachments/assets/terry-terminal-interface.png)

*Features: Colored output, session tracking, real-time processing feedback, and spacebar recording*

## Usage Examples

### Web Mode (Default)
```bash
python main.py
```
- Visit `http://localhost:8080` in your browser
- Click and hold "HOLD TO TALK" button
- Speak your response to Terry's questions
- Release button when finished speaking

### Terminal Mode
```bash
python main.py --mode terminal
```
- Press and hold spacebar to record your voice
- Release spacebar when finished speaking
- Watch real-time transcription and Terry's responses
- Answer 3 questions to get your beer!

### System Information
```bash
python main.py --info
```
- View current configuration
- Check model availability
- Verify system dependencies

## Configuration

The system is easily configurable via `config.py`:
- **AI Model**: Toggle between OpenAI GPT-4.1-mini and Ollama models
- **TTS Voice**: Choose from 6 OpenAI voices with personality-specific settings
- **Personality**: Three distinct personalities with unique voice instructions
- **Audio Settings**: Configure recording and playback parameters
- **API Settings**: Configure OpenAI API usage and fallback behavior

## Architecture

- **main.py**: Clean entry point with command-line interface
- **config.py**: Centralized configuration constants
- **src/terry_app.py**: Main application orchestrator
- **src/core/**: Core business logic (AI handler, conversation manager)
- **src/audio/**: Audio processing modules (TTS, STT, recording)
- **src/web/**: Modern TypeScript-based web interface with comprehensive documentation
- **src/utils/**: Utilities like file cleanup

## Documentation

For detailed technical information:
- **[Frontend Architecture](src/web/README.md)**: Comprehensive guide to the TypeScript-based web interface, including component structure, state management, and WebSocket communication
- **[Development Guide](CLAUDE.md)**: Technical documentation for developers and AI assistants working with the codebase
