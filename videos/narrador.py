"""Narración de los videos: normalizador de texto para TTS y servicios de voz para manim-voiceover.

En las escenas:
    from narrador import servicio
    self.set_speech_service(servicio())

`servicio()` devuelve Kokoro (local) salvo que VOZ_SERVICIO=elevenlabs. El texto se normaliza antes de
sintetizar y el servicio devuelve el texto normalizado, para que las marcas <bookmark/> se alineen con la
transcripción de Whisper.
"""
import os
import re
from pathlib import Path

from num2words import num2words

os.environ.setdefault("ESPEAK_DATA_PATH", "/usr/share/espeak-ng-data")  # el espeakng-loader de PyPI trae una ruta rota

VOZ = "em_alex"
ACENTO = "es-419"  # espeak "es" cecea ("opθión"); "es-419" sesea, como en Perú
VELOCIDAD = 0.95  # D1: un poco más lenta que la natural
DECIMAL = "coma"

# ---------------------------------------------------------------- normalizador

MARCA = re.compile(r"(<bookmark\s+mark\s*=\s*['\"][^'\"]*['\"]\s*/>)")
NUM = r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?"
MESES = {
    "ene": "enero", "feb": "febrero", "mar": "marzo", "abr": "abril", "may": "mayo", "jun": "junio",
    "jul": "julio", "ago": "agosto", "sep": "septiembre", "set": "septiembre", "oct": "octubre",
    "nov": "noviembre", "dic": "diciembre",
}
# Sustantivos masculinos ante los que "uno" se apocopa ("veintiún días", "un millón").
APOCOPE = r"(?=\s+(?:dólar|dólares|sol|soles|barril|barriles|días?|mes|meses|años?|millón|millones|puntos?)\b)"

# Siglas (sensibles a mayúsculas) y términos en inglés (insensibles), a la forma en que deben sonar.
# D2: las siglas se dicen por su nombre (en español si el libro lo usa); las que ya se pronuncian como palabra
# (ISDA, NYMEX, SOFR, NIIF, CESCE) quedan así. Ojo con el género: "la CSA" daría "la anexo"; en los guiones,
# escribir el nombre directamente y dejar este diccionario como red de seguridad.
SIGLAS = {
    "WTI": "uést téxas", "CCS": "cros cárrensi suap", "NDF": "fóruard sin entrega", "IRS": "suap de tasas",
    "CSA": "anexo de garantías", "ISDA": "ísda", "CVA": "ajuste por riesgo de crédito", "OTC": "fuera de bolsa",
    "VaR": "valor en riesgo", "NYMEX": "náimex", "SOFR": "sófer", "NIIF": "nif", "BCRP": "Banco Central de Reserva",
    "BN": "Banco de la Nación", "PFE": "exposición potencial futura", "EEFF": "estados financieros",
    "PETROPERÚ": "Petroperú", "CESCE": "cesce", "USD": "dólares", "PEN": "soles",
}
INGLES = {
    "cross currency swap": "cros cárrensi suap", "rate lock": "réit lok", "backwardation": "bacuardéishon",
    "moneyness": "mánines", "payoffs": "péy-ofs", "payoff": "péy-of", "swaps": "suaps", "swap": "suap",
    "forwards": "fóruards", "forward": "fóruard", "calls": "cols", "call": "col", "strike": "estráik",
    "spot": "espót", "collar": "cólar",
}


def _numero(texto: str) -> str:
    entero, _, decimales = texto.replace(",", "").partition(".")
    palabras = num2words(int(entero), lang="es")
    if decimales:
        ceros = len(decimales) - len(decimales.lstrip("0"))
        resto = decimales.lstrip("0")
        palabras += f" {DECIMAL} " + " ".join(["cero"] * ceros + ([num2words(int(resto), lang="es")] if resto else []))
    return palabras


def _apocopar(palabras: str) -> str:
    return re.sub(r"veintiuno$", "veintiún", re.sub(r"\buno$", "un", palabras))


def _moneda(m: re.Match) -> str:
    signo, simbolo, valor, escala = m.group("signo"), m.group("simbolo"), m.group("valor"), m.group("escala")
    moneda = "dólares" if simbolo == "US$" else "soles"
    palabras = _numero(valor)
    if escala:
        escala = escala.strip()
        if escala == "millones" and valor == "1":
            escala = "millón"
        texto = f"{_apocopar(palabras)} {escala} de {moneda}"
    elif valor == "1":
        texto = "un dólar" if simbolo == "US$" else "un sol"
    else:
        texto = f"{_apocopar(palabras)} {moneda}"
    return f"menos {texto}" if signo else texto


