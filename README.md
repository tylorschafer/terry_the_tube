# Terry the Tube 🍺

Terry the Tube is an AI-powered beer dispensing system that combines speech recognition, text-to-speech, and conversational AI. The system acts as a sarcastic beer-dispensing tube that interacts with users through voice, requires them to answer questions before dispensing beer, and uses advanced TTS for natural-sounding speech synthesis.

## Features

- **Sarcastic AI Personality**: Bill Burr-style humor and attitude
- **Voice Interaction**: Speech-to-text input and text-to-speech responses
- **Question-Based Beer Dispensing**: Users must answer 3 questions correctly
- **Dual Interface**: Both terminal and web modes available
- **High-Quality Audio**: Advanced TTS with multiple model support
- **Real-time Processing**: Live audio transcription and response generation

## Interface Modes

### Web Interface (Default)
The web interface provides a modern, user-friendly experience with:
- Real-time chat interface with Terry
- "Hold to Talk" button for voice input
- Visual status indicators
- Responsive design for desktop and mobile

### Terminal Mode
The terminal mode offers a classic command-line experience with:
- Direct terminal output with colored text
- Spacebar-triggered voice recording
- Real-time processing feedback
- Session logging and timestamps

## Installation

#### Prerequisites
- [Download and install Ollama locally](https://ollama.com/download)
- Once Ollama is installed, run: `ollama run gemma3:4b-it-q8_0`
- Python 3.9.4 or higher
- macOS system with `afplay`, `say`, and `rec` commands

#### Setup
1. Clone this repository and navigate to the directory
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application:
   ```bash
   python main.py                    # Web interface (default)
   python main.py --mode terminal    # Terminal mode
   python main.py --info             # Show system information
   ```

## How It Works

1. **Voice Input**: Users press and hold spacebar (terminal) or the talk button (web) to record
2. **Speech Recognition**: OpenAI Whisper transcribes audio to text
3. **AI Response**: Ollama generates personality-appropriate responses
4. **Text-to-Speech**: TTS library synthesizes natural-sounding audio responses
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
- **AI Model**: Change `OLLAMA_MODEL` to use different models
- **TTS Models**: Modify `TTS_MODELS_TO_TRY` for different voice options  
- **Personality**: Adjust the AI prompt for different personalities
- **Audio Settings**: Configure recording and playback parameters

## Architecture

- **main.py**: Clean entry point with command-line interface
- **config.py**: Centralized configuration constants
- **src/terry_app.py**: Main application orchestrator
- **src/core/**: Core business logic (AI handler, conversation manager)
- **src/audio/**: Audio processing modules (TTS, STT, recording)
- **src/web/**: Web interface components
- **src/utils/**: Utilities like file cleanup
