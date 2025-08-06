import typing
from typing import List, Tuple, Union
import os

import PyInstaller.__main__ as pyinstaller


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
    [StringStruct(u'CompanyName', u'{company_name}'),
    StringStruct(u'FileDescription', u'{file_description}'),
    StringStruct(u'FileVersion', u'{version}'),
    StringStruct(u'InternalName', u'{internal_name}'),
    StringStruct(u'LegalCopyright', u'{copyright}'),
    StringStruct(u'OriginalFilename', u'{original_filename}'),
    StringStruct(u'ProductName', u'{product_name}'),
    StringStruct(u'ProductVersion', u'{version}')])
  ]), 
VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""


class AppInfo:
    def __init__(self, a_app_name, a_company_name="", a_file_description="", a_version="0.0", a_internal_name="",
                 a_copyright="", a_original_filename="", a_product_name=""):

        self.app_name = a_app_name
        self.company_name = a_company_name
        self.file_description = a_file_description
        self.version = a_version
        self.internal_name = a_internal_name
        self.copyright = a_copyright
        self.original_filename = a_original_filename
        self.product_name = a_product_name


def build_app(
        a_main_filename: Union[str, os.PathLike],
        a_app_info: AppInfo,
        a_icon_filename: Union[str, os.PathLike] = "",
        a_noconsole=True,
        a_one_file=True,
        a_admin = False,
        a_libs: List[Tuple[Union[str, os.PathLike], str]] = None,
        dist_path: Union[str, os.PathLike, None] = None,
        spec_path: Union[str, os.PathLike, None] = None,
        build_path: Union[str, os.PathLike, None] = None,
        version_filename: Union[str, os.PathLike] = 'version.txt',
        a_hidden_import: List[Union[str, os.PathLike]] = None,
        a_collect_all: List[Union[str, os.PathLike]] = None,
) -> None:
    """
    Запускает сборку через pyinstaller с заданными параметрами.
    :param a_main_filename: Имя файла главного скрипта
    :param a_app_info: Информация о приложении
    :param a_icon_filename: Путь к иконке приложения
    :param a_noconsole: Параметр noconole в pyinstaller
    :param a_one_file: Параметр onefile в pyinstaller
    :param a_admin: Параметр --uac-admin в pyinstaller
    :param a_libs: Библиотеки (dll), которые нужно добавить в сборку
    :param dist_path: Параметр --distpath в pyinstaller
    :param spec_path: Параметр --specpath в pyinstaller
    :param build_path: Параметр --workpath в pyinstaller
    :param version_filename: Параметр --version-file в pyinstaller
    :param a_hidden_import: Параметр --hidden-import в pyinstaller
    :param a_collect_all: Параметр --collect-all в pyinstaller
    """
    pyinstaller_args = [a_main_filename, "--name={}".format(a_app_info.app_name)]
    if a_one_file:
        pyinstaller_args.append("--onefile")
    if a_noconsole:
        pyinstaller_args.append("--noconsole")
    if a_icon_filename:
        pyinstaller_args.append("--icon={}".format(a_icon_filename))
    if a_admin:
        pyinstaller_args.append("--uac-admin")
    if a_libs:
        for src, dst in a_libs:
            pyinstaller_args.append("--add-data={}{}{}".format(src, os.pathsep, dst))
    if dist_path:
        pyinstaller_args.append("--distpath={}".format(dist_path))
    if spec_path:
        pyinstaller_args.append("--specpath={}".format(spec_path))
    if build_path:
        pyinstaller_args.append("--workpath={}".format(build_path))
    if a_hidden_import:
        for module_name in a_hidden_import:
            pyinstaller_args.append("--hidden-import={}".format(module_name))
    if a_collect_all:
        for module_name in a_collect_all:
            pyinstaller_args.append("--collect-all={}".format(module_name))

    with open(version_filename, 'w', encoding="utf8") as version_file:
        version_file.write(version_file_content.format(
            company_name=a_app_info.company_name, file_description=a_app_info.file_description,
            version=a_app_info.version, internal_name=a_app_info.internal_name,
            copyright=a_app_info.copyright, original_filename=a_app_info.original_filename,
            product_name=a_app_info.product_name)
        )

    pyinstaller_args.append("--version-file={}".format(version_filename))

    try:
        pyinstaller.run(pyinstaller_args)
    finally:
        os.remove(version_filename)


def build_qt_app(
        a_main_filename: Union[os.PathLike, str],
        a_app_info: AppInfo,
        a_icon_filename: Union[str, os.PathLike] = "",
        a_noconsole=True,
        a_one_file=True,
        a_admin=False,
        a_libs: List[Tuple[Union[str, os.PathLike], str]] = None,
        dist_path: Union[str, os.PathLike, None] = None,
        spec_path: Union[str, os.PathLike, None] = None,
        build_path: Union[str, os.PathLike, None] = None,
        version_file_path: Union[str, os.PathLike, None] = None,
        a_hidden_import: List[Union[str, os.PathLike]] = None,
        a_collect_all: List[Union[str, os.PathLike]] = None,
) -> None:
    """
      Запускает сборку через pyinstaller с заданными параметрами. Перед этим удаляет из главного скрипта строки,
      которые конвертируют ресурсы qt в python.
      Параметры, как у build_app
    """
    tmp_filename = "{}.py".format(a_app_info.app_name)

    with open(a_main_filename, encoding='utf8') as main_py:
        with open(tmp_filename, "w", encoding='utf8') as compile_main:
            for line in main_py:
                if not ("ui_to_py" in line):
                    compile_main.write(line)

    try:
        build_app(
            tmp_filename,
            a_app_info,
            a_icon_filename,
            a_noconsole,
            a_one_file,
            a_admin,
            a_libs,
            dist_path,
            spec_path,
            build_path,
            version_file_path,
            a_hidden_import,
            a_collect_all,
        )
    finally:
        os.remove(tmp_filename)
