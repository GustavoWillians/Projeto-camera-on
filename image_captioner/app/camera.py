import cv2


class Camera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Usando backend mais estável no Windows
        if not self.cap.isOpened():
            raise Exception("Falha na captura da câmera.")

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        if self.cap.isOpened():
            self.cap.release()
