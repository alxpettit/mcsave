#!/usr/bin/env python3

# TODO: set up version tracking
# TODO: add config parsing
# See: https://www.reddit.com/r/admincraft/comments/vgdbi/minecraft_backups_saveoff_and_saveall/

import time
import logging
from pathlib import Path
from threading import Thread
import sys

from minecraft_control import MinecraftSaveControl
from snapshot import BasicSnapshot

log_file_name: str = 'main.log'
root_logger = logging.root
root_logger.setLevel(logging.DEBUG)
log_formatter = logging.Formatter("%(asctime)s:%(levelname)s %(message)s")

stream_handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_formatter)
stream_handler.setLevel(logging.DEBUG)
root_logger.addHandler(stream_handler)

file_handler: logging.StreamHandler = logging.FileHandler(log_file_name, mode='w', encoding='utf-8')
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)

class MCSaveThread(Thread):
    snap: BasicSnapshot
    ctrl: MinecraftSaveControl
    src: Path
    dst: Path

    def __init__(self, port: int, src, dst):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.snap = BasicSnapshot()
        self.snap.src = Path(src)
        self.snap.dst = Path(dst)
        self.ctrl = MinecraftSaveControl()
        self.ctrl.port = port
        self.ctrl.connect()

    # Shut up Pycharm -- I know what I'm doing >.>
    # noinspection PyBroadException
    def run(self):
        try:
            while True:
                self.loop()
                time.sleep(60 * 5)  # run loop every 5 mins
        except KeyboardInterrupt:
            stop_request(self)
        except Exception as e:
            # If we fail, DO NOT LEAVE SAVING DISABLED!!!!
            try:
                self.ctrl.save_on()
            except Exception:
                pass
            self.ctrl.say('Oh dear. It seems something horrible has gone wrong with my programming. Help, Alexandria! >.<')
            # raise  # Raise original exception

    def loop(self):
        self.logger.info('Checking for number of players...')
        if self.ctrl.num_players() > 0:  # No backups necessary if no one is online and making changes to the server
            self.ctrl.say('Players have been detected by automated system.')
            self.ctrl.say('Beginning Alexandria\'s backup process...')
            self.ctrl.save_off()
            self.ctrl.save_all()
            # At this point, we should be safe from unexpected writes to save file...
            try:
                self.snap.do_snapshot()
                self.ctrl.say(
                    'Backup complete. If you see this message, everything has probably gone as intended! ^w^')
            except FileNotFoundError:
                self.ctrl.say('FileNotFoundError while attempting to create snapshot. Oh no :(')
            self.ctrl.save_on()
            if self.ctrl.saving_enabled is False:
                self.ctrl.say('WARNING: It looks like I was unable to enable automatic world-saving.\
                Your world might be in danger! D:')
            time.sleep(60 * 60)
        else:
            self.logger.info('Skipping backup process.')


def stop_request(mc: MCSaveThread):
    mc.ctrl.say('Looks like I\'ve been asked to stop. Oh well. See y\'all later!')
    mc.ctrl.save_on()
    exit(0)


def main():
    threads = [
        MCSaveThread(25575, '/var/lib/docker/volumes/mc0_mc0/_data/world',
                          '/var/lib/docker/volumes/mc0_mc0/_data/.snapshots'),
        MCSaveThread(25577, '/dvol/mc2/world', '/dvol/mc2/.mc_snapshots/mc2')
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

if __name__ == '__main__':
    main()