from tkinter import Tk, Button, Label, Canvas, StringVar, Frame, CENTER
import threading
import cv2
from PIL import Image, ImageTk
from camera import Camera
from model import ImageCaptioner
from translator import TranslatorPT
import time


class App:
    def __init__(self, window):
        self.window = window
        self.translator = TranslatorPT()
        self.window.title("Descritivo de Câmera com IA")
        self.window.state('zoomed')

        # Tamanho mínimo da janela (garante que a janela não fique menor que a área da câmera)
        self.min_width = 700
        self.min_height = 600
        self.window.minsize(self.min_width, self.min_height)

        self.description = StringVar()
        self.description.set("Descrição: Nenhuma")

        # Frame do vídeo com borda
        self.video_frame = Frame(window, bg="black", padx=20, pady=20)
        self.video_frame.pack(fill="both", expand=True)

        self.canvas = Canvas(self.video_frame, bg="gray20", highlightthickness=4, highlightbackground="white")
        self.canvas.place(relx=0.5, rely=0.5, anchor=CENTER)

        # Controles
        self.controls_frame = Frame(window)
        self.controls_frame.pack(pady=10)

        self.start_button = Button(self.controls_frame, text="Iniciar Captura", command=self.start_capture)
        self.start_button.pack(side="left", padx=10)

        self.stop_button = Button(self.controls_frame, text="Parar Captura", command=self.stop_capture, state="disabled")
        self.stop_button.pack(side="left", padx=10)

        self.label = Label(
            window,
            textvariable=self.description,
            justify="center",
            font=("Arial", 16),
            bg="#222222",
            fg="#00FF00"
        )
        self.label.pack(pady=20, fill="x")

        self.camera = None
        self.ai = ImageCaptioner()
        self.running = False
        self.last_frame = None  # Frame compartilhado para legenda

        self.lock = threading.Lock()  # Protege acesso ao last_frame

        # Bind para redimensionamento da janela
        self.window.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        new_width = event.width
        wrap = max(100, new_width - 100)
        self.label.config(wraplength=wrap)
        # Também reajustar o tamanho do canvas para manter centralizado e com borda
        self.resize_canvas()

    def resize_canvas(self):
        if not self.camera:
            return
        win_w = self.window.winfo_width()
        win_h = self.window.winfo_height()

        # Define tamanho máximo para o vídeo respeitando bordas e controles
        max_w = max(self.min_width - 100, win_w - 100)
        max_h = max(self.min_height - 200, win_h - 200)

        # Usar último frame para calcular escala
        with self.lock:
            frame = self.last_frame.copy() if self.last_frame is not None else None
        if frame is None:
            # Usa tamanho default se não tem frame ainda
            video_w, video_h = 640, 480
        else:
            h, w = frame.shape[:2]
            scale = min(max_w / w, max_h / h)
            video_w = int(w * scale)
            video_h = int(h * scale)

        self.canvas.config(width=video_w, height=video_h)

    def start_capture(self):
        if not self.running:
            self.camera = Camera()
            self.running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")

            self.update_frame()  # Inicia o loop de vídeo via after
            threading.Thread(target=self.run_captioner, daemon=True).start()

    def stop_capture(self):
        self.running = False
        if self.camera:
            self.camera.release()
            self.camera = None
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.canvas.delete("all")
        self.description.set("Descrição: Nenhuma")

    def update_frame(self):
        if self.running and self.camera:
            try:
                frame = self.camera.get_frame()
            except Exception as e:
                self.description.set(f"Erro câmera: {e}")
                self.stop_capture()
                return

            with self.lock:
                self.last_frame = frame.copy()

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = self.resize_frame(frame_rgb)

            img = Image.fromarray(frame_resized)
            imgtk = ImageTk.PhotoImage(image=img)

            self.canvas.create_image(0, 0, anchor="nw", image=imgtk)
            self.canvas.imgtk = imgtk  # Referência para evitar GC

            self.resize_canvas()  # Ajusta o canvas caso a janela tenha sido redimensionada

        if self.running:
            self.window.after(15, self.update_frame)  # Atualiza frame ~66 fps

    def resize_frame(self, frame):
        h, w = frame.shape[:2]

        win_w = self.window.winfo_width()
        win_h = self.window.winfo_height()

        max_w = max(self.min_width - 100, win_w - 100)
        max_h = max(self.min_height - 200, win_h - 200)

        scale = min(max_w / w, max_h / h)
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        return cv2.resize(frame, (new_w, new_h))

    def run_captioner(self):
        while self.running:
            with self.lock:
                frame = self.last_frame.copy() if self.last_frame is not None else None
            if frame is not None:
                try:
                    caption = self.ai.generate_caption(frame)
                    caption_ptbr = self.translator.traduzir(caption)
                    self.description.set(f"Descrição: {caption_ptbr}")
                except Exception as e:
                    self.description.set(f"Erro IA: {e}")
            time.sleep(5)


if __name__ == "__main__":
    window = Tk()
    app = App(window)
    window.mainloop()
