import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QDesktopWidget
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QSize
import os

class ImageViewer(QWidget):
    def __init__(self, image_folder, ID='ID.01'):
        super().__init__()
        self.image_folder = image_folder
        self.ID = ID
        self.images = [os.path.join(image_folder, f) for f in sorted(os.listdir(image_folder)) if f.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        self.current_image_index = 0
        # Задаем индекс текущего изображения на основе имени файла вида 'ID.11.jpg'
        initial_image_name = self.ID + '.jpg'
        initial_image_path = os.path.join(self.image_folder, initial_image_name)
        if initial_image_path in self.images:
            self.current_image_index = self.images.index(initial_image_path)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Сотрудники компании "Пилигрим"')

        self.label = QLabel(self)
        self.pixmap = QPixmap(self.images[self.current_image_index])
        self.label.setPixmap(self.pixmap)

        self.first_btn = QPushButton('⏮', self)
        self.first_btn.clicked.connect(self.first_image)

        self.prev_btn = QPushButton('⏪', self)
        self.prev_btn.clicked.connect(self.previous_image)

        self.center_btn = QPushButton('⏺', self)
        self.center_btn.clicked.connect(self.center_image)

        self.next_btn = QPushButton('⏩', self)
        self.next_btn.clicked.connect(self.next_image)

        self.last_btn = QPushButton('⏭', self)
        self.last_btn.clicked.connect(self.last_image)

        self.file_name_edit = QLineEdit(self)
        # self.file_name_edit.setPlaceholderText('ID')
        self.file_name_edit.setPlaceholderText(self.ID)
        self.file_name_edit.returnPressed.connect(self.load_image_by_name)
        self.file_name_edit.setFixedWidth(80)  # Задать ширину виджета

        #print("First button width:", self.first_btn.sizeHint().width())
        #print("Previous button width:", self.prev_btn.sizeHint().width())
        #print("Center button width:", self.center_btn.sizeHint().width())
        #print("Next button width:", self.next_btn.sizeHint().width())
        #print("Last button width:", self.last_btn.sizeHint().width())

        hbox = QHBoxLayout()
        hbox.addWidget(self.first_btn)
        hbox.addWidget(self.prev_btn)
        hbox.addWidget(self.center_btn)
        hbox.addWidget(self.file_name_edit)  # добавляем виджет QLineEdit справа от кнопки "середина"
        hbox.addWidget(self.next_btn)
        hbox.addWidget(self.last_btn)

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.label)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        # Центрировать окно на экране
        self.center()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        window = self.geometry()
        self.move((screen.width() - window.width()) // 2, (screen.height() - window.height()) // 2)

    def first_image(self):
        self.current_image_index = 0
        self.update_image()

    def previous_image(self):
        self.current_image_index -= 1
        if self.current_image_index < 0:
            self.current_image_index = 0
        self.update_image()

    def center_image(self):
        self.current_image_index = len(self.images) // 2
        self.update_image()

    def next_image(self):
        self.current_image_index += 1
        if self.current_image_index >= len(self.images):
            self.current_image_index = len(self.images) - 1
        self.update_image()

    def last_image(self):
        self.current_image_index = len(self.images) - 1
        self.update_image()

    def load_image_by_name(self):
        file_name = self.file_name_edit.text()
        if not file_name:
            return

        file_path = os.path.join(self.image_folder, f"{file_name}.jpg")
        if os.path.exists(file_path):
            self.current_image_index = self.images.index(file_path)
            self.update_image()

    def update_image(self):
        self.pixmap.load(self.images[self.current_image_index])
        self.label.setPixmap(self.pixmap)

        # Выводим размеры виджета для изображения
        # print(f'Image widget width: {self.label.size().width()} x {self.label.size().height()}')

        # Получаем имя файла без расширения и устанавливаем его в виджет QLineEdit
        file_name = os.path.splitext(os.path.basename(self.images[self.current_image_index]))[0]
        self.file_name_edit.setText(file_name)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    image_folder = '/home/bunta/.000/faces.img/Faces.Best'  # замените на путь к вашей папке с изображениями
    id = 'ID.11'
    viewer = ImageViewer(image_folder, id)
    viewer.show()
    sys.exit(app.exec_())
