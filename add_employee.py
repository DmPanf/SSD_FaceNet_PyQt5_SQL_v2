# 15-06-2023
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QApplication, QFormLayout
from PyQt5.QtSql import QSqlQuery, QSqlDatabase
import sys

class AddEmployeeWindow(QDialog):
    def __init__(self, db, parent=None):
        super(AddEmployeeWindow, self).__init__(parent)

        # Сохраняем объект QSqlDatabase для дальнейшего использования
        self.db = db

        # Инициализируем UI
        self.initUI()

        # Подключаемся к базе данных и получаем новый ID для сотрудника
        query = QSqlQuery()
        query.exec_("SELECT max(id) FROM employees")
        max_id = None
        while query.next():
            max_id = query.value(0)
        self.id = int(max_id) + 1 if max_id and max_id.isdigit() else 1  # self.id = int(max_id) + 1 if max_id is not None else 1

        # Задаем новый ID уже после self.initUI()
        self.id_input.setText(str(self.id))


    def initUI(self):
        self.setWindowTitle("Добавить нового сотрудника")
        
        # Создание полей для ввода информации о сотруднике
        self.id_label = QLabel("ID:")
        self.full_name_label = QLabel("ФИО:")
        self.department_label = QLabel("Отдел:")
        self.email_label = QLabel("Эл. почта:")
        self.mobile_label = QLabel("Мобильный:")
        self.birthday_label = QLabel("Дата рождения:")

        self.id_input = QLineEdit()
        self.full_name_input = QLineEdit()
        self.department_input = QLineEdit()
        self.email_input = QLineEdit()
        self.mobile_input = QLineEdit()
        self.birthday_input = QLineEdit()

        # Создание кнопки для сохранения нового сотрудника в базе
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.add_employee)

        # Размещение виджетов в вертикальном layout
        layout = QFormLayout()
        layout.addRow(self.id_label, self.id_input)
        layout.addRow(self.full_name_label, self.full_name_input)
        layout.addRow(self.department_label, self.department_input)
        layout.addRow(self.email_label, self.email_input)
        layout.addRow(self.mobile_label, self.mobile_input)
        layout.addRow(self.birthday_label, self.birthday_input)
        layout.addWidget(self.save_button)
        self.setLayout(layout)


    def add_employee(self):
        if not self.db.isOpen():
            print("База данных не открыта")
            return

        # Добавляем сотрудника в базу данных
        full_name = self.full_name_input.text()
        if not full_name:
            QMessageBox.warning(self, "Ошибка", "Поле 'ФИО' обязательно для заполнения.")
            return

        # ... получение остальных данных ...
        department = self.department_input.text()
        email = self.email_input.text()
        phone = self.mobile_input.text()
        my_id = self.id_input.text()
        birthday = self.birthday_input.text()


        query = QSqlQuery()
        query.prepare("""
            INSERT INTO employees (id, full_name, department, email, phone, birthday)
            VALUES (?, ?, ?, ?, ?, ?)
        """)
        query.addBindValue(my_id)
        query.addBindValue(full_name)
        query.addBindValue(department)
        query.addBindValue(email)
        query.addBindValue(phone)
        query.addBindValue(birthday)

        if not query.exec_():
            print("Ошибка при добавлении сотрудника:", query.lastError().text())
            return

        self.accept()
        QMessageBox.information(self, "Добавление сотрудника", f"Сотрудник {self.full_name_input.text()} добавлен.")


    # Функция closeEvent в PyQt5 вызывается, когда происходит событие 
    # закрытия виджета (в данном случае окна). Это может произойти, например, 
    # при нажатии на кнопку закрытия окна или при вызове метода close() виджета.
    # В итоге, функция closeEvent обеспечивает корректное закрытие соединения с 
    # базой данных и затем позволяет стандартному коду PyQt5 обработать событие закрытия окна.
    def closeEvent(self, event):
        # Закрываем соединение с базой данных, которое было открыто в этом объекте. Это важно делать 
        # перед закрытием приложения, чтобы освободить ресурсы, связанные с соединением с базой данных.
        self.db.close()
        # Эта строка вызывает реализацию closeEvent в родительском классе виджета. 
        # В PyQt5 все виджеты наследуются от базового класса QWidget, который содержит стандартную реализацию 
        # некоторых функций, включая closeEvent. Это нужно, чтобы дать возможность стандартному коду PyQt5 обработать 
        # событие закрытия, например, сохранить положение и размер окна или выполнить другие операции по очистке.
        super().closeEvent(event)

    # В отличие от closeEvent, метод __del__ не связан с закрытием виджета, и будет вызван независимо от того, было ли окно
    # закрыто или нет. Например, он будет вызван, если вы удаляете объект окна или если программа полностью завершается.
    # def __del__(self):
    #    self.db.close()
    #    QSqlDatabase.removeDatabase('AddEmployeeConnection')


#if __name__ == "__main__":
#    app = QApplication([])
#    # Создаем QSqlDatabase, указываем имя базы данных и открываем ее
#    db = QSqlDatabase.addDatabase('QSQLITE', 'AddEmployeeConnection')
#    db.setDatabaseName('employees.db')
#    if not db.open():
#        print("Не удалось открыть базу данных")
#    window = AddEmployeeWindow(db)
#    window.show()
#    ret = app.exec_()
#    # Закрытие и удаление подключения к базе данных при выходе из приложения
#    db.close()
#    QSqlDatabase.removeDatabase('AddEmployeeConnection')
#    sys.exit(ret)
