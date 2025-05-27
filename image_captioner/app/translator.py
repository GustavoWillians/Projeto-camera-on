from deep_translator import GoogleTranslator


class TranslatorPT:
    def __init__(self):
        self.translator = GoogleTranslator(source='auto', target='pt')

    def traduzir(self, texto):
        try:
            return self.translator.translate(texto)
        except Exception as e:
            print(f"[Erro na tradução] {e}")
            return texto  # Se falhar, retorna o texto original
