from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
import cv2


class ImageCaptioner:
    def __init__(self):
        print("Carregando modelo de IA...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(self.device)
        print("Modelo carregado.")

    def generate_caption(self, frame):
        try:
            # Converte o frame OpenCV (BGR) para PIL (RGB)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)

            inputs = self.processor(images=image, return_tensors="pt").to(self.device)
            out = self.model.generate(**inputs)
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            return caption

        except Exception as e:
            return f"Erro na descrição: {str(e)}"
