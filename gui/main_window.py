import cv2

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QLabel,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
)

from camera.scanner import QRScanner
from lookup.csv_loader import CSVLoader


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Receipt Verifier")
        self.resize(900, 700)

        self.loader = None
        self.scanner = None
        self.last_booking = ""

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        layout = QVBoxLayout()

        # ---------------- CSV ----------------

        csv_layout = QHBoxLayout()

        self.csv_path = QLineEdit()
        self.csv_path.setPlaceholderText("Select Delivery Register CSV...")

        browse = QPushButton("Browse")
        browse.clicked.connect(self.browse_csv)

        csv_layout.addWidget(self.csv_path)
        csv_layout.addWidget(browse)

        layout.addLayout(csv_layout)

        # ---------------- Start ----------------

        self.start = QPushButton("Start Scanning")
        self.start.clicked.connect(self.start_camera)

        layout.addWidget(self.start)

        # ---------------- Camera ----------------

        self.camera = QLabel("Camera Feed")
        self.camera.setFixedSize(800, 450)
        self.camera.setAlignment(Qt.AlignCenter)
        self.camera.setStyleSheet("border:2px solid black;")

        layout.addWidget(self.camera)

        # ---------------- Results ----------------

        self.booking = QLabel("Booking No : -")
        self.consumer = QLabel("Consumer No : -")
        self.customer = QLabel("Customer : -")
        self.mobile = QLabel("Mobile : -")

        self.status = QLabel("Status : Waiting...")
        self.status.setStyleSheet("font-size:18px;font-weight:bold;color:blue;")

        layout.addWidget(self.booking)
        layout.addWidget(self.consumer)
        layout.addWidget(self.customer)
        layout.addWidget(self.mobile)
        layout.addWidget(self.status)

        self.setLayout(layout)

    def browse_csv(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Choose CSV",
            "",
            "CSV Files (*.csv)"
        )

        if filename:

            self.csv_path.setText(filename)

            self.loader = CSVLoader(filename)
            self.loader.load()

            self.status.setText("Status : CSV Loaded")
            self.status.setStyleSheet(
                "font-size:18px;font-weight:bold;color:green;"
            )

    def start_camera(self):

        if self.loader is None:

            self.status.setText("Status : Load CSV First")
            self.status.setStyleSheet(
                "font-size:18px;font-weight:bold;color:red;"
            )

            return

        self.scanner = QRScanner(camera=1)

        self.timer.start(30)

    def update_frame(self):

        frame, booking_no = self.scanner.get_frame()

        if frame is None:
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w, ch = rgb.shape

        image = QImage(
            rgb.data,
            w,
            h,
            ch * w,
            QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(image)

        self.camera.setPixmap(
            pixmap.scaled(
                self.camera.size(),
                Qt.KeepAspectRatio
            )
        )

        if not booking_no:
            return

        if booking_no == self.last_booking:
            return

        self.last_booking = booking_no

        self.booking.setText(f"Booking No : {booking_no}")

        result = self.loader.find_booking(booking_no)

        if result:

            self.consumer.setText(
                f"Consumer No : {result['consumer']}"
            )

            self.customer.setText(
                f"Customer : {result['name']}"
            )

            self.mobile.setText(
                f"Mobile : {result['mobile']}"
            )

            self.status.setText("Status : ✅ FOUND")

            self.status.setStyleSheet(
                "font-size:18px;font-weight:bold;color:green;"
            )

        else:

            self.consumer.setText("Consumer No : -")
            self.customer.setText("Customer : -")
            self.mobile.setText("Mobile : -")

            self.status.setText("Status : ❌ NOT FOUND")

            self.status.setStyleSheet(
                "font-size:18px;font-weight:bold;color:red;"
            )