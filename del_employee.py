# del_employee.py
# 15-06-2023

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

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
    #    QSqlDatabase.removeDatabase("QSQLITE")  # Или имя подключения базы
