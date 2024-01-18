# Импорт необходимых модулей и классов
import cutter  # Модуль для взаимодействия с Cutter
import json  # Модуль для работы с форматом данных JSON
import os  # Модуль для работы с функциями операционной системы
from PySide2.QtCore import (
    Qt,
)  # Импорт класса Qt для работы с элементами пользовательского интерфейса
from PySide2.QtWidgets import (
    QAction,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
    QHeaderView,
)

# Определение класса MyDockWidget, унаследованного от cutter.CutterDockWidget
class MyDockWidget(cutter.CutterDockWidget):
    def __init__(self, parent, action, plugin):
        # Вызов конструктора базового класса с передачей родительского элемента и действия
        super(MyDockWidget, self).__init__(parent, action)
        # Связывание плагина с виджетом
        self.plugin = plugin
        self.setObjectName("MyDockWidget")
        self.setWindowTitle("My cool DockWidget")
        # Создание вертикального layout'а
        layout = QVBoxLayout()
        # Создание QTableWidget для отображения данных
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(
            ["Address function", "Original Name", "New Name", ""]
        )
        self.set_table_width()
        layout.addWidget(self.table_widget)
        # Установка виджета для DockWidget
        self.setWidget(QWidget(self))
        self.widget().setLayout(layout)
        # Словарь для хранения новых имен переменных
        self.name_vars = {}
        # Подключение сигналов и слотов
        cutter.core().refreshAll.connect(self.plugin.create_json)
        cutter.core().refreshAll.connect(self.plugin.first_load_to_json)
        cutter.core().refreshAll.connect(self.plugin.update_function_data)
        cutter.core().functionRenamed.connect(self.plugin.update_function_data)
        # Настройка QTableWidget
        self.table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table_widget.cellChanged.connect(self.on_cell_changed)
        self.table_widget.itemDoubleClicked.connect(self.item_double_clicked)

    # Метод для заполнения таблицы данными о функциях и их локальных переменных
    def populate_table_with_function_data(self, function_data):
        # Очистка таблицы перед заполнением новыми данными
        self.table_widget.setRowCount(0)
        # TODO Данная строка позволяет отключить коннект к вызову self.on_cell_changed (к событию изменения ячейки в таблице)
        # Если не использовать данную строку, то при переименовании более одной функции или локальной переменной происходит зависание приложения
        # Предположительно, данная проблема связана с возникновением бесконечной рекурсии
        self.table_widget.cellChanged.disconnect(
            self.on_cell_changed
        )  # TODO попробовать blocksignal
        # Итерация по данным о функциях и их переменных
        for data in function_data:
            row = None
            offset = data.get("offset", "-")
            original_name = data.get("old_name", "")
            new_name = data.get("new_name", "-")
            # Поиск строки в таблице по адресу и оригинальному имени функции
            row = self.find_row_with_offset(offset, original_name)
            new_vars = list(data.get("new_local_variables", "-"))
            old_vars = list(data.get("old_local_variables", "-"))
            # Логика обновления таблицы для имен функций
            if row is not None and row[1] == 1:
                table_item_offset = QTableWidgetItem(f"{hex(offset)}")
                table_item_offset.setFlags(
                    table_item_offset.flags() & ~Qt.ItemIsEditable
                )
                table_item_original_name = QTableWidgetItem(original_name)
                table_item_original_name.setFlags(
                    table_item_original_name.flags() & ~Qt.ItemIsEditable
                )
                table_item_new_name = QTableWidgetItem(new_name)
                # Создание кнопки "Restore Name" и ее подключение к соответствующему слоту
                restore_button = QPushButton("Restore Name")
                restore_button.clicked.connect(self.restore_name_clicked)
                # Установка кнопки в третий столбец таблицы
                self.table_widget.setCellWidget(row[0], 3, restore_button)
                self.table_widget.setItem(row[0], 0, table_item_offset)
                self.table_widget.setItem(row[0], 1, table_item_original_name)
                self.table_widget.setItem(row[0], 2, table_item_new_name)
            # Логика обновления таблицы для имен переменных
            elif original_name != new_name:
                row = self.table_widget.rowCount()
                self.table_widget.insertRow(row)
                table_item_offset = QTableWidgetItem(f"{hex(offset)}")
                table_item_offset.setFlags(
                    table_item_offset.flags() & ~Qt.ItemIsEditable
                )
                table_item_original_name = QTableWidgetItem(original_name)
                table_item_original_name.setFlags(
                    table_item_original_name.flags() & ~Qt.ItemIsEditable
                )
                table_item_new_name = QTableWidgetItem(new_name)
                # Создание кнопки "Restore Name" и ее подключение к соответствующему слоту
                restore_button = QPushButton("Restore Name")
                restore_button.clicked.connect(self.restore_name_clicked)
                # Установка кнопки в третий столбец таблицы
                self.table_widget.setCellWidget(row, 3, restore_button)
                self.table_widget.setItem(row, 0, table_item_offset)
                self.table_widget.setItem(row, 1, table_item_original_name)
                self.table_widget.setItem(row, 2, table_item_new_name)
            # Логика обновления таблицы для имен переменных
            for i in range(len(new_vars)):
                if new_vars[i] != old_vars[i]:
                    row = self.find_row_with_offset(offset, old_vars[i])
                    self.name_vars[old_vars[i]] = new_vars[i]
                    # Логика обновления таблицы для имен переменных
                    if row is not None and row[1] == 0:
                        table_item_offset = QTableWidgetItem(f"vars-{hex(offset)}")
                        table_item_offset.setFlags(
                            table_item_offset.flags() & ~Qt.ItemIsEditable
                        )
                        table_item_original_name_vars = QTableWidgetItem(old_vars[i])
                        table_item_original_name_vars.setFlags(
                            table_item_original_name_vars.flags() & ~Qt.ItemIsEditable
                        )
                        table_item_new_name_vars = QTableWidgetItem(new_vars[i])
                        # Создание кнопки "Restore Name" и ее подключение к соответствующему слоту
                        restore_button = QPushButton("Restore Name")
                        restore_button.clicked.connect(self.restore_name_clicked)
                        # Установка кнопки в третий столбец таблицы
                        self.table_widget.setCellWidget(row[0], 3, restore_button)
                        self.table_widget.setItem(row[0], 0, table_item_offset)
                        self.table_widget.setItem(
                            row[0], 1, table_item_original_name_vars
                        )
                        self.table_widget.setItem(row[0], 2, table_item_new_name_vars)
                    # Логика обновления таблицы для имен переменных
                    else:
                        row = self.table_widget.rowCount()
                        self.table_widget.insertRow(row)
                        table_item_offset = QTableWidgetItem(f"vars-{hex(offset)}")
                        table_item_offset.setFlags(
                            table_item_offset.flags() & ~Qt.ItemIsEditable
                        )
                        table_item_original_name_vars = QTableWidgetItem(old_vars[i])
                        table_item_original_name_vars.setFlags(
                            table_item_original_name_vars.flags() & ~Qt.ItemIsEditable
                        )
                        table_item_new_name_vars = QTableWidgetItem(new_vars[i])
                        # Создание кнопки "Restore Name" и ее подключение к соответствующему слоту
                        restore_button = QPushButton("Restore Name")
                        restore_button.clicked.connect(self.restore_name_clicked)
                        # Установка кнопки в третий столбец таблицы
                        self.table_widget.setCellWidget(row, 3, restore_button)
                        self.table_widget.setItem(row, 0, table_item_offset)
                        self.table_widget.setItem(row, 1, table_item_original_name_vars)
                        self.table_widget.setItem(row, 2, table_item_new_name_vars)
         # TODO Подключение слота on_cell_changed к событию изменения ячейки в таблице
        self.table_widget.cellChanged.connect(self.on_cell_changed)


    # Слот для обработки изменения ячейки таблицы
    def on_cell_changed(self, row, column):
        # Прерываем временно соединение, чтобы избежать рекурсивных вызовов
        self.table_widget.cellChanged.disconnect(self.on_cell_changed)
        # Проверяем, что изменение произошло в столбце New Name
        if column == 2:
            if len(self.table_widget.item(row, 0).text().split("-")) == 2:
                # Получаем offset из пользовательских данных
                offset = int(self.table_widget.item(row, 0).text().split("-")[-1], 16)
                # Получаем новое имя
                new_name = self.table_widget.item(row, column).text()
                # Переходим к адресу в Cutter
                cutter.cmd(f"s {offset}")
                old_name = self.table_widget.item(row, 1).text()
                # Выполняем команду Cutter для переименования функции с учетом нового имени
                cutter.cmd(f"afvn {new_name} {self.name_vars[old_name]}")
                # Обновляем информацию в JSON-файле
                self.update_name_vars_in_json(offset, new_name)
            else:
                # Получаем offset из пользовательских данных
                offset = int(self.table_widget.item(row, 0).text(), 16)
                # Получаем новое имя
                new_name = self.table_widget.item(row, column).text()
                # Переходим к адресу в Cutter
                cutter.cmd(f"s {offset}")
                # Выполняем команду Cutter для переименования функции
                cutter.cmd(f"afn {new_name}")
                # Обновляем информацию в JSON-файле
                self.update_name_in_json(offset, new_name)
        # Подключаем снова сигнал к слоту после выполнения обработки
        self.table_widget.cellChanged.connect(self.on_cell_changed)

    # Слот для восстановления исходного имени
    def restore_name_clicked(self):
        # Получаем объект, инициировавший сигнал
        button = self.sender()
        # Проверяем, что объект существует
        if button:
            # Получаем номер строки в таблице, по которой был произведен клик
            row = self.table_widget.indexAt(button.pos()).row()
            # Проверяем, что клик произошел в колонке с адресом
            if len(self.table_widget.item(row, 0).text().split("-")) == 2:
                # Получаем offset из пользовательских данных
                offset = int(self.table_widget.item(row, 0).text().split("-")[-1], 16)
                old_name = self.table_widget.item(row, 1).text()
                new_name = self.table_widget.item(row, 2).text()
                # Переходим к адресу в Cutter
                cutter.cmd(f"s {offset}")
                # Восстанавливаем исходное имя функции в Cutter
                cutter.cmd(f"afvn {old_name} {new_name}")
                # Удаляем строку из таблицы
                self.table_widget.removeRow(row)
                # Обновляем информацию в JSON-файле
                self.update_name_vars_in_json(offset, old_name)
                # Обновляем отображение в Cutter
                cutter.refresh()
            else:
                # Получаем offset из пользовательских данных
                offset = int(self.table_widget.item(row, 0).text().split("-")[-1], 16)
                old_name = self.table_widget.item(row, 1).text()
                # Переходим к адресу в Cutter
                cutter.cmd(f"s {offset}")
                # Восстанавливаем исходное имя функции в Cutter
                cutter.cmd(f"afn {old_name}")
                # Удаляем строку из таблицы
                self.table_widget.removeRow(row)
                # Обновляем отображение в Cutter
                cutter.refresh()

    # Метод для обновления имени в JSON-файле
    def update_name_in_json(self, offset, new_name):
        # Получаем уникальный идентификатор проекта в Cutter
        uid = cutter.cmdj("ij")
        # Извлекаем GUID проекта
        project_guid = uid["bin"]["guid"]
        # Получаем текущую директорию, где находится скрипт
        current_dir = os.path.dirname(__file__)
        # Формируем путь к JSON-файлу с данными о переименованных функциях
        self.file_path = os.path.join(
            current_dir, f"renamed_functions{project_guid}.json"
        )
        # Открываем файл для чтения
        with open(self.file_path, "r") as file:
            data = json.load(file)
        # Обновляем имя в соответствующем объекте данных в JSON
        for item in data:
            if item["offset"] == offset:
                item["new_name"] = new_name
        # Записываем обновленные данные в JSON-файл
        with open(self.file_path, "w") as file:
            json.dump(data, file)

    # Метод для обновления имен переменных в JSON-файле
    def update_name_vars_in_json(self, offset, old_name):
        # Получаем уникальный идентификатор проекта в Cutter
        uid = cutter.cmdj("ij")
        # Извлекаем GUID проекта
        project_guid = uid["bin"]["guid"]
        # Получаем текущую директорию, где находится скрипт
        current_dir = os.path.dirname(__file__)
        # Формируем путь к JSON-файлу с данными о переименованных функциях
        self.file_path = os.path.join(
            current_dir, f"renamed_functions{project_guid}.json"
        )
        # Открываем файл для чтения
        with open(self.file_path, "r") as file:
            data = json.load(file)
        # Обновляем имена переменных в соответствующем объекте данных в JSON
        for item in data:
            if item["offset"] == offset:
                for index, var in enumerate(item["old_local_variables"]):
                    if var == old_name:
                        item["new_local_variables"][index] = old_name
        # Записываем обновленные данные в JSON-файл
        with open(self.file_path, "w") as file:
            json.dump(data, file)

    # Метод для поиска строки с заданным смещением и именем
    def find_row_with_offset(self, offset, original_name):
        # Проходим по всем строкам таблицы
        for row in range(self.table_widget.rowCount()):
            # Проверяем, совпадают ли смещение и исходное имя в заданной строке
            if (
                self.table_widget.item(row, 0).text() == hex(offset)
                and self.table_widget.item(row, 1).text() == original_name
            ):
                # Возвращаем информацию о строке и типе (1 для функций, 0 для переменных)
                return [row, 1]
            # Проверяем, совпадают ли смещение и исходное имя в заданной строке, но с префиксом 'vars-'
            elif (
                self.table_widget.item(row, 0).text() == f"vars-{hex(offset)}"
                and self.table_widget.item(row, 1).text() == original_name
            ):
                # Возвращаем информацию о строке и типе (1 для функций, 0 для переменных)
                return [row, 0]
        # Если совпадений не найдено, возвращаем None
        return None

    # Метод для установки ширины столбцов в таблице
    def set_table_width(self):
        # Получаем горизонтальный заголовок таблицы
        header = self.table_widget.horizontalHeader()
        # Устанавливаем режим изменения размеров для каждого столбца
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

    # Слот для обработки двойного щелчка по элементу
    def item_double_clicked(self, item):
        # Проверяем, что событие произошло в колонке с адресом (столбец 0)
        if item.column() == 0:
            # Извлекаем адрес из текста ячейки и преобразуем его в число
            address = int(item.text().split("-")[-1], 16)
            # Переходим к указанному адресу в Cutter
            cutter.cmd(f"s {hex(address)}")


