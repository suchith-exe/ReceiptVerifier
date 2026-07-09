import cv2

from datetime import datetime
import winsound
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
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
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

        # ---------------- Manual Search ----------------

        search_layout = QHBoxLayout()

        self.manual_booking = QLineEdit()
        self.manual_booking.setPlaceholderText("Enter Booking Number")

        search_button = QPushButton("Search")

        search_button.clicked.connect(self.manual_search)
        self.manual_booking.returnPressed.connect(self.manual_search)

        search_layout.addWidget(self.manual_booking)
        search_layout.addWidget(search_button)

        layout.addLayout(search_layout)

        # ---------------- Start ----------------

        self.start = QPushButton("Start Scanning")
        self.start.clicked.connect(self.start_camera)

        layout.addWidget(self.start)

        # ---------------- Counter ----------------

        self.unique_bookings = set()

        self.counter = QLabel("Unique Receipts Scanned : 0")
        self.counter.setStyleSheet("font-size:18px;font-weight:bold;")

        layout.addWidget(self.counter)

        self.found_count = 0
        self.not_found_count = 0

        self.total_records = 0

        self.found_label = QLabel("Found : 0")
        self.not_found_label = QLabel("Not Found : 0")
        self.remaining_label = QLabel("Remaining : 0")

        layout.addWidget(self.found_label)
        layout.addWidget(self.not_found_label)  
        layout.addWidget(self.remaining_label)

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

        self.status = QLabel("WAITING")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setFixedHeight(55)

        self.status.setStyleSheet("""
        QLabel{
            background-color: #f1c40f;
            color: black;
            font-size: 20px;
            font-weight: bold;
            border-radius: 8px;
        }
        """)

        layout.addWidget(self.booking)
        layout.addWidget(self.consumer)
        layout.addWidget(self.customer)
        layout.addWidget(self.mobile)
        layout.addWidget(self.status)

        # ---------------- History ----------------

        history_title = QLabel("Scan History")
        history_title.setStyleSheet(
         "font-size:18px;font-weight:bold;"
        )

        layout.addWidget(history_title)

        self.history = QTableWidget()

        self.history.setColumnCount(4)

        self.history.setHorizontalHeaderLabels(
            [
                "Time",
                "Booking",
                "Customer",
                "Status",
            ]
        )

        self.history.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layout.addWidget(self.history)


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
            
            self.total_records = len(self.loader.database)

            self.remaining_label.setText(
                f"Remaining : {self.total_records}"
            )

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

        self.unique_bookings.add(booking_no)

        previous = len(self.unique_bookings)

        self.unique_bookings.add(booking_no)

        current = len(self.unique_bookings)

        self.counter.setText(
            f"Unique Receipts Scanned : {current}"
        )

        if current > previous:

            self.found_count += 1

            self.found_label.setText(
                f"Found : {self.found_count}"
            )

            remaining = self.total_records - self.found_count

            self.remaining_label.setText(
                f"Remaining : {remaining}"
            )

        self.booking.setText(f"Booking No : {booking_no}")

        result = self.loader.find_booking(booking_no)

        if result:
            self.show_result(booking_no, result)
        else:
            self.show_not_found(booking_no)        


    def manual_search(self):

        booking = self.manual_booking.text().strip().upper()

        if not booking:
            return

        result = self.loader.find_booking(booking)

        if result:

            self.show_result(booking, result)

        else:

            self.show_not_found(booking)

        self.manual_booking.clear()


    def show_result(self, booking_no, result):

        previous = len(self.unique_bookings)

        self.unique_bookings.add(booking_no)

        current = len(self.unique_bookings)

        self.counter.setText(
            f"Unique Receipts Scanned : {current}"
        )

        if current > previous:
            self.found_count += 1

            self.found_label.setText(
                f"Found : {self.found_count}"
            )

            remaining = self.total_records - self.found_count

            self.remaining_label.setText(
                f"Remaining : {remaining}"
            )

        self.booking.setText(
            f"Booking : {booking_no}"
        )

        self.consumer.setText(
            f"Consumer : {result['consumer']}"
        )

        self.customer.setText(
            f"Customer : {result['name']}"
        )

        self.status.setText("✅ FOUND")

        self.status.setStyleSheet("""
        QLabel{
            background-color: #2ecc71;
            color: white;
            font-size: 20px;
            font-weight: bold;
            border-radius: 8px;
        }
        """)

        import winsound
        winsound.Beep(1200,150)

        self.add_history_row(
            booking_no,
            result["name"],
            "FOUND"
        )

    def show_not_found(self, booking_no):

        self.not_found_count += 1

        self.not_found_label.setText(
            f"Not Found : {self.not_found_count}"
        )

        self.booking.setText(
            f"Booking : {booking_no}"
        )

        self.consumer.setText("Consumer : -")
        self.customer.setText("Customer : -")

        self.status.setText("❌ NOT FOUND")

        self.status.setStyleSheet("""
        QLabel{
            background-color: #e74c3c;
            color: white;
            font-size: 20px;
            font-weight: bold;
            border-radius: 8px;
        }
        """)

        import winsound
        winsound.Beep(500,300)

        self.add_history_row(
            booking_no,
            "-",
            "NOT FOUND"
        )


    def add_history_row(
        self,
        booking,
        customer,
        status,
    ):

        self.history.insertRow(0)

        if self.history.rowCount() > 5:
            self.history.removeRow(5)

        self.history.setItem(
            0,
            0,
            QTableWidgetItem(
                datetime.now().strftime("%H:%M:%S")
            ),
        )

        self.history.setItem(
            0,
            1,
            QTableWidgetItem(booking),
        )

        self.history.setItem(
            0,
            2,
            QTableWidgetItem(customer),
        )

        self.history.setItem(
            0,
            3,
            QTableWidgetItem(status),
        )