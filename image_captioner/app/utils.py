import time


def should_generate_caption(last_time, interval):
    """
    Verifica se já passou o intervalo para gerar uma nova legenda.
    """
    return time.time() - last_time > interval
