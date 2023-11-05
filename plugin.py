import cutter
import json
import os

from PySide2.QtWidgets import QAction, QTableWidget, QTableWidgetItem, QLineEdit, QVBoxLayout, QWidget, QSizePolicy, QHeaderView

class MyDockWidget(cutter.CutterDockWidget):
    def __init__(self, parent, action, plugin):
        super(MyDockWidget, self).__init__(parent, action)
        self.plugin = plugin
        self.setObjectName("MyDockWidget")  
        self.setWindowTitle("My cool DockWidget") 

        layout = QVBoxLayout()  
        self.table_widget = QTableWidget()  
        self.table_widget.setColumnCount(3)  
        self.table_widget.setHorizontalHeaderLabels(["Address", "New Name", "Original Name"])  
        self.set_table_width() 
        layout.addWidget(self.table_widget)  

        self.setWidget(QWidget(self))  
        self.widget().setLayout(layout)  

        self.table_widget.itemClicked.connect(self.on_item_clicked)  
        cutter.core().functionRenamed.connect(self.plugin.update_function_data)
        cutter.core().refreshAll.connect(self.plugin.first_load_to_json)
        self.table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  

    def populate_table_with_function_data(self, function_data):
        for data in function_data:
            offset = data.get("offset", "-")
            original_name = data.get("new_name", "-")
            new_name = data.get("old_name", "")  
            
            row = self.find_row_with_offset(offset)

            if row is not None:
                table_item_original_name = QTableWidgetItem(original_name)
                table_item_new_name = QTableWidgetItem(new_name)
                self.table_widget.setItem(row, 1, table_item_original_name)
                self.table_widget.setItem(row, 2, table_item_new_name)
            elif original_name!= new_name:
                row = self.table_widget.rowCount()
                self.table_widget.insertRow(row)
                table_item_offset = QTableWidgetItem(hex(offset))
                table_item_original_name = QTableWidgetItem(original_name)
                table_item_new_name = QTableWidgetItem(new_name)  
                self.table_widget.setItem(row, 0, table_item_offset)
                self.table_widget.setItem(row, 1, table_item_original_name)
                self.table_widget.setItem(row, 2, table_item_new_name)

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

    def on_item_clicked(self, item):
        if item.column() == 2: 
            line_edit = QLineEdit(item.text())  
            line_edit.editingFinished.connect(lambda: self.update_new_name(item.row(), line_edit.text()))  
            self.table_widget.setCellWidget(item.row(), item.column(), line_edit)  

    def update_new_name(self, row, new_name):
        item = QTableWidgetItem(new_name)
        self.table_widget.setItem(row, 2, item)  

class MyCutterPlugin(cutter.CutterPlugin):
    name = "My Plugin"  
    description = "This plugin does awesome things!" 
    version = "1.0" 
    author = "1337 h4x0r" 
    widget = None

    def setupPlugin(self):
        current_dir = os.path.dirname(__file__)
        self.file_path = os.path.join(current_dir, "renamed_functions.json")
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as file:
                json.dump([], file)  

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


    def first_load_to_json (self):
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, "renamed_functions.json")
        with open(file_path, 'r') as file:
            data = json.load(file)
            if data == []:
                function_data = self.get_function_data()
                self.add_to_json(self.file_path, function_data)
            self.load_data_from_json(self.file_path)

    def get_function_data(self):
        functions = cutter.cmdj("aflj")  
        filtered_data = []  
        for function in functions:
            filtered_function = {
                "offset": function["offset"],  
                "new_name": function["name"],  
                "old_name":  function["name"],  
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