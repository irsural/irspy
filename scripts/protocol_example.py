import shutil

from irspy.protocol_generator.data_table import DataTable, DataCell
from irspy.protocol_generator.protocol_generator import ProtocolConfig
from irspy.protocol_generator.protocol_generator_docx import DocxProtocolGenerator
from irspy.protocol_generator.protocol_generator_odt import OdtProtocolGenerator
from irspy.protocol_generator.protocol_generator_xlsx import XlsxProtocolGenerator


if __name__ == '__main__':
    data_table = DataTable(
        cells=[
            DataCell(row=0, column=0, row_span=1, column_span=2, value='Поверяемый прибор'),
            DataCell(row=0, column=2, row_span=1, column_span=4, value='Образцовый прибор'),
            DataCell(row=0, column=6, row_span=3, column_span=1, value='Вариация показаний'),

            DataCell(row=1, column=0, row_span=2, column_span=1, value='Отсчет по шкале, деление'),
            DataCell(row=1, column=1, row_span=2, column_span=1, value='Показание'),

            DataCell(row=1, column=2, row_span=1, column_span=1,
                     value='Отсчет по шкале при прямом направлении тока, деление'),
            DataCell(row=1, column=3, row_span=1, column_span=1,
                     value='Отсчет по шкале при обратном направлении тока, деление'),
            DataCell(row=1, column=4, row_span=1, column_span=1,
                     value='Отсчет по шкале при прямом направлении тока, деление'),
            DataCell(row=1, column=5, row_span=1, column_span=1,
                     value='Отсчет по шкале при обратном направлении тока, деление'),

            DataCell(row=2, column=2, row_span=1, column_span=1, value='Среднее значение1'),
            DataCell(row=2, column=3, row_span=1, column_span=1, value='Среднее значение2'),
            DataCell(row=2, column=4, row_span=1, column_span=1, value='Отклонение., %'),
            DataCell(row=2, column=5, row_span=1, column_span=1, value='Отклонение., %'),

            DataCell(row=3, column=0, row_span=1, column_span=1, value='1'),
            DataCell(row=3, column=2, row_span=1, column_span=1, value='3'),
            DataCell(row=3, column=3, row_span=1, column_span=1, value='4'),
            DataCell(row=3, column=4, row_span=1, column_span=1, value='5'),
            DataCell(row=3, column=5, row_span=1, column_span=1, value='6'),

            DataCell(row=4, column=0, row_span=1, column_span=1, value='7'),
            DataCell(row=4, column=1, row_span=1, column_span=1, value='8'),
            DataCell(row=4, column=2, row_span=1, column_span=1, value='9'),
            DataCell(row=4, column=3, row_span=1, column_span=1, value='10'),
            DataCell(row=4, column=4, row_span=1, column_span=1, value='11'),
            DataCell(row=4, column=5, row_span=1, column_span=1, value='12'),
        ],
        add_border=True,
        xlsx_row_heights=[None, 50, 30],
        xlsx_column_widths=[25, 25, 25, 25, 25, 25, 25],
    )

    config = ProtocolConfig(
        tag_map={
            '%text_1': 'replaced_1',
            '%text_2': 'replaced_2',
            '%table_1': data_table,
            '%text_3': 'replaced_3',
        },
    )

    templates = {
        'protocols/template.xlsx': XlsxProtocolGenerator(),
        'protocols/template.odt': OdtProtocolGenerator(),
        'protocols/template.docx': DocxProtocolGenerator(),
    }

    for template, generator in templates.items():
        protocol = template.replace('template', 'protocol')
        shutil.copy2(template, protocol)
        generator.generate(protocol, config)
