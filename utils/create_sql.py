# create_sql.py
# 15-06-2023

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QTableView
from PyQt5.QtWidgets import QFormLayout, QDialog, QMessageBox, QLineEdit, QLabel
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt5.QtCore import Qt
from add_employee import AddEmployeeWindow
#from del_employee import DeleteEmployeeDialog
from datetime import datetime
import csv
import sys


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.db = QSqlDatabase.addDatabase('QSQLITE', 'MainWindow')
        self.db.setDatabaseName('employees.db')
        if not self.db.open():
            print("Не удалось открыть базу данных")

        # Создание таблицы, если она еще не существует
        query = QSqlQuery(self.db)
        if self.db.isOpen():
            query.exec_(
                """
                CREATE TABLE IF NOT EXISTS employees (
                    id TEXT PRIMARY KEY,
                    full_name TEXT,
                    department TEXT,
                    email TEXT,
                    phone TEXT,
                    birthday TEXT
                )
                """
            )
        else:
            print("База данных не открыта")

        # Создание модели данных и настройка ее параметров
        self.model = QSqlTableModel(self, self.db)
        self.model.setTable("employees")
        self.model.select()

        # Инициализируем UI
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Регистрация сотрудников учета рабочего времени")
        self.resize(650, 480)

        # Создание виджета QTableView и связывание его с моделью данных
        self.table_view = QTableView()
        self.table_view.setModel(self.model)

        # Создание кнопок для добавления новых сотрудников и генерации отчетов
        self.add_employee_button = QPushButton("Добавить сотрудника")
        self.delete_employee_button = QPushButton("Удалить запись по ID")
        self.generate_report_button = QPushButton("Сгенерировать отчет")

        # Привязка сигналов кнопок к соответствующим слотам
        self.add_employee_button.clicked.connect(self.open_add_employee_window)
        self.delete_employee_button.clicked.connect(self.delete_employee)
        self.generate_report_button.clicked.connect(self.generate_report)

        # Размещение виджетов в вертикальном layout
        layout = QVBoxLayout()
        # layout = QFormLayout()
        layout.addWidget(self.table_view)
        layout.addWidget(self.add_employee_button)
        layout.addWidget(self.delete_employee_button)
        layout.addWidget(self.generate_report_button)

        # Установка layout в центральный виджет
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        # self.setLayout(layout)

        # Получаем геометрию экрана
        screen_geometry = QApplication.desktop().availableGeometry()
        # Получаем геометрию окна
        window_geometry = self.frameGeometry()
        # Устанавливаем центр окна в центр экрана
        window_geometry.moveCenter(screen_geometry.center())
        # Добавляем смещение: отодвигаем окно вверх на 50 пикселей
        window_geometry.moveTop(window_geometry.top() - 50)
        # Перемещаем главное окно по этим координатам
        self.move(window_geometry.topLeft())


    def open_add_employee_window(self):
        self.add_employee_window = AddEmployeeWindow(self.db, self)
        if self.add_employee_window.exec_():
            self.model.select()


    def delete_employee(self):
        # Получаем id сотрудника, который нужно удалить
        # employee_id = self.id_input.text()
        dialog = DeleteEmployeeDialog(self.db, self)
        employee_id = None
        if dialog.exec_() == QDialog.Accepted:
            employee_id = dialog.id_input.text()

        # Проверяем, что база данных открыта
        if not self.db.isOpen():
            print("База данных не открыта")
            return

        if not employee_id:
            QMessageBox.warning(self, "Ошибка", "Поле 'ID' обязательно для заполнения.")
            return

        # Проверка существования сотрудника с указанным ID
        check_query = QSqlQuery()
        check_query.prepare("SELECT * FROM employees WHERE id = ?")
        check_query.addBindValue(employee_id)
        check_query.exec_()
        if not check_query.next():
            QMessageBox.warning(self, "Ошибка", "Сотрудника с указанным ID не существует.")
            return


        # Создаем и выполняем запрос на удаление
        query = QSqlQuery()
        query.prepare("DELETE FROM employees WHERE id = ?")
        query.addBindValue(employee_id)

        if not query.exec_():
            print("Ошибка при удалении сотрудника:", query.lastError().text())
        else:
            QMessageBox.information(self, "Удаление сотрудника", f"Сотрудник {employee_id} удален.")
            self.model.select()


    def generate_report(self):
        # Проверяем, что база данных открыта
        if not self.db.isOpen():
            print("База данных не открыта")
            return

        # Получаем данные из базы данных
        self.model.setTable("employees")
        self.model.select()

        # Создаем имя файла
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = f"{timestamp}.csv"

        # Записываем данные в файл CSV
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            headers = [self.model.headerData(i, Qt.Horizontal) for i in range(self.model.columnCount())]
            writer.writerow(headers)
            for row in range(self.model.rowCount()):
                rowdata = []
                for column in range(self.model.columnCount()):
                    item = self.model.data(self.model.index(row, column))
                    rowdata.append(item)
                writer.writerow(rowdata)

        QMessageBox.information(self, "Генерация отчета", f"Отчет успешно сохранен в файл {filename}.")

    # Функция closeEvent в PyQt5 вызывается, когда происходит событие 
    # закрытия виджета (в данном случае окна). Это может произойти, например, 
    # при нажатии на кнопку закрытия окна или при вызове метода close() виджета.
    # В итоге, функция closeEvent обеспечивает корректное закрытие соединения с 
    # базой данных и затем позволяет стандартному коду PyQt5 обработать событие закрытия окна.
    def closeEvent(self, event):
        # Закрываем соединение с базой данных, которое было открыто в этом объекте. Это важно делать 
        # перед закрытием приложения, чтобы освободить ресурсы, связанные с соединением с базой данных.
        #self.db.close()
        # Эта строка вызывает реализацию closeEvent в родительском классе виджета. 
        # В PyQt5 все виджеты наследуются от базового класса QWidget, который содержит стандартную реализацию 
        # некоторых функций, включая closeEvent. Это нужно, чтобы дать возможность стандартному коду PyQt5 обработать 
        # событие закрытия, например, сохранить положение и размер окна или выполнить другие операции по очистке.
        #super().closeEvent(event)
        self.db.close()
        QSqlDatabase.removeDatabase('MainWindow')
        event.accept()

class DeleteEmployeeDialog(QDialog):
    def __init__(self, db, parent=None):
        super(DeleteEmployeeDialog, self).__init__(parent)

        self.db = db

        # Инициализируем UI
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Удаление записи сотрудника")

        self.id_input = QLineEdit()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Отмена")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Введите ID сотрудника для удаления:"))
        layout.addWidget(self.id_input)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