def _normalizar_tramo(t: str) -> str:
    t = re.sub(r"(\d{1,2})-(" + "|".join(MESES) + r")-(\d{4})",
               lambda m: f"{_numero(m[1])} de {MESES[m[2]]} de {_numero(m[3])}", t)
    t = re.sub(r"/\s*bbl\b", " por barril", t)
    t = re.sub(r"\bbbl\b", "barriles", t)
    moneda = rf"(?P<simbolo>US\$|S/)\s*(?P<valor>{NUM})(?P<escala>\s+(?:mil\s+)?(?:millones|millón))?"
    t = re.sub(rf"(?P<signo>\(){moneda}\)", _moneda, t)
    t = re.sub(rf"(?P<signo>){moneda}", _moneda, t)
    t = re.sub(rf"\(({NUM})\)", lambda m: f"menos {_numero(m[1])}", t)
    t = re.sub(rf"({NUM})\s*%", lambda m: f"{_numero(m[1])} por ciento", t)
    t = re.sub(rf"({NUM})\s*pb\b", lambda m: f"{_apocopar(_numero(m[1]))} puntos básicos", t)
    t = re.sub(rf"({NUM}){APOCOPE}", lambda m: _apocopar(_numero(m[1])), t)
    t = re.sub(NUM, lambda m: _numero(m[0]), t)
    t = re.sub(r"\s*=\s*", " igual a ", t)
    for sigla, dicho in SIGLAS.items():
        t = re.sub(rf"(?<![\w-]){re.escape(sigla)}(?![\w])", dicho, t)
    for termino, dicho in INGLES.items():
        t = re.sub(rf"\b{re.escape(termino)}\b", dicho, t, flags=re.IGNORECASE)
    return t


def normalizar(texto: str) -> str:
    """Convierte cifras, monedas, fechas, siglas y anglicismos a la forma en que deben leerse.
    Las marcas <bookmark mark="..."/> se conservan tal cual."""
    return "".join(p if MARCA.fullmatch(p) else _normalizar_tramo(p) for p in MARCA.split(texto))


# ---------------------------------------------------------------- servicios de voz

def _kokoro_service():
    from manim_voiceover.helper import remove_bookmarks
    from manim_voiceover.services.base import SpeechService, initialize_speech_service

    class KokoroService(SpeechService):
        """Kokoro-82M en local (CPU). Guarda .wav en la caché de manim-voiceover."""

        _pipeline = None

        def __init__(self, voz=VOZ, acento=ACENTO, velocidad=VELOCIDAD, **kwargs):
            kwargs.setdefault("transcription_model", "base")
            kwargs.setdefault("transcription_kwargs", {"language": "es"})
            initialize_speech_service(self, kwargs)
            self.voz, self.acento, self.velocidad = voz, acento, velocidad

        @classmethod
        def pipeline(cls, acento):
            if cls._pipeline is None:
                from kokoro import KPipeline
                from misaki import espeak

                cls._pipeline = KPipeline(lang_code="e", repo_id="hexgrad/Kokoro-82M")
                cls._pipeline.g2p = espeak.EspeakG2P(language=acento)
            return cls._pipeline

        def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
            import numpy as np
            import soundfile as sf

            cache_dir = cache_dir or self.cache_dir
            texto = normalizar(text)
            input_data = {"input_text": remove_bookmarks(texto), "service": "kokoro",
                          "voz": self.voz, "acento": self.acento, "velocidad": self.velocidad}
            cached = self.get_cached_result(input_data, cache_dir)
            if cached is not None:
                return cached
            audio_path = path or self.get_audio_basename(input_data) + ".wav"
            partes = self.pipeline(self.acento)(input_data["input_text"], voice=self.voz, speed=self.velocidad)
            audio = np.concatenate([a for _, _, a in partes])
            sf.write(Path(cache_dir) / audio_path, audio, 24000)
            return {"input_text": texto, "input_data": input_data, "original_audio": str(audio_path)}

    return KokoroService


def servicio(**kwargs):
    """Servicio de voz de la serie. VOZ_SERVICIO=elevenlabs usa ElevenLabs (requiere ELEVENLABS_API_KEY y
    ELEVENLABS_VOICE_ID); por defecto, Kokoro local."""
    if os.environ.get("VOZ_SERVICIO", "kokoro") == "elevenlabs":
        from manim_voiceover.services.elevenlabs import ElevenLabsService

        class ElevenLabsNormalizado(ElevenLabsService):
            def generate_from_text(self, text, *args, **kw):
                return super().generate_from_text(normalizar(text), *args, **kw)

        return ElevenLabsNormalizado(voice_id=os.environ["ELEVENLABS_VOICE_ID"],
                                     model="eleven_multilingual_v2", transcription_model="base", **kwargs)
    return _kokoro_service()(**kwargs)
