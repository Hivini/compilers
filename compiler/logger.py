class Logger:
    # ANSI Escape Codes
    OK = '\033[94m'
    DEBUG = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'

    def LogDebug(self, message: str):
        print(self._CreateMessage(self.DEBUG, message))

    def LogError(self, message: str):
        print(self._CreateMessage(self.ERROR, f'ERROR: {message}'))

    def LogSuccess(self, message: str):
        print(self._CreateMessage(self.OK, message))

    def _CreateMessage(self, escapeCode: str, message) -> str:
        return f'{escapeCode}{message}{self.ENDC}'
