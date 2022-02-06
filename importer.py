"""Импортер для шифрованных файлов с исходным кодом.
"""

import sys
import imp
import os

from abc import ABC, abstractmethod


class AbstractDecoder(ABC):
    @abstractmethod
    def decode(a_input_file: str) -> str:
        return NotImplemented


class CustomImporter:
    """Служит для поиска и импорта python-модулей, шифрованных с помощью AES

    Класс реализует Import Protocol (PEP 302) для возможности импортирования
    модулей, зашифрованных в ASE из указанного пакета.
    """

    def __init__(self, a_decoder: AbstractDecoder, a_root_package_path: str, a_ext='.tmp'):
        """
        Args:
            a_decoder (AbstractDecoder): Декодер, который дешифрует модули питона
            a_root_package_path (str): Путь до модуля
            a_ext (str, optional): Расширение файлов, подлежащих дешифрации. Defaults to '.tmp'.
        """

        self.__ext = a_ext
        self.__decoder = a_decoder
        self.__modules_info = self.__collect_modules_info(a_root_package_path)


    def find_module(self, fullname, _=None):
        """Метод будет вызван при импорте модулей

        Если модуль с именем fullname является AES и находится в заданной
        папке, данный метод вернёт экземпляр импортёра (finder), либо None, если
        модуль не является AES.
        """

        if fullname in self.__modules_info:
            return self
        return None

    def load_module(self, fullname):
        """Метод загружает AES модуль

        Если модуль с именем fullname является AES, то метод попытается его
        загрузить. Возбуждает исключение ImportError в случае любой ошибки.
        """

        if fullname not in self.__modules_info:
            raise ImportError(fullname)

        # Для потокобезопасности
        imp.acquire_lock()

        try:
            mod = sys.modules.setdefault(fullname, imp.new_module(fullname))

            mod.__file__ = "<{}>".format(self.__class__.__name__)
            mod.__loader__ = self

            if self.is_package(fullname):
                mod.__path__ = []
                mod.__package__ = fullname
            else:
                mod.__package__ = fullname.rpartition('.')[0]

            src = self.get_source(fullname)

            try:
                exec(src, mod.__dict__)
            except Exception as ex:
                del sys.modules[fullname]
                raise ex
        finally:
            imp.release_lock()

        return mod

    def is_package(self, fullname):
        """Возвращает True если fullname является пакетом
        """

        return self.__modules_info[fullname]['ispackage']

    def get_source(self, fullname):
        """Возвращает исходный код модуля fullname в виде строки

        Метод дешифрует исходные коды из AES
        """

        filename = self.__modules_info[fullname]['filename']
        return self.__decoder.decode(filename)

    def __collect_modules_info(self, root_package_path):
        """Собирает информацию о модулях из указанного пакета
        """

        modules = {}

        p = os.path.abspath(root_package_path)
        dir_name = os.path.dirname(p) + os.sep

        for root, _, files in os.walk(p):
            # Информация о текущем пакете
            filename = os.path.join(root, '__init__' + self.__ext)
            p_fullname = root.rpartition(dir_name)[2].replace(os.sep, '.')

            modules[p_fullname] = {
                'filename': filename,
                'ispackage': True
            }

            # Информация о модулях в текущем пакете
            for f in files:
                if not f.endswith(self.__ext):
                    continue

                filename = os.path.join(root, f)
                fullname = '.'.join([p_fullname, os.path.splitext(f)[0]])

                modules[fullname] = {
                    'filename': filename,
                    'ispackage': False
                }

        modules = dict(sorted(modules.items(), key=lambda item: item[0]))
        return modules

