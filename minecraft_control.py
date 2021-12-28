import logging
import re
import time
from pathlib import Path
from typing import Optional

from rcon import Client


class MinecraftSaveControl:
    logger = logging.getLogger(__name__)
    client: Client = None
    last_response: str
    max_connect_attempts: int = -1  # -1 means infinite attempts
    longdelay_attempts_threshold: int = 60  # Number of attempts before switching to long delay mode
    host: str = '127.0.0.1'
    port: int = 25575
    delay_between_attempts: int = 5
    longdelay_between_attempts: int = 120  # 2 mins by default
    saving_enabled: bool = True

    def __init__(self, pwfile: Optional[Path] = None, passwd: Optional[str] = None):
        if pwfile is None:
            pwfile = Path.home() / ".mcpw"
        if passwd is None:
            try:
                passwd = pwfile.open('r').read().strip()
            except FileNotFoundError:
                self.logger.warning('No .mcpw file found.')
        self.passwd = passwd

    def __del__(self):
        # For safety, try to ensure that save is always on when class is deleted
        self.save_on()

    def connect(self):
        self.logger.info('Beginning RCON server connection attempt...')
        attempts = 0
        delay_between_attempts: int = self.delay_between_attempts
        while True:
            try:
                self.client = Client(self.host, self.port, passwd=self.passwd)
                self.client.connect(True)
                break
            except (ConnectionRefusedError, ConnectionResetError) as e:
                self.logger.warning('Could not connect to server. Retrying in %i seconds',
                                    delay_between_attempts)
            time.sleep(delay_between_attempts)

            if self.max_connect_attempts != -1 and attempts >= self.max_connect_attempts:
                raise ConnectionError  # We give up
            elif attempts > self.longdelay_attempts_threshold:
                delay_between_attempts = self.longdelay_between_attempts
            # Keep track of attempts
            attempts += 1
            del self.client  # Important to avoid connection reset error, i think

    def _run_wrapper(self, *args) -> str:
        self.logger.info('Sending command: %s', list(args))
        try:
            r = self.client.run(*args)
            return r
        except AttributeError as e:
            self.logger.debug("Could not run RCON command. Was .connect() skipped?", exc_info=e)

    def set_save(self, state: bool):
        if state:
            self.save_on()
        else:
            self.save_off()

    def save_on(self) -> bool:
        r = self._run_wrapper('save-on')
        success = 'now enabled' in r or 'already turned on' in r
        self.saving_enabled = success
        return success

    def save_off(self) -> bool:
        r = self._run_wrapper('save-off')
        self.last_response = r
        success = 'now disabled' in r or 'already turned off' in r
        self.saving_enabled = not success  # If we succeeded, saving is disabled, and vice versa
        return success

    def save_all(self) -> bool:
        r = self._run_wrapper('save-all')
        self.last_response = r
        success = 'Saved the game' in r
        return success

    def num_players(self) -> int:
        r = self._run_wrapper('list')
        match = re.match(r'There are (\d*) of .*', r)
        num_players = int(match.group(1))
        self.logger.info("Number of players detected as %i", num_players)
        return num_players

    def say(self, msg: str):
        r = self.client.run('say', msg)
        print(r)
