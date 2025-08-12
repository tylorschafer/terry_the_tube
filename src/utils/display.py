import time
from datetime import datetime
from typing import Optional

class TerryDisplay:
  # Colors and styles
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Colors
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'
    
    # Background colors for highlights
    BG_BLUE = '\033[44m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_RED = '\033[41m'
    
    def __init__(self):
        self.session_id = None
        self.start_time = time.time()
    
    def set_session_id(self, session_id: str):
        self.session_id = session_id
    
    def _get_timestamp(self) -> str:
        return datetime.now().strftime("%H:%M")
    
    def _get_elapsed(self) -> str:
        elapsed = time.time() - self.start_time
        if elapsed < 60:
            return f"{elapsed:.1f}s"
        else:
            minutes = int(elapsed // 60)
            seconds = elapsed % 60
            return f"{minutes}m {seconds:.1f}s"
    
    def header(self, title: str):
        print(f"\n{self.BOLD}{self.BLUE}{'=' * 60}{self.RESET}")
        print(f"{self.BOLD}{self.BLUE}  🍺 {title.upper()} 🍺{self.RESET}")
        print(f"{self.BOLD}{self.BLUE}{'=' * 60}{self.RESET}")
        print(f"{self.DIM}  Started at {self._get_timestamp()}{self.RESET}\n")
    
    def section(self, title: str):
        print(f"\n{self.BOLD}{self.CYAN}▶ {title}{self.RESET}")
        print(f"{self.GRAY}{'─' * (len(title) + 2)}{self.RESET}")
    
    def info(self, message: str, prefix: str = "ℹ"):
        timestamp = self._get_timestamp()
        print(f"{self.GRAY}[{timestamp}]{self.RESET} {self.BLUE}{prefix}{self.RESET} {message}")
    
    def success(self, message: str, prefix: str = "✓"):
        timestamp = self._get_timestamp()
        print(f"{self.GRAY}[{timestamp}]{self.RESET} {self.GREEN}{prefix}{self.RESET} {message}")
    
    def warning(self, message: str, prefix: str = "⚠"):
        timestamp = self._get_timestamp()
        print(f"{self.GRAY}[{timestamp}]{self.RESET} {self.YELLOW}{prefix}{self.RESET} {message}")
    
    def error(self, message: str, prefix: str = "✗"):
        timestamp = self._get_timestamp()
        print(f"{self.GRAY}[{timestamp}]{self.RESET} {self.RED}{prefix}{self.RESET} {message}")
    
    def session_start(self, session_id: str):
        self.session_id = session_id
        print(f"\n{self.BG_GREEN}{self.WHITE} SESSION STARTED {self.RESET}")
        print(f"{self.GRAY}Session ID:{self.RESET} {self.BOLD}{session_id}{self.RESET}")
        print(f"{self.GRAY}Time:{self.RESET} {self._get_timestamp()}")
        print(f"{self.GRAY}{'─' * 50}{self.RESET}")
    
    def conversation_question(self, question_num: int, total: int = 3):
        progress = "●" * question_num + "○" * (total - question_num)
        print(f"\n{self.MAGENTA}📋 QUESTION {question_num}/{total}{self.RESET} {self.GRAY}[{progress}]{self.RESET}")
    
    def user_input(self, message: str, is_silence: bool = False):
        timestamp = self._get_timestamp()
        if is_silence:
            print(f"{self.GRAY}[{timestamp}]{self.RESET} {self.DIM}👤 You:{self.RESET} {self.GRAY}[silence]{self.RESET}")
        else:
            print(f"{self.GRAY}[{timestamp}]{self.RESET} {self.BOLD}👤 You:{self.RESET} {message}")
    
    def bot_response(self, message: str, question_num: Optional[int] = None):
        timestamp = self._get_timestamp()
        prefix = "🍺 Terry:"
        if question_num:
            prefix = f"🍺 Terry [Q{question_num}]:"
        print(f"{self.GRAY}[{timestamp}]{self.RESET} {self.YELLOW}{prefix}{self.RESET} {message}")
    
    def recording_start(self):
        print(f"\n{self.BG_RED}{self.WHITE} ● REC {self.RESET} {self.RED}Hold spacebar to record...{self.RESET}")
    
    def recording_stop(self):
        print(f"{self.GRAY}● Recording stopped{self.RESET}")
    
    def transcribing(self):
        print(f"{self.BLUE}🎤 Transcribing speech...{self.RESET}")
    
    def thinking(self):
        print(f"{self.MAGENTA}🤔 Terry is thinking...{self.RESET}")
    
    def speaking(self):
        print(f"{self.CYAN}🗣️  Terry is speaking...{self.RESET}")
    
    def beer_dispensed(self):
        print(f"\n{self.BG_YELLOW}{self.BOLD} 🍺 BEER DISPENSED! 🍺 {self.RESET}")
        print(f"{self.YELLOW}{'🍺' * 20}{self.RESET}")
    
    def conversation_end(self):
        elapsed = self._get_elapsed()
        print(f"\n{self.BG_BLUE}{self.WHITE} CONVERSATION ENDED {self.RESET}")
        print(f"{self.GRAY}Session duration:{self.RESET} {elapsed}")
        if self.session_id:
            print(f"{self.GRAY}Session saved:{self.RESET} {self.session_id}")
        print(f"{self.GRAY}{'─' * 50}{self.RESET}")
        print(f"{self.GREEN}Ready for next customer...{self.RESET}\n")
    
    def separator(self):
        print(f"{self.GRAY}{'─' * 60}{self.RESET}")
    
    def system_info(self, info_dict: dict):
        print(f"\n{self.BOLD}{self.WHITE}System Information:{self.RESET}")
        for key, value in info_dict.items():
            status_color = self.GREEN if value.get('available', True) else self.RED
            status_icon = "✓" if value.get('available', True) else "✗"
            print(f"  {status_color}{status_icon}{self.RESET} {key}: {value}")
    
    def component_init(self, component: str, status: str = "OK"):
        icon = "✓" if status == "OK" else "✗"
        color = self.GREEN if status == "OK" else self.RED
        print(f"  {color}{icon}{self.RESET} {component}")
    
    def cleanup_start(self):
        print(f"{self.YELLOW}🧹 Cleaning up old files...{self.RESET}")
    
    def cleanup_complete(self):
        print(f"{self.GREEN}✓ Cleanup complete{self.RESET}")


# Global instance
display = TerryDisplay()