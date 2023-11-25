import cutter
import json
import os
from PySide2.QtCore import Qt

from PySide2.QtWidgets import QAction, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QVBoxLayout, QWidget, QSizePolicy, QHeaderView

class MyDockWidget(cutter.CutterDockWidget):
    def __init__(self, parent, action, plugin):
        super(MyDockWidget, self).__init__(parent, action)
        self.plugin = plugin
        self.setObjectName("MyDockWidget")  
        self.setWindowTitle("My cool DockWidget") 

        layout = QVBoxLayout()  
        self.table_widget = QTableWidget()  
        self.table_widget.setColumnCount(4)  
        self.table_widget.setHorizontalHeaderLabels(["Address function", "Original Name", "New Name", ""])  
        self.set_table_width() 
        layout.addWidget(self.table_widget)  

        self.setWidget(QWidget(self))  
        self.widget().setLayout(layout)  

        cutter.core().refreshAll.connect(self.plugin.create_json)
        cutter.core().refreshAll.connect(self.plugin.first_load_to_json)
        cutter.core().functionRenamed.connect(self.plugin.update_function_data)

        self.table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  

    def populate_table_with_function_data(self, function_data):
        for data in function_data:
            offset = data.get("offset", "-")
            original_name = data.get("old_name", "")
            new_name = data.get("new_name", "-")

            row = self.find_row_with_offset(offset)


            if row is not None:
                table_item_offset = QTableWidgetItem(hex(offset))
                table_item_offset.setFlags(table_item_offset.flags() & ~Qt.ItemIsEditable)
                table_item_original_name = QTableWidgetItem(original_name)
                table_item_original_name.setFlags(table_item_original_name.flags() & ~Qt.ItemIsEditable)
                table_item_new_name = QTableWidgetItem(new_name)


                # Create a button and set it in the third column
                restore_button = QPushButton("Restore Name")
                restore_button.clicked.connect(self.restore_name_clicked)

                self.table_widget.setCellWidget(row, 3, restore_button)
                self.table_widget.setItem(row, 0, table_item_offset)
                self.table_widget.setItem(row, 1, table_item_original_name)
                self.table_widget.setItem(row, 2, table_item_new_name)


            elif original_name != new_name:
                row = self.table_widget.rowCount()
                self.table_widget.insertRow(row)
                table_item_offset = QTableWidgetItem(hex(offset))
                table_item_offset.setFlags(table_item_offset.flags() & ~Qt.ItemIsEditable)
                table_item_original_name = QTableWidgetItem(original_name)
                table_item_original_name.setFlags(table_item_original_name.flags() & ~Qt.ItemIsEditable)
                table_item_new_name = QTableWidgetItem(new_name)

                # Create a button and set it in the third column
                restore_button = QPushButton("Restore Name")
                restore_button.clicked.connect(self.restore_name_clicked)
                self.table_widget.setCellWidget(row, 3, restore_button)
                self.table_widget.setItem(row, 0, table_item_offset)
                self.table_widget.setItem(row, 1, table_item_original_name)
                self.table_widget.setItem(row, 2, table_item_new_name)


    def on_cell_changed(self, row, column):
        self.table_widget.cellChanged.disconnect(self.on_cell_changed)
        
        if column == 2:  # Проверяем, что изменение произошло в столбце New Name
            item = self.table_widget.item(row, column)
            offset = int(self.table_widget.item(row, 0).text(), 16)  # Получаем offset из пользовательских данных
            new_name = item.text()  # Получаем новое имя
            cutter.cmd(f"s {offset}")
            cutter.cmd(f"afn {new_name}")
            self.update_name_in_json(offset, new_name)
            cutter.refresh()

        self.table_widget.cellChanged.connect(self.on_cell_changed)

    def restore_name_clicked(self):
        button = self.sender()
        if button:
            row = self.table_widget.indexAt(button.pos()).row()
            offset = int(self.table_widget.item(row, 0).text(), 16)
            old_name = self.table_widget.item(row, 1).text()
            cutter.cmd(f"s {offset}")
            cutter.cmd(f"afn {old_name}")
            self.update_name_in_json(offset, old_name)
            self.table_widget.removeRow(row)
            cutter.refresh()
            
    def update_name_in_json(self, offset, new_name):
        uid = cutter.cmdj("ij")  
        project_guid = uid["bin"]["guid"]
        current_dir = os.path.dirname(__file__)
        self.file_path = os.path.join(current_dir, f"renamed_functions{project_guid}.json")
        with open(self.file_path, 'r') as file:
            data = json.load(file)

        for item in data:
            if item["offset"] == offset:
                item["new_name"] = new_name

        with open(self.file_path, 'w') as file:
            json.dump(data, file) 


    def find_row_with_offset(self, offset):
        for row in range(self.table_widget.rowCount()):
            if self.table_widget.item(row, 0).text() == hex(offset):
                return row
        return None

    def set_table_width(self):
        header = self.table_widget.horizontalHeader()  
        header.setSectionResizeMode(0, QHeaderView.Stretch)  
        header.setSectionResizeMode(1, QHeaderView.Stretch)  
        header.setSectionResizeMode(2, QHeaderView.Stretch)  
        self.table_widget.cellChanged.connect(self.on_cell_changed)

        self.table_widget.itemDoubleClicked.connect(self.item_double_clicked)  # подключаем событие

    def item_double_clicked(self, item):
        if item.column() == 0:  # проверяем, что событие произошло в колонке с адресом
            address = int(item.text(), 16)  # получаем адрес из ячейки таблицы
            cutter.cmd(f"s {hex(address)}")  # выполняем команду для перехода в дизассемблерное окно


