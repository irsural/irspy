from dataclasses import dataclass
from pathlib import Path
from abc import ABCMeta, abstractmethod
from typing import Dict

from irspy.protocol_generator.data_table import DataTable


@dataclass
class ProtocolConfig:
    def __post_init__(self) -> None:
        for key, val in self.tag_map.items():
            if val is None:
                self.tag_map[key] = '-'
            elif not isinstance(val, DataTable):
                self.tag_map[key] = str(val)

    tag_map: Dict[str, str | DataTable]


class ProtocolGenerator(metaclass=ABCMeta):
    @abstractmethod
    def generate(self, file: Path, config: ProtocolConfig) -> bool:
        pass
