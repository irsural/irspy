from pathlib import Path
from typing import Iterable, Tuple
from zipfile import BadZipFile
from odf.element import Element
from odf import text as odf_text, teletype, table as odfpy_table
from odf.opendocument import load as odf_load, OpenDocument

from irspy.protocol_generator.protocol_generator import ProtocolGenerator, ProtocolConfig
from irspy.protocol_generator.data_table import DataTable, DataCell
from irspy.protocol_generator.utils import handle_exceptions


class _OdfTableFabric:
    def __init__(self) -> None:
        self.__curr_row = 0
        self.__curr_cell = 0

    def make(self, data_table: DataTable) -> odfpy_table.Table:
        odf_table = odfpy_table.Table()

        for _ in range(data_table.column_count):
            self.__add_column(odf_table, self.__make_odf_column())

        header_rows = odfpy_table.TableHeaderRows()
        self.__curr_row = 0
        for row_index, data_row in data_table.rows:
            odf_row = self.__make_odf_row()
            self.__add_row(odf_table, odf_row, row_index, header_rows=header_rows,
                           header_row_count=data_table.header_rows)
            # FIXME: Если в предыдущей строке есть клетки с column_span > 1, работает не так как ожидается
            self.__curr_cell = 0
            for data_cell in data_row:
                odf_cell = self.__make_odf_cell(data_cell)
                self.__add_cell(odf_row, odf_cell, data_cell.column, data_cell.column_span)

        return odf_table

    def __make_odf_cell(self, data_cell: DataCell | None = None) -> odfpy_table.TableCell:
        if data_cell is None:
            odf_cell = odfpy_table.CoveredTableCell()
            # odf_cell = odfpy_table.TableCell(valuetype="string", numberrowsspanned=1,
            #                                  numbercolumnsspanned=1)
        else:
            odf_cell = odfpy_table.TableCell(valuetype="string", numberrowsspanned=data_cell.row_span,
                                             numbercolumnsspanned=data_cell.column_span)
            text = odf_text.P(text=str(data_cell.value))
            odf_cell.addElement(text)
        return odf_cell

    def __make_odf_row(self) -> odfpy_table.TableRow:
        return odfpy_table.TableRow()

    def __make_odf_column(self) -> odfpy_table.TableColumn:
        return odfpy_table.TableColumn()

    def __add_cell(self, odf_row: odfpy_table.TableRow, odf_cell: odfpy_table.TableCell,
                   pos: int, span: int) -> None:
        for _ in range(self.__curr_cell, pos):
            odf_row.addElement(self.__make_odf_cell())
        self.__curr_cell = pos + span
        odf_row.addElement(odf_cell)

    def __add_row(self,
                  odf_table: odfpy_table.Table,
                  odf_row: odfpy_table.TableRow,
                  pos: int,
                  span: int = 1,
                  header_rows: Element = odfpy_table.TableHeaderRows(),
                  header_row_count: int = 0) -> None:
        def add_row(row: Element, curr_pos: int) -> None:
            if curr_pos < header_row_count:
                header_rows.addElement(row)
                if curr_pos + 1 == header_row_count:
                    odf_table.addElement(header_rows)
            else:
                odf_table.addElement(row)

        for i in range(self.__curr_row, pos):
            empty_row = self.__make_odf_row()
            add_row(empty_row, self.__curr_row + i)
        add_row(odf_row, pos)
        self.__curr_row = pos + span

    def __add_column(self, odf_table: odfpy_table.Table, odf_column: odfpy_table.TableColumn) -> None:
        odf_table.addElement(odf_column)


class OdtProtocolGenerator(ProtocolGenerator):
    TEXT_ELEMENT_TYPES = odf_text.H, odf_text.P

    def __init__(self) -> None:
        self.__table_fabric = _OdfTableFabric()

    @handle_exceptions(BadZipFile, PermissionError, FileNotFoundError)
    def generate(self, file: Path, config: ProtocolConfig) -> None:
        document = odf_load(file)
        for tag, element in self.__find_elements(document, config.tag_map.keys(),
                                                 self.TEXT_ELEMENT_TYPES):
            value = config.tag_map[tag]
            if isinstance(value, DataTable):
                new_element = self.__table_fabric.make(value)
            else:
                new_element = self.__make_text_element(element, tag, str(value))
            self.__replace_elements(document, element, new_element)

        document.save(file)

    def __make_text_element(self, old_element: Element, dst: str, src: str) -> Element:
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

    def __find_elements(self, document: OpenDocument, texts: Iterable[str], element_types) -> \
            Iterable[Tuple[str, Element]]:
        for element_type in element_types:
            for element in document.getElementsByType(element_type):
                for text in texts:
                    if text in teletype.extractText(element):
                        yield text, element

    def __replace_elements(self, document: OpenDocument, src_element: Element,
                           dst_element: Element) -> None:
        if src_element.parentNode is not None:
            src_element.parentNode.insertBefore(dst_element, src_element)
            src_element.parentNode.removeChild(src_element)
            # Без этого дерево нодов сломается
            document.rebuild_caches(src_element.parentNode)
