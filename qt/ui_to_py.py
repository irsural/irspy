import hashlib
import json
import os

HASHES_FILE = "hashes.json"


def convert_ui(path_in=".", path_out="."):
    """
    Конвертирует .ui формы из path_in в .py файлы (в path_out)
    :param path_in: Каталог, содержащий .ui формы
    :param path_out: Каталог, в коротом будут создаваться .py файлы
    """
    __convert_gui("pyuic5 {_in} > {_out}", ".ui", ".py", path_in, path_out)


def convert_resources(path_in=".", path_out="."):
    """
    Конвертирует .qrc ресурсы из path_in в .py файлы (в path_out)
    :param path_in: Каталог, содержащий .qrc формы
    :param path_out: Каталог, в коротом будут создаваться .py файлы
    """
    __convert_gui("pyrcc5 {_in} > {_out}", ".qrc", "_rc.py", path_in, path_out)


def __convert_gui(convert_cmd: str, ext_in: str, ext_out: str, path_in=".", path_out="."):
    """
    Конвертирует специальные файлы qt в файлы python. При это вычисляет и сохраняет хэш конвртируемого файла.
    Если хэш совпадает с прошлым и python файл уже существует, то не конвертирует файл
    """
    hashes_path = "{0}/{1}".format(path_in, HASHES_FILE)
    try:
        with open(hashes_path, 'r') as hashes_file:
            hashes = json.load(hashes_file)
    except IOError:
        hashes = {}

    for file in os.listdir(path_in):
        if ext_in in file:
            ui_filename = "{0}/{1}".format(path_in, file)
            ui_current_hash = __get_file_hash(ui_filename)
            ui_prev_hash = "" if ui_filename not in hashes.keys() else hashes[ui_filename]

            py_filename = "{0}/{1}".format(path_out, file.replace(ext_in, ext_out))

            if ui_prev_hash != ui_current_hash or not os.path.isfile(py_filename):
                hashes[ui_filename] = ui_current_hash
                os.system(convert_cmd.format(_in=ui_filename, _out=py_filename))

    with open(hashes_path, 'w') as hashes_file:
        json.dump(hashes, hashes_file)


def create_translate(a_py_files_folder: str, a_ts_file_path: str):
    """
    Создает ts-файлы с помощью pylupdate5 из py-файлов qt-форм. Полученные файлы можно открыть в QtLinguist, чтобы
    сгенерировать qm-файл для QTranslator
    :param a_py_files_folder: Каталог с py-файлами
    :param a_ts_files_folder: Каталог, в который будут помещены ts-файлы
    """
    hashes_path = "{0}/{1}".format(a_py_files_folder, HASHES_FILE)
    try:
        with open(hashes_path, 'r') as hashes_file:
            hashes = json.load(hashes_file)
    except FileNotFoundError:
        hashes = {}

    py_files_list = []
    py_files_changed = False
    for file in os.listdir(a_py_files_folder):
        if file.endswith(".py"):
            py_filename = "{0}/{1}".format(a_py_files_folder, file)
            py_files_list.append(py_filename)

            py_current_hash = __get_file_hash(py_filename)
            py_prev_hash = "" if py_filename not in hashes.keys() else hashes[py_filename]

            if py_prev_hash != py_current_hash or not os.path.isfile(a_ts_file_path):
                hashes[py_filename] = py_current_hash
                py_files_changed = True

    if py_files_changed:
        os.system("pylupdate5 {} -ts {}".format(" ".join(py_files_list), a_ts_file_path))

        with open(hashes_path, 'w') as hashes_file:
            json.dump(hashes, hashes_file)


def __get_file_hash(a_filename):
    with open(a_filename, 'rb') as file:
        return hashlib.md5(file.read()).hexdigest()


if __name__ == "__main__":
    convert_ui("../../ui", "../../ui/py")
    convert_resources("../../resources", "../../")
    # create_translate("../../upms_1v_pc/ui/py", "../../upms_1v_pc/ui/translates")
