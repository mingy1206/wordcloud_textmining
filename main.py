import sys

from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QComboBox, \
    QMessageBox, QScrollArea
from WordCloud import generate_wordcloud, fetch_contents_from_urls
from jamo import h2j, j2hcj



class CustomComboBox(QComboBox):
    def __init__(self, placeholder, *args, **kwargs):
        super(CustomComboBox, self).__init__(*args, **kwargs)
        self.placeholder = placeholder
        self.addItem(self.placeholder)  # placeholder 첫 번째 항목으로 추가
        self.isPlaceholderVisible = True  # 표시 여부를 추적하는 flag

    def mousePressEvent(self, event: QMouseEvent):
        if self.isPlaceholderVisible:  # placeholder 표시되는지 확인
            self.removeItem(0)  # placeholder 항목 제거
            self.isPlaceholderVisible = False  # flag 업데이트
        super(CustomComboBox, self).mousePressEvent(event)  # event 호출

    def showPopup(self):
        if self.count() == 0:  # 모든 항목이 제거되면 팝업 표시 전에 placeholder 다시 추가
            self.addItem(self.placeholder)
            self.isPlaceholderVisible = True
        super(CustomComboBox, self).showPopup()  # 드롭다운 목록 표시

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
        self.fontSelector.addItem("나눔고딕에코", QVariant("NanumGothicEco"))
        self.fontSelector.addItem("나눔명조", QVariant("NanumMyeongjo"))
        self.fontSelector.addItem("나눔명조에코", QVariant("NanumMyeongjoEco"))
        self.fontSelector.addItem("나눔명조-옛한글", QVariant("NanumMyeongjo-YetHangul"))
        self.fontSelector.addItem("나눔바른고딕", QVariant("NanumBrush"))
        self.fontSelector.addItem("나눔바른팬", QVariant("NanumBarunpenR"))
        self.fontSelector.addItem("나눔손글씨펜", QVariant("NanumPen"))
        self.fontSelector.addItem("나눔손글씨붓", QVariant("NanumBrush"))
        self.fontSelector.addItem("나눔스퀘어", QVariant("NanumSquareR"))



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
        self.createButton = QPushButton('Create', self)
        self.layout.addWidget(self.createButton)
        self.createButton.clicked.connect(self.onSubmit)

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
        addButton.clicked.connect(self.addUrlInput)
        deleteButton = QPushButton("Delete", self)
        deleteButton.clicked.connect(lambda: self.deleteInput(urlLayout, self.urlLayout))
        addButton.setFixedSize(150,30)

        urlInput.setFixedSize(500, 30)
        urlInput.setPlaceholderText("Enter URL here")

        urlLayout.addWidget(urlInput)
        urlLayout.addWidget(addButton)
        urlLayout.addWidget(deleteButton)
        self.urlLayout.addLayout(urlLayout)

    def addExcludeWordInput(self):
        wordLayout = QHBoxLayout()
        wordInput = QLineEdit(self)
        addButton = QPushButton("Add Exclude Word", self)
        addButton.clicked.connect(self.addExcludeWordInput)
        deleteButton = QPushButton("Delete", self)
        deleteButton.clicked.connect(lambda: self.deleteInput(wordLayout, self.excludeWordLayout))
        addButton.setFixedSize(150,30)


        wordInput.setFixedSize(500, 30)
        wordInput.setPlaceholderText("Enter exclude word here")

        wordLayout.addWidget(wordInput)
        wordLayout.addWidget(addButton)
        wordLayout.addWidget(deleteButton)
        self.excludeWordLayout.addLayout(wordLayout)


    def addTrainWordInput(self):
        wordLayout = QHBoxLayout()
        wordInput = QLineEdit(self)
        addButton = QPushButton("Add Train Word", self)
        addButton.clicked.connect(self.addTrainWordInput)
        deleteButton = QPushButton("Delete", self)
        deleteButton.clicked.connect(lambda: self.deleteInput(wordLayout, self.trainWordLayout))
        addButton.setFixedSize(150,30)

        wordInput.setFixedSize(500, 30)
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
        if index > 0:  #  첫 번째 항목이 placeholder라고 가정
            # 제거X -> 제거
            if self.fontSelector.itemText(0) == "Select Font":
                self.fontSelector.removeItem(0)

    # Handle the case if needed, for example, if the user can deselect a font

    def onBaseImageChanged(self, index):
        if index > 0:  #  첫 번째 항목이 placeholder라고 가정
            # 제거X -> 제거
            if self.baseImageSelector.itemText(0) == "Select Base Image":
                self.baseImageSelector.removeItem(0)

    def deleteInput(self, inputLayout, parentLayout):
        # 마지막 필드임을 확인 (1개보다 작은지)
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
        # GUI에서 URL을 수집
        urls = [self.urlLayout.itemAt(i).layout().itemAt(0).widget().text() for i in range(self.urlLayout.count())]

        # GUI에서 제외할 단어를 수집
        exclude_words = [self.excludeWordLayout.itemAt(i).layout().itemAt(0).widget().text() for i in
                         range(self.excludeWordLayout.count())]

        train_words = [self.trainWordLayout.itemAt(i).layout().itemAt(0).widget().text() for i in
                         range(self.trainWordLayout.count())]
        #Check and Warnings
        if self.fontSelector.currentText() == "Font":
            QMessageBox.warning(self, "Warning", "Please select a font.")
            return

            # Check if base image is selected
        if self.baseImageSelector.currentText() == "Base Image":            # Show a warning message
            QMessageBox.warning(self, "Warning", "Please select a base image.")
            return
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


        # URL로 이동 후 데이터 전처리
        all_content = fetch_contents_from_urls(urls)

        if all_content:
            font = self.fontSelector.itemData(self.fontSelector.currentIndex())
            baseImage = self.baseImageSelector.currentText()
            print(font)
            print(baseImage)
            # 워드 클라우드 생성
            generate_wordcloud(all_content, font, baseImage, exclude_words,train_words)
            print("finish!")


if __name__ == '__main__':
    app = QApplication([])
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())