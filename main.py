import sys

from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QComboBox, \
    QMessageBox, QScrollArea

from WordCloud import fetch_url_content_selenium, generate_wordcloud, fetch_contents_from_urls


class CustomComboBox(QComboBox):
    def __init__(self, placeholder, *args, **kwargs):
        super(CustomComboBox, self).__init__(*args, **kwargs)
        self.placeholder = placeholder
        self.addItem(self.placeholder)  # Add placeholder as the first item
        self.isPlaceholderVisible = True  # Flag to track placeholder visibility

    def mousePressEvent(self, event: QMouseEvent):
        if self.isPlaceholderVisible:  # Check if the placeholder is visible
            self.removeItem(0)  # Remove the placeholder item
            self.isPlaceholderVisible = False  # Update the flag
        super(CustomComboBox, self).mousePressEvent(event)  # Call the base class event

    def showPopup(self):
        if self.count() == 0:  # If all items are removed, re-add the placeholder before showing the popup
            self.addItem(self.placeholder)
            self.isPlaceholderVisible = True
        super(CustomComboBox, self).showPopup()  # Show the dropdown list

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)  # container에 QVBoxLayout을 사용

        # Font Selector with title
        self.layout.addWidget(QLabel("글자폰트:"))  # 폰트 선택 섹션의 타이틀 추가
        self.fontSelector = CustomComboBox("Font", self)
        self.fontSelector.addItem("나눔고딕", QVariant("NanumGothic"))
        self.fontSelector.addItem("나눔명조-옛한글", QVariant("NanumMyeongjo-YetHangul"))
        self.fontSelector.addItem("나눔손글씨펜", QVariant("NanumPen"))
        self.fontSelector.addItem("나눔손글씨붓", QVariant("NanumBrush"))
        self.layout.addWidget(self.fontSelector)

        # Base Image Selector with title
        self.layout.addWidget(QLabel("배경 이미지:"))  # 기본 이미지 선택 섹션의 타이틀 추가
        self.baseImageSelector = CustomComboBox("Base Image", self)
        self.baseImageSelector.addItems(["거북이", "고래", "나비", "두뇌", "말", "부엉이", "새", "코끼리"])
        self.layout.addWidget(self.baseImageSelector)

        # URL Input List with title
        self.layout.addWidget(QLabel("사이트 주소:"))  # URL 입력 섹션의 타이틀 추가
        self.urlLayout = QVBoxLayout()
        self.layout.addLayout(self.urlLayout)
        self.addUrlInput()

        # Exclude Word Input List with title
        self.layout.addWidget(QLabel("제외시킬 단어:"))  # 제외할 단어 입력 섹션의 타이틀 추가
        self.excludeWordLayout = QVBoxLayout()
        self.layout.addLayout(self.excludeWordLayout)
        self.addExcludeWordInput()

        # Training Word Input List with title
        self.layout.addWidget(QLabel("학습시킬 단어:"))  # 학습할 단어 입력 섹션의 타이틀 추가
        self.trainWordLayout = QVBoxLayout()
        self.layout.addLayout(self.trainWordLayout)
        self.addTrainWordInput()

        # Submit Button
        self.submitButton = QPushButton('Submit', self)
        self.layout.addWidget(self.submitButton)
        self.submitButton.clicked.connect(self.onSubmit)

        # QScrollArea 설정
        self.scrollArea = QScrollArea(self)  # 현재 인스턴스를 부모로 하는 QScrollArea 생성
        self.scrollArea.setWidgetResizable(True)  # 스크롤 영역의 크기 조정 가능하도록 설정
        self.scrollArea.setWidget(self.container)  # 스크롤 영역에 컨테이너 위젯을 설정

        # 메인 윈도우의 레이아웃 설정
        mainLayout = QVBoxLayout(self)  # 메인 윈도우의 레이아웃
        mainLayout.addWidget(self.scrollArea)  # 스크롤 영역을 메인 레이아웃에 추가

        self.setGeometry(300, 300, 850, 400)  # 윈도우의 위치와 크기 설정
        self.setWindowTitle('WordCloud Maker')  # 윈도우 타이틀 설정
        self.show()
    def addUrlInput(self):
        urlLayout = QHBoxLayout()
        urlInput = QLineEdit(self)
        addButton = QPushButton("Add URL", self)
        addButton.clicked.connect(self.addUrlInput)  # Connect the click event to addUrlInput function
        deleteButton = QPushButton("Delete", self)
        deleteButton.clicked.connect(lambda: self.deleteInput(urlLayout, self.urlLayout))
        addButton.setFixedSize(150,30)

        urlInput.setFixedSize(500, 30)  # Example: 200 width and 30 height
        urlInput.setPlaceholderText("Enter URL here")

        urlLayout.addWidget(urlInput)
        urlLayout.addWidget(addButton)
        urlLayout.addWidget(deleteButton)
        self.urlLayout.addLayout(urlLayout)

    def addExcludeWordInput(self):
        wordLayout = QHBoxLayout()
        wordInput = QLineEdit(self)
        addButton = QPushButton("Add Exclude Word", self)
        addButton.clicked.connect(self.addExcludeWordInput)  # Connect the click event to addExcludeWordInput function
        deleteButton = QPushButton("Delete", self)
        deleteButton.clicked.connect(lambda: self.deleteInput(wordLayout, self.excludeWordLayout))
        addButton.setFixedSize(150,30)


        wordInput.setFixedSize(500, 30)  # Use the same dimensions as for the URL input
        wordInput.setPlaceholderText("Enter exclude word here")

        wordLayout.addWidget(wordInput)
        wordLayout.addWidget(addButton)
        wordLayout.addWidget(deleteButton)
        self.excludeWordLayout.addLayout(wordLayout)


    def addTrainWordInput(self):
        wordLayout = QHBoxLayout()
        wordInput = QLineEdit(self)
        addButton = QPushButton("Add Train Word", self)
        addButton.clicked.connect(self.addTrainWordInput)  # Connect the click event to addUrlInput function
        deleteButton = QPushButton("Delete", self)
        deleteButton.clicked.connect(lambda: self.deleteInput(wordLayout, self.trainWordLayout))
        addButton.setFixedSize(150,30)

        wordInput.setFixedSize(500, 30)  # Example: 200 width and 30 height
        wordInput.setPlaceholderText("Enter train word here")

        wordLayout.addWidget(wordInput)
        wordLayout.addWidget(addButton)
        wordLayout.addWidget(deleteButton)
        self.trainWordLayout.addLayout(wordLayout)

    def onFontChanged(self, index):
        # 사용자가 "Font" 이외의 항목을 선택하면 동작하는 함수
        if index != 0:  # 첫 번째 항목("Font")이 아니라면
            print("Font 선택됨:", self.fontSelector.currentText())

    def onBaseImageChanged(self, index):
        # 사용자가 "BaseImage" 이외의 항목을 선택하면 동작하는 함수
        if index != 0:  # 첫 번째 항목("BaseImage")이 아니라면
            print("BaseImage 선택됨:", self.baseImageSelector.currentText())

    def onFontChanged(self, index):
        if index > 0:  # Assuming the first item is the placeholder
            # Remove placeholder if not already removed
            if self.fontSelector.itemText(0) == "Select Font":
                self.fontSelector.removeItem(0)

    # Handle the case if needed, for example, if the user can deselect a font

    def onBaseImageChanged(self, index):
        if index > 0:  # Assuming the first item is the placeholder
            # Remove placeholder if not already removed
            if self.baseImageSelector.itemText(0) == "Select Base Image":
                self.baseImageSelector.removeItem(0)

    def deleteInput(self, inputLayout, parentLayout):
        # Check if this is the last input field
        if parentLayout.count() <= 1:
            QMessageBox.warning(self, "Warning", "At least one input must exist.")
        else:
            for i in reversed(range(inputLayout.count())):
                item = inputLayout.itemAt(i)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            parentLayout.removeItem(inputLayout)

    def onSubmit(self):
        # Assuming you've validated input as before...

        # Collect URLs from the GUI
        urls = [self.urlLayout.itemAt(i).layout().itemAt(0).widget().text() for i in range(self.urlLayout.count())]

        # Collect exclude words from the GUI
        exclude_words = [self.excludeWordLayout.itemAt(i).layout().itemAt(0).widget().text() for i in
                         range(self.excludeWordLayout.count())]

        train_words = [self.trainWordLayout.itemAt(i).layout().itemAt(0).widget().text() for i in
                         range(self.trainWordLayout.count())]

        if self.fontSelector.currentText() == "Font":
            # Show a warning message
            QMessageBox.warning(self, "Warning", "Please select a font.")
            return

            # Check if base image is selected
        if self.baseImageSelector.currentText() == "Base Image":            # Show a warning message
            QMessageBox.warning(self, "Warning", "Please select a base image.")
            return

        # Check if any URL is empty
        url_count = self.urlLayout.count()
        has_at_least_one_url = False
        for i in range(url_count):
            url = self.urlLayout.itemAt(i).layout().itemAt(0).widget().text()
            if url:
                has_at_least_one_url = True
                break

        if not has_at_least_one_url:
            # Show a warning message
            QMessageBox.warning(self, "Warning", "Please enter at least one URL.")
            return


        # Process each URL
        all_content = fetch_contents_from_urls(urls)

        if all_content:
            # Assuming 'font' and 'baseImage' are selected by the user in the GUI
            font = self.fontSelector.itemData(self.fontSelector.currentIndex())
            baseImage = self.baseImageSelector.currentText()
            print(font)
            print(baseImage)
            # Generate word cloud
            wordcloud_result = generate_wordcloud(all_content, font, baseImage, exclude_words,train_words)

            print(wordcloud_result["tags"])
            # Here, you can also update the GUI to show the generated word cloud image or the path to it



if __name__ == '__main__':
    app = QApplication([])
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())