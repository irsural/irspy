from dataclasses import dataclass
from pathlib import Path
from abc import ABCMeta, abstractmethod
from typing import Dict

from irspy.protocol_generator.data_table import DataTable


@dataclass
class ProtocolConfig:
    tag_map: Dict[str, str | DataTable]


class ProtocolGenerator(metaclass=ABCMeta):
    @abstractmethod
    def generate(self, file: Path, config: ProtocolConfig) -> bool:
        pass