# Определение класса MyCutterPlugin, унаследованного от cutter.CutterPlugin
class MyCutterPlugin(cutter.CutterPlugin):

    # Определение основных свойств плагина
    name = "My Plugin"
    description = "This plugin does awesome things!"
    version = "1.0"
    author = "1337 h4x0r"
    widget = None

    def setupPlugin(self):
        pass

    # Метод для обновления данных о функциях
    def update_function_data(self):
        # Открываем файл JSON для чтения
        with open(self.file_path, "r") as file:
            data = json.load(file)
        # Получаем данные о функциях из Cutter
        functions = cutter.cmdj("aflj")
        # Обновляем информацию о функциях в данных плагина
        for entry in data:
            for function in functions:
                # Получаем локальные переменные для каждой функции
                local_variables = cutter.cmdj(f"afvj @ {function['offset']}")
                local_variables_name = [
                    var["name"] for var in local_variables.get("stack", [])
                ]
                # Если найдено совпадение по смещению, обновляем данные
                if entry["offset"] == function["offset"]:
                    entry["offset"] = function["offset"]
                    entry["new_name"] = function["name"]
                    entry["new_local_variables"] = local_variables_name
        # Обновляем JSON-файл
        self.add_to_json(self.file_path, data)
        self.load_data_from_json(self.file_path)

    # Метод для создания JSON-файла при первом запуске
    def create_json(self):
        # Получаем уникальный идентификатор проекта в Cutter
        uid = cutter.cmdj("ij")
        # Извлекаем GUID проекта
        project_guid = uid["bin"]["guid"]
        # Получаем текущую директорию, где находится скрипт
        current_dir = os.path.dirname(__file__)
        # Формируем путь к JSON-файлу с данными о переименованных функциях
        self.file_path = os.path.join(
            current_dir, f"renamed_functions{project_guid}.json"
        )
        # Проверяем, существует ли файл, и если нет, создаем его с пустым массивом данных
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as file:
                json.dump([], file)

    # Метод для первоначальной загрузки данных из JSON-файла
    def first_load_to_json(self):
        # Получаем уникальный идентификатор проекта в Cutter
        uid = cutter.cmdj("ij")
        # Извлекаем GUID проекта
        project_guid = uid["bin"]["guid"]
        # Получаем текущую директорию, где находится скрипт
        current_dir = os.path.dirname(__file__)
        # Формируем путь к JSON-файлу с данными о переименованных функциях
        self.file_path = os.path.join(
            current_dir, f"renamed_functions{project_guid}.json"
        )
        # Открываем файл JSON для чтения
        with open(self.file_path, "r") as file:
            data = json.load(file)
            # Если данные пусты, выполняем первоначальную загрузку
            if data == []:
                function_data = self.get_function_data()
                self.add_to_json(self.file_path, function_data)
            # Загружаем данные из JSON-файла
            self.load_data_from_json(self.file_path)

    # Метод для получения данных о функциях
    def get_function_data(self):
        # Получаем список функций из Cutter
        functions = cutter.cmdj("aflj")
        # Инициализируем пустой список для отфильтрованных данных
        filtered_data = []
        # Обходим каждую функцию и получаем информацию о локальных переменных
        for function in functions:
            local_variables = cutter.cmdj(f"afvj @ {function['offset']}")
            local_variables_name = [
                var["name"] for var in local_variables.get("stack", [])
            ]
            # Формируем словарь с данными о функции и локальных переменных
            filtered_function = {
                "offset": function["offset"],
                "new_name": function["name"],
                "old_name": function["name"],
                "new_local_variables": local_variables_name,
                "old_local_variables": local_variables_name,
            }
            # Добавляем словарь в список
            filtered_data.append(filtered_function)
        return filtered_data

    # Метод для добавления данных в JSON-файл
    def add_to_json(self, file_path, data):
        # Открываем файл JSON для записи
        with open(file_path, "w") as file:
            # Записываем данные в файл
            json.dump(data, file)

    # Метод для загрузки данных из JSON-файла
    def load_data_from_json(self, file_path):
        # Открываем файл JSON для чтения
        with open(file_path, "r") as file:
            # Загружаем данные из файла
            data = json.load(file)

            # Если виджет существует, вызываем метод для заполнения таблицы данными
            if self.widget:
                self.widget.populate_table_with_function_data(data)

    # Метод для настройки интерфейса плагина в Cutter
    def setupInterface(self, main):
        # Создаем действие для активации плагина
        action = QAction("My Plugin", main)

        # Устанавливаем возможность переключения состояния действия
        action.setCheckable(True)

        # Создаем экземпляр виджета MyDockWidget и добавляем его в главный интерфейс Cutter
        self.widget = MyDockWidget(main, action, self)
        main.addPluginDockWidget(self.widget, action)

    # Метод для завершения работы плагина
    def terminate(self):
        pass

# Функция для создания экземпляра плагина
def create_cutter_plugin():
    return MyCutterPlugin()
