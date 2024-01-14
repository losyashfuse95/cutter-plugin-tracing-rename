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
        self.name_vars={}
        cutter.core().refreshAll.connect(self.plugin.create_json)
        cutter.core().refreshAll.connect(self.plugin.first_load_to_json)
        cutter.core().refreshAll.connect(self.plugin.update_function_data)
        cutter.core().functionRenamed.connect(self.plugin.update_function_data)


        self.table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  
        self.table_widget.cellChanged.connect(self.on_cell_changed)
        self.table_widget.itemDoubleClicked.connect(self.item_double_clicked)

    def populate_table_with_function_data(self, function_data):
        self.table_widget.setRowCount(0)
        self.table_widget.cellChanged.disconnect(self.on_cell_changed)

        for data in function_data:
            row = None
            offset = data.get("offset", "-")
            original_name = data.get("old_name", "")
            new_name = data.get("new_name", "-")

            row = self.find_row_with_offset(offset,original_name)
            new_vars = list(data.get("new_local_variables", "-"))
            old_vars = list(data.get("old_local_variables", "-"))
            


            if row is not None and row[1]==1:
                table_item_offset = QTableWidgetItem(f'{hex(offset)}')
                table_item_offset.setFlags(table_item_offset.flags() & ~Qt.ItemIsEditable)
                table_item_original_name = QTableWidgetItem(original_name)
                table_item_original_name.setFlags(table_item_original_name.flags() & ~Qt.ItemIsEditable)
                table_item_new_name = QTableWidgetItem(new_name)


                # Create a button and set it in the third column
                restore_button = QPushButton("Restore Name")
                restore_button.clicked.connect(self.restore_name_clicked)

                self.table_widget.setCellWidget(row[0], 3, restore_button)
                self.table_widget.setItem(row[0], 0, table_item_offset)
                self.table_widget.setItem(row[0], 1, table_item_original_name)
                self.table_widget.setItem(row[0], 2, table_item_new_name)

            elif original_name != new_name:
                row = self.table_widget.rowCount()
                self.table_widget.insertRow(row)
                table_item_offset = QTableWidgetItem(f'{hex(offset)}')
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
            
            for i in range (len(new_vars)):
                if new_vars[i] != old_vars[i]:
                    row = self.find_row_with_offset(offset,old_vars[i])
                    self.name_vars[old_vars[i]] = new_vars[i]

                    if row is not None and row[1]==0:
                        table_item_offset = QTableWidgetItem(f'vars-{hex(offset)}')
                        table_item_offset.setFlags(table_item_offset.flags() & ~Qt.ItemIsEditable)
                        table_item_original_name_vars = QTableWidgetItem(old_vars[i])
                        table_item_original_name_vars.setFlags(table_item_original_name_vars.flags() & ~Qt.ItemIsEditable)
                        table_item_new_name_vars = QTableWidgetItem(new_vars[i])


                        # Create a button and set it in the third column
                        restore_button = QPushButton("Restore Name")
                        restore_button.clicked.connect(self.restore_name_clicked)

                        self.table_widget.setCellWidget(row[0], 3, restore_button)
                        self.table_widget.setItem(row[0], 0, table_item_offset)
                        self.table_widget.setItem(row[0], 1, table_item_original_name_vars)
                        self.table_widget.setItem(row[0], 2, table_item_new_name_vars)
                

                    else:
                        row = self.table_widget.rowCount()
                        self.table_widget.insertRow(row)
                        table_item_offset = QTableWidgetItem(f'vars-{hex(offset)}')
                        table_item_offset.setFlags(table_item_offset.flags() & ~Qt.ItemIsEditable)
                        table_item_original_name_vars = QTableWidgetItem(old_vars[i])
                        table_item_original_name_vars.setFlags(table_item_original_name_vars.flags() & ~Qt.ItemIsEditable)
                        table_item_new_name_vars = QTableWidgetItem(new_vars[i])

                        # Create a button and set it in the third column
                        restore_button = QPushButton("Restore Name")
                        restore_button.clicked.connect(self.restore_name_clicked)
                        self.table_widget.setCellWidget(row, 3, restore_button)
                        self.table_widget.setItem(row, 0, table_item_offset)
                        self.table_widget.setItem(row, 1, table_item_original_name_vars)
                        self.table_widget.setItem(row, 2, table_item_new_name_vars)
                        # continue
        self.table_widget.cellChanged.connect(self.on_cell_changed)
            

    def on_cell_changed(self, row, column):
        self.table_widget.cellChanged.disconnect(self.on_cell_changed)
        if column == 2:  # Проверяем, что изменение произошло в столбце New Name
            if len(self.table_widget.item(row, 0).text().split("-")) == 2:
                item = self.table_widget.item(row, column)
                offset = int(self.table_widget.item(row, 0).text().split("-")[-1], 16)  # Получаем offset из пользовательских данных
                new_name = item.text()  # Получаем новое имя
                cutter.cmd(f"s {offset}")
                old_name = self.table_widget.item(row, 1).text()
                cutter.cmd(f"afvn {new_name} {self.name_vars[old_name]}")
                self.update_name_vars_in_json(offset, new_name)
            else:
                item = self.table_widget.item(row, column)
                offset = int(self.table_widget.item(row, 0).text(), 16)  # Получаем offset из пользовательских данных
                new_name = item.text()  # Получаем новое имя
                cutter.cmd(f"s {offset}")
                cutter.cmd(f"afn {new_name}")
                self.update_name_in_json(offset, new_name)

               

        self.table_widget.cellChanged.connect(self.on_cell_changed)

    def restore_name_clicked(self):
        button = self.sender()
        if button: 
            row = self.table_widget.indexAt(button.pos()).row()
            if len(self.table_widget.item(row, 0).text().split("-")) == 2:
                offset = int(self.table_widget.item(row, 0).text().split("-")[-1], 16)
                old_name = self.table_widget.item(row, 1).text()
                new_name = self.table_widget.item(row, 2).text()
                cutter.cmd(f"s {offset}")
                cutter.cmd(f"afvn {old_name} {new_name}")
                self.table_widget.removeRow(row)
                self.update_name_vars_in_json(offset, old_name)
                cutter.refresh()
            else:
                offset = int(self.table_widget.item(row, 0).text().split("-")[-1], 16)
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

    def update_name_vars_in_json(self, offset, old_name):
        uid = cutter.cmdj("ij")  
        project_guid = uid["bin"]["guid"]
        current_dir = os.path.dirname(__file__)
        self.file_path = os.path.join(current_dir, f"renamed_functions{project_guid}.json")
        with open(self.file_path, 'r') as file:
            data = json.load(file)

        for item in data:
            if item["offset"] == offset:
                for index, vars in enumerate(old_name):
                    if vars == old_name:
                        item["new_local_variables"][index] = old_name
        with open(self.file_path, 'w') as file:
            json.dump(data, file) 

    def find_row_with_offset(self, offset, original_name):
        for row in range(self.table_widget.rowCount()):
            if self.table_widget.item(row, 0).text() == hex(offset) and self.table_widget.item(row, 1).text() == original_name:
                return [row,1]
            elif self.table_widget.item(row, 0).text() == f'vars-{hex(offset)}' and self.table_widget.item(row, 1).text() == original_name:
                return [row,0]
                
        return None

    def set_table_width(self):
        header = self.table_widget.horizontalHeader()  
        header.setSectionResizeMode(0, QHeaderView.Stretch)  
        header.setSectionResizeMode(1, QHeaderView.Stretch)  
        header.setSectionResizeMode(2, QHeaderView.Stretch)  


    def item_double_clicked(self, item):
        if item.column() == 0:  # проверяем, что событие произошло в колонке с адресом
            address = int(item.text().split("-")[-1], 16)
            cutter.cmd(f"s {hex(address)}") 


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
                local_variables = cutter.cmdj(f"afvj @ {function['offset']}")
                local_variables_name = [var['name'] for var in local_variables.get('stack', [])]
                if entry["offset"] == function["offset"]:
                    entry["offset"] = function["offset"]
                    entry["new_name"] = function["name"]
                    entry["new_local_variables"] = local_variables_name

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