# IRSPY LIBRARY

IrsPy - python библиотека от ИРС

## Разработчикам

**Установка зависимостей**

```cmd
python -m pip install -r requirements.txt
```

**Сборка пакета**

```cmd
python -m build
```

### Установка пакета пользователем

**Локально**

```cmd
python -m pip install .\dist\irspy-0.0.1-py3-none-any.whl
```

**Из GitHub**

```cmd
python -m pip install git+https://github.com/irsural/irspy.git@master#egg=irspy
```

При повторном вызове команды для GitHub, обновление пакета не произойдет. Для обновления необходимо удалить пакет и выполнить установку заного. 

**Удаление пакета**

```cmd
python -m pip uninstall irspy
```