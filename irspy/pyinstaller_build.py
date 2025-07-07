from typing import List
import os


version_file_content = \
"""
# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
# filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
# Set not needed items to zero 0.
filevers=(0, {version}, 0, 0),
prodvers=(0, 0, 0, 0),
# Contains a bitmask that specifies the valid bits 'flags'r
mask=0x0,
# Contains a bitmask that specifies the Boolean attributes of the file.
flags=0x0,
# The operating system for which this file was designed.
# 0x4 - NT and there is no need to change it.
OS=0x4,
# The general type of file.
# 0x1 - the file is an application.
fileType=0x1,
# The function of the file.
# 0x0 - the function is not defined for this fileType
subtype=0x0,
# Creation date and time stamp.
date=(0, 0)
),
  kids=[
StringFileInfo(
  [
  StringTable(
    u'040904B0',
    [StringStruct(u'CompanyName', u'ООО "Радиоэлектронные системы"'),
    StringStruct(u'FileDescription', u'Clb AutoCalibration'),
    StringStruct(u'FileVersion', u'0.{version}.0.0'),
    StringStruct(u'InternalName', u'CAC'),
    StringStruct(u'LegalCopyright', u'Копирайт © ООО "РЭС"'),
    StringStruct(u'OriginalFilename', u'Clb_AutoCalibration.exe'),
    StringStruct(u'ProductName', u'Calibrator AutoCalibration'),
    StringStruct(u'ProductVersion', u'0.{version}.0.0')])
  ]), 
VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""


def _create_pyinstaller_parameter(pyinstaller_parameter: str, args: List[str], add_data_sep: str) -> str:
    if args:
        hidden_import_parts = []
        for arg in args:
            hidden_import_parts.append(f' {pyinstaller_parameter} "{arg}"{add_data_sep}.')
        pyinstaller_param_with_args = "".join(hidden_import_parts)
    else:
        pyinstaller_param_with_args = ""
    return pyinstaller_param_with_args


def _create_pyinstaller_parameter_without_sep(pyinstaller_parameter: str, args: List[str]) -> str:
    if args:
        hidden_import_parts = []
        for arg in args:
            hidden_import_parts.append(f' {pyinstaller_parameter} "{arg}"')
        pyinstaller_param_with_args = "".join(hidden_import_parts)
    else:
        pyinstaller_param_with_args = ""
    return pyinstaller_param_with_args


def build_app(
    a_main_filename: str,
    a_app_name: str,
    a_version: int,
    a_icon_filename: str="",
    a_noconsole=True,
    a_one_file=True,
    a_libs: List[str]=None,
    a_hidden_import: List[str]=None,
    a_collect_all: List[str]=None,
) -> None:
    """
    Запускает сборку через pyinstaller с заданными параметрами.
    :param a_main_filename: Имя файла главного скрипта
    :param a_app_name: Имя приложения
    :param a_version: Версия приложения
    :param a_icon_filename: Путь к иконке приложения
    :param a_noconsole: Параметр noconole в pyinstaller
    :param a_one_file: Параметр onefile в pyinstaller
    :param a_libs: Библиотеки (dll), которые нужно добавить в сборку
    :param a_hidden_import: параметр hidden-import в pyinstaller
    :param a_collect_all: параметр collect-all в pyinstaller
    """
    name = " -n {}".format(a_app_name)
    onefile = " --onefile" if a_one_file else ""
    noconsole = " --noconsole" if a_noconsole else ""
    icon = " --icon={}".format(a_icon_filename) if a_icon_filename else ""
    add_data_sep = ";" if os.name == 'nt' else ":"
    libs = _create_pyinstaller_parameter('--add-data', a_libs, add_data_sep)
    hidden_import = _create_pyinstaller_parameter_without_sep('--hidden-import', a_hidden_import)
    collect_all = _create_pyinstaller_parameter_without_sep('--collect-all', a_collect_all)

    version_filename = "version.txt"
    with open(version_filename, 'w', encoding="utf8") as version_file:
        version_file.write(version_file_content.format(version=a_version))
        version = " --version-file={}".format(version_filename)

    os.system(
        "pyinstaller{}{}{}{}{}{}{}{} {}".format(
            name, onefile, noconsole, icon, version, libs, hidden_import, collect_all, a_main_filename
        )
    )

    os.remove(version_filename)


def build_qt_app(
    a_main_filename: str,
    a_app_name: str,
    a_version: int,
    a_icon_filename: str="",
    a_noconsole=True,
    a_one_file=True,
    a_libs: List[str]=None,
    a_hidden_import: List[str]=None,
    a_collect_all: List[str]=None,
) -> None:
    """
      Запускает сборку через pyinstaller с заданными параметрами. Перед этим удаляет из главного скрипта строки,
      которые конвертируют ресурсы qt в python.
      Параметры, как у build_app
    """

    tmp_filename = "{}.py".format(a_app_name)

    with open(a_main_filename, encoding='utf8') as main_py:
        with open(tmp_filename, "w", encoding='utf8') as compile_main:
            for line in main_py:
                if not ("ui_to_py" in line):
                    compile_main.write(line)

    build_app(
        tmp_filename,
        a_app_name,
        a_version,
        a_icon_filename,
        a_noconsole,
        a_one_file,
        a_libs,
        a_hidden_import,
        a_collect_all
    )

    os.remove(tmp_filename)
