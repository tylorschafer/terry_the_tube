# Terry the Tube - Refactored Structure

## Project Structure

The project has been completely refactored and organized into a clean, modular structure:

```
terry_the_tube/
├── main_new.py              # New main entry point
├── config.py                # Centralized configuration constants
├── src/                     # Source code modules
│   ├── __init__.py
│   ├── terry_app.py         # Main application orchestrator
│   ├── core/                # Core business logic
│   │   ├── __init__.py
│   │   ├── ai_handler.py    # AI/LLM interface
│   │   └── conversation_manager.py  # Conversation flow management
│   ├── audio/               # Audio processing modules
│   │   ├── __init__.py
│   │   ├── audio_manager.py # Audio orchestrator
│   │   ├── tts_handler.py   # Text-to-speech handler
│   │   ├── stt_handler.py   # Speech-to-text handler
│   │   └── recording_handler.py  # Audio recording handler
│   ├── web/                 # Web interface modules
│   │   ├── __init__.py
│   │   ├── web_interface.py # Web interface logic
│   │   ├── web_server.py    # HTTP server
│   │   └── web_templates.py # HTML templates
│   └── utils/               # Utility modules
│       ├── __init__.py
│       └── cleanup.py       # File cleanup utilities
└── [old files...]           # Legacy files (to be replaced)
```

## Key Improvements

### 1. **Centralized Configuration** (`config.py`)
- All constants and settings in one place
- Easy to swap models (Ollama model, TTS models, etc.)
- Environment-specific configurations
- Consistent naming conventions

### 2. **Modular Architecture**
- **Core**: Business logic separated from implementation details
- **Audio**: All audio processing in dedicated modules
- **Web**: Web interface completely isolated
- **Utils**: Shared utilities and helpers

### 3. **Clean Separation of Concerns**
- `AIHandler`: Manages LLM interactions
- `ConversationManager`: Handles conversation flow and state
- `AudioManager`: Orchestrates all audio operations
- `TerryTubeApp`: Main application coordinator

### 4. **Improved Error Handling**
- Consistent error messages from config
- Better fallback mechanisms
- Graceful degradation when components fail

### 5. **Enhanced Maintainability**
- Single responsibility principle
- Clear interfaces between modules
- Easy to test individual components
- Simple to extend or modify features

## Usage

### Running the Application

```bash
# Web interface mode (default)
python main_new.py

# Terminal mode
python main_new.py --mode terminal

# Show system information
python main_new.py --info
```

### Key Configuration Changes

Easy model swapping in `config.py`:
```python
# Change Ollama model
OLLAMA_MODEL = "gemma3:4b-it-q8_0"  # or "llama2", "mistral", etc.

# Try different TTS models
TTS_MODELS_TO_TRY = [
    "tts_models/en/vctk/vits",
    "tts_models/en/ljspeech/fast_pitch",
    # Add more models here
]
```

## Migration Notes

1. **Old files preserved**: All original files remain unchanged
2. **New entry point**: Use `main_new.py` instead of `main.py`
3. **Same functionality**: All features work identically
4. **Enhanced debugging**: Better error messages and system info

## Next Steps

1. Test the refactored code
2. Replace old files with new structure
3. Update documentation
4. Add unit tests for individual modules

This refactored structure makes Terry the Tube much more maintainable, testable, and extensible!