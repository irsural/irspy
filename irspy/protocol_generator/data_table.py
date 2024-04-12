import itertools
import operator
from dataclasses import dataclass
from operator import attrgetter
from typing import Any, Iterable, Tuple, Set, Iterator, Callable, List


@dataclass
class DataCell:
    row: int
    column: int
    value: Any = None
    row_span: int = 1
    column_span: int = 1

    @property
    def row_positions(self) -> Iterable[int]:
        return range(self.row, self.row + self.row_span)

    @property
    def column_positions(self) -> Iterable[int]:
        return range(self.column, self.column + self.column_span)

    @property
    def positions(self) -> Iterable[Tuple[int, int]]:
        for r in self.row_positions:
            for c in self.column_positions:
                yield r, c

    def __comp(self, other: 'DataCell', func: Callable[[int, int], bool]) -> bool:
        if self.row == other.row:
            return func(self.column, other.column)
        return func(self.row, other.row)

    def __le__(self, other: 'DataCell') -> bool:
        return self.__comp(other, operator.le)

    def __lt__(self, other: 'DataCell') -> bool:
        return self.__comp(other, operator.lt)

    def __ge__(self, other: 'DataCell') -> bool:
        return self.__comp(other, operator.ge)

    def __gt__(self, other: 'DataCell') -> bool:
        return self.__comp(other, operator.gt)


class DataTable:
    def __init__(self,
                 cells: Iterable[DataCell],
                 xlsx_row_heights: List[int | None] | None = None,
                 xlsx_column_widths: List[int | None] | None = None,
                 add_border: bool = False) -> None:
        self.__xlsx_column_widths = xlsx_column_widths if xlsx_column_widths else []
        self.__xlsx_row_heights = xlsx_row_heights if xlsx_row_heights else []
        self.__add_border = add_border

        used_cells: Set[Tuple[int, int]] = set()
        for cell in cells:
            for row, column in cell.positions:
                if (row, column) in used_cells:
                    raise ValueError('Ячейки таблицы перекрываются', cell)
                used_cells.add((row, column))
        self.__row_count = 1 + max((cell[0] for cell in used_cells))
        self.__column_count = 1 + max((cell[1] for cell in used_cells))
        self.__cells = sorted(cells)

    @property
    def xlsx_row_heights(self) -> List[int | None]:
        return self.__xlsx_row_heights

    @property
    def xlsx_column_widths(self) -> List[int | None]:
        return self.__xlsx_column_widths

    @property
    def add_border(self) -> bool:
        return self.__add_border

    @property
    def rows(self) -> Iterable[Tuple[int, Iterable[DataCell]]]:
        for k, g in itertools.groupby(self.__cells, attrgetter('row')):
            yield int(k), list(g)

    @property
    def row_count(self) -> int:
        return self.__row_count

    @property
    def column_count(self) -> int:
        return self.__column_count

    @property
    def cells(self) -> Iterator[DataCell]:
        return iter(self.__cells)
