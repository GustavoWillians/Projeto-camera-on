import cv2
import time


class Camera: # Classe para gerenciar a câmera e exibir imagens com legendas
    def __init__(self): # Inicializa a câmera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise IOError("Não foi possível acessar a câmera.")
        self.last_caption_time = 0

    def get_frame(self): # Captura um frame da câmera
        ret, frame = self.cap.read()
        if not ret:
            raise IOError("Falha na captura da câmera.")
        return frame

    def release(self): # Libera os recursos da câmera
        self.cap.release()

    def show_frame(self, frame, caption=""): # Exibe o frame com uma legenda
        # Exibir legenda na imagem
        cv2.putText(
            frame,
            caption,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )
        cv2.imshow("Camera com IA", frame)

    def wait_key(self):
        return cv2.waitKey(1) & 0xFF
