import cutter

from PySide2.QtWidgets import QAction, QTableWidget, QTableWidgetItem, QLineEdit, QVBoxLayout, QWidget, QSizePolicy, QHeaderView
from PySide2.QtCore import QTimer

class MyDockWidget(cutter.CutterDockWidget):
    def __init__(self, parent, action):
        super(MyDockWidget, self).__init__(parent, action)
        self.setObjectName("MyDockWidget")  
        self.setWindowTitle("My cool DockWidget") 

        layout = QVBoxLayout()  # Создание вертикального лэйаута
        self.table_widget = QTableWidget()  # Создание таблицы
        self.table_widget.setColumnCount(3)  # Установка количества столбцов
        self.table_widget.setHorizontalHeaderLabels(["Address", "Original Name", "New Name"])  # Установка заголовков столбцов
        self.update_function_data()
        self.set_table_width() 
        layout.addWidget(self.table_widget)  # Добавление таблицы в лэйаут

        self.setWidget(QWidget(self))  # Установка виджета
        self.widget().setLayout(layout)  # Установка лэйаута для виджета

        self.table_widget.itemClicked.connect(self.on_item_clicked)  # Подключение обработчика события нажатия на элемент таблицы

        self.table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Установка политики размера для таблицы
        self.timer = QTimer(self)  # Создание таймера
        self.timer.timeout.connect(self.update_function_data) 
        self.timer.start(1000) 

    def populate_table_with_function_data(self, function_data):
        self.table_widget.setRowCount(len(function_data))  # Установка количества строк в таблице
        for row, data in enumerate(function_data):
            offset = str(data.get("offset", "-"))
            name = data.get("name", "-")
            size = str(data.get("size", "-"))
            
            table_item_offset = QTableWidgetItem(offset)
            table_item_name = QTableWidgetItem(name)
            table_item_size = QTableWidgetItem(size)
            
            self.table_widget.setItem(row, 0, table_item_offset) 
            self.table_widget.setItem(row, 1, table_item_name) 
            self.table_widget.setItem(row, 2, table_item_size) 

    def update_function_data(self):
        function_data = cutter.cmdj("aflj")  
        self.populate_table_with_function_data(function_data)

    def set_table_width(self):
        header = self.table_widget.horizontalHeader()  # Получение горизонтального заголовка таблицы
        header.setSectionResizeMode(0, QHeaderView.Stretch)  
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Установка растягивающегося режима для столбца 0 1 2
        header.setSectionResizeMode(2, QHeaderView.Stretch)  

    def on_item_clicked(self, item):
        if item.column() == 2: 
            line_edit = QLineEdit(item.text())  # Создание поля ввода с текстом из ячейки
            line_edit.editingFinished.connect(lambda: self.update_new_name(item.row(), line_edit.text()))  # Подключение обработчика завершения редактирования поля ввода
            self.table_widget.setCellWidget(item.row(), item.column(), line_edit)  # Установка поля ввода в ячейку

    def update_new_name(self, row, new_name):
        item = QTableWidgetItem(new_name)
        self.table_widget.setItem(row, 2, item)  # Обновление содержимого ячейки на новое имя

class MyCutterPlugin(cutter.CutterPlugin):
    name = "My Plugin"  
    description = "This plugin does awesome things!" 
    version = "1.0" 
    author = "1337 h4x0r" 

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
