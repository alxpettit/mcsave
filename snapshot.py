import abc
import datetime
import logging
import shutil
from pathlib import Path

class Snapshot:
    """ Generic base snapshot class, allowing us to switch between different snapshot methods"""
    mc_server_instance_name: str = 'mc0'
    time_format = '%Y-%m-%d %H:%M:%S'
    logger = logging.getLogger(__name__)

    # If overridden before process_src_dst is called,
    # this value will override get_default functions
    src: Path = None
    dst: Path = None

    # def get_default_src(self) -> Path:
    #     return Path(f'/dvol/{self.mc_server_instance_name}/world')

    # def get_default_dst(self) -> Path:
    #     timestamp = datetime.datetime.now().strftime(self.time_format)
    #     return Path.home() / '.mc_snapshots' / self.mc_server_instance_name / timestamp

    # @abc.abstractmethod
    # def do_snapshot(self):
    #     """ Does the actual snapshot process. """
    #     raise NotImplementedError

    # def process_src_dst(self):
    #     if self.src is None:
    #         self.src = self.get_default_src()
    #     if self.dst is None:
    #         self.dst = self.get_default_dst()

class BasicSnapshot(Snapshot):
    def do_snapshot(self):
        # self.process_src_dst()
        shutil.copytree(self.src, self.dst)
