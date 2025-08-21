"""
Modular HTML Templates for Terry the Tube Web Interface
Refactored to use separate files for better maintainability
"""

import os
from pathlib import Path


def get_file_content(filename):
    """Get content from a file in the web directory or dist directory"""
    web_dir = Path(__file__).parent
    
    # Try compiled TypeScript first (dist directory)
    if filename.endswith('.js') and not filename.startswith('dist/'):
        dist_path = web_dir / 'dist' / filename
        if dist_path.exists():
            with open(dist_path, 'r', encoding='utf-8') as f:
                return f.read()
    
    # Fall back to direct file path
    file_path = web_dir / filename
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        print(f"Warning: {filename} not found in web directory")
        return ""


def get_main_html_template(text_only_mode=False):
    """Get the main HTML template with optional text-only mode"""
    
    # Load all the separate files
    styles_css = get_file_content('styles.css')
    state_manager_js = get_file_content('state-manager.js')
    ui_controller_js = get_file_content('ui-controller.js')
    polling_manager_js = get_file_content('polling-manager.js')
    app_controller_js = get_file_content('app-controller.js')
    main_template = get_file_content('main-template.html')
    
    # Conditionally include recording elements
    recording_indicator_html = ""
    talk_button_html = ""
    
    if not text_only_mode:
        talk_button_html = '''
            <button class="talk-button" id="talkButton" 
                    onmousedown="startRecording()" 
                    onmouseup="stopRecording()"
                    ontouchstart="startRecording()" 
                    ontouchend="stopRecording()">
                <i class="fas fa-microphone"></i>
                <span>Hold to Talk</span>
            </button>
        '''
        
        recording_indicator_html = '''
        <div class="recording-indicator" id="recordingIndicator">
            <div class="recording-dot"></div>
            <span>Recording...</span>
        </div>
        '''
    
    # Replace placeholders with actual content
    template = main_template.replace('{STYLES_PLACEHOLDER}', styles_css)
    template = template.replace('{STATE_MANAGER_JS}', state_manager_js)
    template = template.replace('{UI_CONTROLLER_JS}', ui_controller_js)
    template = template.replace('{WEBSOCKET_MANAGER_JS}', polling_manager_js)
    template = template.replace('{APP_CONTROLLER_JS}', app_controller_js)
    template = template.replace('{RECORDING_INDICATOR_HTML}', recording_indicator_html)
    template = template.replace('{TALK_BUTTON_HTML}', talk_button_html)
    
    return template