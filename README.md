# variables.py

Этот файл на языке Python содержит плагин для Cutter, предназначенный для управления и переименования функций в рамках платформы реверс-инжиниринга Cutter. Плагин предоставляет возможность переименовывать функции и отслеживать изменения с использованием графического интерфейса.

## Требования
- **cutter**: Импорт из фреймворка Cutter.
- **json**: Библиотека для работы с данными в формате JSON.
- **os**: Функциональности, связанные с операционной системой.
- **PySide2**: Импорт элементов из PySide2 для компонентов графического интерфейса.

## Использование
Этот плагин создает виджет док-окна внутри Cutter, позволяя пользователям просматривать и управлять именами функций и их изменениями. Вот обзор функционала:

### Класс `MyDockWidget`
- **`__init__(self, parent, action, plugin)`**: Инициализирует виджет док-окна.
- **`populate_table_with_function_data(self, function_data)`**: Заполняет виджет таблицы данными о функциях.
- **`on_cell_changed(self, row, column)`**: Обрабатывает изменения ячеек в таблице.
- **`restore_name_clicked(self)`**: Восстанавливает исходное имя функции по щелчку кнопки.
- **`update_name_in_json(self, offset, new_name)`**: Обновляет имя функции в файле JSON.
- **`find_row_with_offset(self, offset)`**: Находит строку в таблице на основе заданного смещения.
- **`set_table_width(self)`**: Устанавливает ширину столбцов таблицы.
- **`item_double_clicked(self, item)`**: Обрабатывает двойные щелчки по элементам таблицы.

### Класс `MyCutterPlugin`
- **`setupPlugin(self)`**: Настройка плагина (пусто в данной реализации).
- **`update_function_data(self)`**: Обновляет данные о функциях, сравнивая с существующими данными.
- **`create_json(self)`**: Создает файл JSON для хранения данных о функциях, если он не существует.
- **`first_load_to_json(self)`**: Загружает данные в JSON при активации плагина.
- **`get_function_data(self)`**: Получает данные о функциях из фреймворка Cutter.
- **`add_to_json(self, file_path, data)`**: Добавляет данные в файл JSON.
- **`load_data_from_json(self, file_path)`**: Загружает данные из файла JSON в виджет.
- **`setupInterface(self, main)`**: Настраивает интерфейс плагина внутри Cutter.
- **`terminate(self)`**: Останавливает работу плагина (пусто в данной реализации).

### Функция `create_cutter_plugin()`
- **`create_cutter_plugin()`**: Создает и возвращает экземпляр класса `MyCutterPlugin`.

## Инструкции по использованию
1. Разместите файл `variables.py` в соответствующем каталоге плагинов Cutter.
2. Откройте Cutter и активируйте плагин через интерфейс Cutter.
3. Используйте предоставленные элементы графического интерфейса для управления именами функций и их изменениями в рамках Cutter.
