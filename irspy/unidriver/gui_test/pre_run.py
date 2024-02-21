from irspy.qt.ui_to_py import convert_ui, create_translate, convert_resources, compile_ts
import os

gui_test_dir = f'{os.getcwd()}/unidriver/gui_test'
convert_resources(f'{os.getcwd()}/qt/resources', f'{gui_test_dir}/ui/resources')
convert_ui(f'{gui_test_dir}/ui/', f'{gui_test_dir}/ui/py', resources_path='irspy.unidriver.gui_test.ui.resources')
create_translate(f'{gui_test_dir}/', f'{gui_test_dir}/ui/translations/en.ts', True)
compile_ts(f'{gui_test_dir}/ui/translations', f'{gui_test_dir}/ui/translations')