class MyCutterPlugin(cutter.CutterPlugin):
    name = "My Plugin"  
    description = "This plugin does awesome things!" 
    version = "1.0" 
    author = "1337 h4x0r" 
    widget = None

    def setupPlugin(self):
        pass

    def update_function_data(self):
        with open(self.file_path, 'r') as file:
            data = json.load(file)
        functions = cutter.cmdj("aflj")
        for entry in data:
            for function in functions:
                if entry["offset"] == function["offset"]:
                    entry["offset"] = function["offset"]
                    entry["new_name"] = function["name"]
        self.add_to_json(self.file_path, data)
        self.load_data_from_json(self.file_path)

    def create_json(self):
        uid = cutter.cmdj("ij")  
        project_guid = uid["bin"]["guid"]
        current_dir = os.path.dirname(__file__)
        self.file_path = os.path.join(current_dir, f"renamed_functions{project_guid}.json")
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as file:
                json.dump([], file)  

    def first_load_to_json (self):

        uid = cutter.cmdj("ij")  
        project_guid = uid["bin"]["guid"]
        current_dir = os.path.dirname(__file__)
        self.file_path = os.path.join(current_dir, f"renamed_functions{project_guid}.json")
        with open(self.file_path, 'r') as file:
            data = json.load(file)
            if data == []:
                function_data = self.get_function_data()
                self.add_to_json(self.file_path, function_data)
            self.load_data_from_json(self.file_path)

    def get_function_data(self):
        functions = cutter.cmdj("aflj")  
        filtered_data = []  
        for function in functions:
            local_variables = cutter.cmdj(f"afvj @ {function['offset']}")
            local_variables_name = [var['name'] for var in local_variables.get('stack', [])]

            filtered_function = {
                "offset": function["offset"],  
                "new_name": function["name"],  
                "old_name":  function["name"],
                "new_local_variables": local_variables_name,
                "old_local_variables": local_variables_name
            }
            filtered_data.append(filtered_function)  
        return filtered_data

    def add_to_json(self, file_path, data):
        with open(file_path, 'w') as file:
            json.dump(data, file)

    def load_data_from_json(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            if self.widget:
                self.widget.populate_table_with_function_data(data)

    def setupInterface(self, main):
        action = QAction("My Plugin", main)  
        action.setCheckable(True)  
        self.widget = MyDockWidget(main, action, self)
        main.addPluginDockWidget(self.widget, action)  

    def terminate(self):
        pass  

def create_cutter_plugin():
    return MyCutterPlugin()