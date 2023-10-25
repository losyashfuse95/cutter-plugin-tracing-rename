import cutter

from PySide2.QtWidgets import QAction, QTableWidget, QTableWidgetItem, QLineEdit, QVBoxLayout, QWidget, QSizePolicy, QHeaderView

class MyDockWidget(cutter.CutterDockWidget):
    def __init__(self, parent, action):
        super(MyDockWidget, self).__init__(parent, action)  # Инициализация родительского класса
        self.setObjectName("MyDockWidget")  # Установка имени для док-виджета
        self.setWindowTitle("My cool DockWidget")  # Установка заголовка для док-виджета

        layout = QVBoxLayout()  # Создание вертикального лэйаута
        self.table_widget = QTableWidget()  # Создание таблицы
        self.table_widget.setColumnCount(3)  # Установка количества столбцов
        self.table_widget.setHorizontalHeaderLabels(["Address", "Original Name", "New Name"])  # Установка заголовков столбцов
        self.populate_table_with_dummy_data()  # Заполнение таблицы фиктивными данными
        self.set_table_width()  # Установка ширины столбцов
        layout.addWidget(self.table_widget)  # Добавление таблицы в лэйаут

        self.setWidget(QWidget(self))  # Установка виджета
        self.widget().setLayout(layout)  # Установка лэйаута для виджета

        self.table_widget.itemClicked.connect(self.on_item_clicked)  # Подключение обработчика события нажатия на элемент таблицы

        self.table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Установка политики размера для таблицы

    def populate_table_with_dummy_data(self):
        dummy_data = [
            ["0x001", "Var_1", "-"],
            ["0x002", "Var_2", "New_Var_2"],
            ["-", "Data_Type", "-"]
        ]
        self.table_widget.setRowCount(len(dummy_data))  # Установка количества строк в таблице
        for row, data in enumerate(dummy_data):
            for col, item in enumerate(data):
                table_item = QTableWidgetItem(item)
                self.table_widget.setItem(row, col, table_item)  # Установка элемента в ячейку таблицы

    def set_table_width(self):
        header = self.table_widget.horizontalHeader()  # Получение горизонтального заголовка таблицы
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Установка растягивающегося режима для столбца 0
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Установка растягивающегося режима для столбца 1
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Установка растягивающегося режима для столбца 2

    def on_item_clicked(self, item):
        if item.column() == 2:  # Проверка, является ли столбец 2
            line_edit = QLineEdit(item.text())  # Создание поля ввода с текстом из ячейки
            line_edit.editingFinished.connect(lambda: self.update_new_name(item.row(), line_edit.text()))  # Подключение обработчика завершения редактирования поля ввода
            self.table_widget.setCellWidget(item.row(), item.column(), line_edit)  # Установка поля ввода в ячейку

    def update_new_name(self, row, new_name):
        item = QTableWidgetItem(new_name)
        self.table_widget.setItem(row, 2, item)  # Обновление содержимого ячейки на новое имя

class MyCutterPlugin(cutter.CutterPlugin):
    name = "My Plugin"  # Имя плагина
    description = "This plugin does awesome things!"  # Описание плагина
    version = "1.0"  # Версия плагина
    author = "1337 h4x0r"  # Автор плагина

    def setupPlugin(self):
        pass  # Метод для инициализации плагина

    def setupInterface(self, main):
        action = QAction("My Plugin", main)  # Создание действия для плагина
        action.setCheckable(True)  # Установка возможности отметки действия
        widget = MyDockWidget(main, action)  # Создание экземпляра виджета
        main.addPluginDockWidget(widget, action)  # Добавление виджета в главное окно

    def terminate(self):
        pass  # Метод для завершения плагина

def create_cutter_plugin():
    return MyCutterPlugin()
