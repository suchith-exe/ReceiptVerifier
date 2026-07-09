import cv2


class QRScanner:

    def __init__(self, camera=1):
        self.cap = cv2.VideoCapture(camera)
        self.detector = cv2.QRCodeDetector()

    def get_frame(self):

        ret, frame = self.cap.read()

        if not ret:
            return None, None

        data, points, _ = self.detector.detectAndDecode(frame)

        if points is not None:
            points = points.astype(int)

            for i in range(len(points[0])):
                pt1 = tuple(points[0][i])
                pt2 = tuple(points[0][(i + 1) % len(points[0])])

                cv2.line(frame, pt1, pt2, (0, 255, 0), 3)

        return frame, data

    def release(self):
        self.cap.release()