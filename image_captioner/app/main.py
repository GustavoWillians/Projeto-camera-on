from tkinter import Tk, Button, Label, Canvas, StringVar, Frame, BOTH
import threading
import cv2
from PIL import Image, ImageTk
from camera import Camera
from model import ImageCaptioner


class App:
    def __init__(self, window):
        self.window = window
        self.window.title("Descritivo de Câmera com IA")
        self.window.state('zoomed')  # Maximiza a janela

        # Obter tamanho da tela
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()

        # Texto da descrição
        self.description = StringVar()
        self.description.set("Descrição: Nenhuma")

        # Frame para o vídeo
        self.video_frame = Frame(window, bg="black")
        self.video_frame.pack(fill=BOTH, expand=True)

        # Canvas para exibir o vídeo
        self.canvas = Canvas(self.video_frame, bg="black")
        self.canvas.pack(fill=BOTH, expand=True)

        # Frame dos botões e descrição
        self.controls_frame = Frame(window)
        self.controls_frame.pack(pady=10)

        # Botões
        self.start_button = Button(self.controls_frame, text="Iniciar Captura", command=self.start_capture)
        self.start_button.pack(side="left", padx=10)

        self.stop_button = Button(self.controls_frame, text="Parar Captura", command=self.stop_capture)
        self.stop_button.pack(side="left", padx=10)

        # Label de descrição
        self.label = Label(window, textvariable=self.description, wraplength=self.screen_width - 100, justify="center")
        self.label.pack(pady=10)

        self.camera = None
        self.ai = ImageCaptioner()
        self.running = False

        # Evento para redimensionar
        self.window.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        if event.width > 100 and event.height > 100:
            self.screen_width = event.width
            self.screen_height = event.height


    def start_capture(self):
        self.camera = Camera()
        self.running = True
        threading.Thread(target=self.update_frame, daemon=True).start()
        threading.Thread(target=self.run_captioner, daemon=True).start()

    def stop_capture(self):
        self.running = False
        if self.camera:
            self.camera.release()
            self.camera = None
        self.canvas.delete("all")
        self.description.set("Descrição: Nenhuma")

    def update_frame(self):
        while self.running and self.camera:
            frame = self.camera.get_frame()
            if frame is None:
                continue

            # Redimensiona o frame para caber na tela mantendo proporção
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Calcula o tamanho proporcional
            frame = self.resize_frame(frame)

            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            self.canvas.create_image(0, 0, anchor="nw", image=imgtk)
            self.canvas.imgtk = imgtk  # Mantém a referência

    def resize_frame(self, frame):
        h, w, _ = frame.shape
        max_width = max(640, self.screen_width)      # Garante pelo menos 640px
        max_height = max(480, self.screen_height - 200)  # Pelo menos 480px de altura útil

        scale = min(max_width / w, max_height / h)
        new_w = max(1, int(w * scale))   # Nunca menor que 1
        new_h = max(1, int(h * scale))   # Nunca menor que 1

        return cv2.resize(frame, (new_w, new_h))


    def run_captioner(self):
        while self.running and self.camera:
            frame = self.camera.get_frame()
            if frame is not None:
                caption = self.ai.generate_caption(frame)
                self.description.set(f"Descrição: {caption}")
            self.window.after(5000)  # Atualiza a cada 5 segundos


if __name__ == "__main__":
    window = Tk()
    app = App(window)
    window.mainloop()
