from abc import abstractmethod
from pathlib import Path
from typing import Iterable, Tuple, Callable
from zipfile import BadZipFile
from odf.element import Element
from odf import text as odf_text, teletype, table as odfpy_table
from odf.opendocument import load as odf_load, OpenDocument

from irspy.protocol_generator.protocol_generator import ProtocolGenerator, ProtocolConfig
from irspy.protocol_generator.data_table import DataTable
from irspy.protocol_generator.utils import handle_exceptions


def _make_odf_rows(data_table: DataTable) -> Iterable[odfpy_table.Element]:
    covered_rows = 0
    for row_index, (row_pos, data_row) in enumerate(data_table.rows):
        if (index_delta := row_pos - row_index - covered_rows) > 0:
            covered_row = odfpy_table.TableRow(numberrowsrepeated=index_delta)
            covered_rows += index_delta
            yield covered_row

        odf_row = odfpy_table.TableRow()
        covered_cells = 0
        for data_cell_index, data_cell in enumerate(data_row):
            if (index_delta := data_cell.column - data_cell_index - covered_cells) > 0:
                covered_cell = odfpy_table.CoveredTableCell(numbercolumnsrepeated=index_delta)
                odf_row.addElement(covered_cell)
                covered_cells += index_delta

            odf_cell = odfpy_table.TableCell(valuetype="string",
                                             numberrowsspanned=data_cell.row_span,
                                             numbercolumnsspanned=data_cell.column_span)
            text = odf_text.P(text=str(data_cell.value))
            odf_cell.addElement(text)
            odf_row.addElement(odf_cell)

        yield odf_row


def _make_odf_table(data_table: DataTable) -> odfpy_table.Table:
    odf_table = odfpy_table.Table()
    odf_column = odfpy_table.TableColumn(numbercolumnsrepeated=data_table.column_count)
    odf_table.addElement(odf_column)
    for odf_row in _make_odf_rows(data_table):
        odf_table.addElement(odf_row)
    return odf_table


def _make_text_element(old_element: Element, dst: str, src: str) -> Element:
    new_element = odf_text.P()
    new_element.setAttribute("stylename", old_element.getAttribute("stylename"))

    for space_elements in old_element.getElementsByType(odf_text.S):
        # Без этого все пробельные символы в начале строк удалятся
        spaces = space_elements.getAttribute('c')
        if spaces is not None:
            new_space_element = odf_text.S()
            new_space_element.setAttribute('c', spaces)
            new_element.appendChild(new_space_element)

    text = teletype.extractText(old_element).replace(dst, src)
    new_element.addText(text)
    return new_element


def _insert_element_before(dst_elements: Iterable[Element] | Element, src_element: Element) -> None:
    if not isinstance(dst_elements, Iterable):
        dst_elements = (dst_elements, )
    for dst_element in dst_elements:
        if src_element.parentNode:
            src_element.parentNode.insertBefore(dst_element, src_element)


def _replace_elements(document: OpenDocument, src_element: Element, dst_elements: Iterable[Element] | Element) -> None:
    if src_element is not None and src_element.parentNode is not None:
        _insert_element_before(dst_elements, src_element)
        src_element.parentNode.removeChild(src_element)
        # Без этого дерево нодов сломается
        document.rebuild_caches(src_element.parentNode)


def _find_parent(child: Element, parent_type: Callable[..., Element]) -> Element | None:
    while not (child is None or child.isInstanceOf(parent_type)):
        parent = child.parentNode
        if child.parentNode:
            child.parentNode.removeChild(child)
        child = parent
    return child


def _find_elements(document: OpenDocument,
                   texts: Iterable[str],
                   element_types: Iterable[Callable[..., Element]]) -> Iterable[Tuple[str, Element]]:
    for element_type in element_types:
        for element in document.getElementsByType(element_type):
            for text in texts:
                if text in teletype.extractText(element):
                    yield text, element


class _OdfProtocolGenerator(ProtocolGenerator):
    TEXT_ELEMENT_TYPES = odf_text.H, odf_text.P

    @handle_exceptions(BadZipFile, PermissionError, FileNotFoundError)
    def generate(self, file: Path, config: ProtocolConfig) -> None:
        document = odf_load(file)

        for tag, element in _find_elements(document, config.tag_map.keys(), self.TEXT_ELEMENT_TYPES):
            value = config.tag_map[tag]
            if isinstance(value, DataTable):
                new_element = self._make_table(value)
                if (parent_type := self._table_parent_type()) is not None:
                    element = _find_parent(element, parent_type)
            else:
                new_element = _make_text_element(element, tag, str(value))

            _replace_elements(document, element, new_element)

        document.save(file)

    @abstractmethod
    def _make_table(self, data_table: DataTable) -> Iterable[Element] | Element:
        pass

    @abstractmethod
    def _table_parent_type(self) -> Callable[..., Element] | None:
        pass


class OdsProtocolGenerator(_OdfProtocolGenerator):
    def _make_table(self, data_table: DataTable) -> Iterable[Element]:
        return _make_odf_rows(data_table)

    def _table_parent_type(self) -> Callable[..., Element] | None:
        return odfpy_table.TableRow


class OdtProtocolGenerator(_OdfProtocolGenerator):
    def _make_table(self, data_table: DataTable) -> Element:
        return _make_odf_table(data_table)

    def _table_parent_type(self) -> Callable[..., Element] | None:
        return None
