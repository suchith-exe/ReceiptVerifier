import cv2
from lookup.csv_loader import CSVLoader

# Load the CSV once
loader = CSVLoader("data/Delivery Register Report.csv")
loader.load()

last_booking = None

# Open PHONE camera (DroidCam)
cap = cv2.VideoCapture(1)

detector = cv2.QRCodeDetector()

if not cap.isOpened():
    print("Couldn't open camera!")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Detect QR Code
    data, points, _ = detector.detectAndDecode(frame)

    # New QR detected
    if data and data != last_booking:

        last_booking = data

        print("\n==============================")
        print("BOOKING :", data)

        # Search CSV
        record = loader.find_booking(data)

        if record:
            print("CONSUMER:", record["consumer"])
            print("NAME    :", record["name"])
            print("DATE    :", record["date"])
            print("MOBILE  :", record["mobile"])
        else:
            print("❌ Booking not found in CSV!")

        print("==============================")

    # Draw QR box
    if points is not None:
        points = points.astype(int)

        for i in range(len(points[0])):
            pt1 = tuple(points[0][i])
            pt2 = tuple(points[0][(i + 1) % len(points[0])])

            cv2.line(frame, pt1, pt2, (0, 255, 0), 3)

    # Show booking number on screen
    if data:
        cv2.putText(
            frame,
            data,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

    cv2.imshow("Receipt Verifier", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()