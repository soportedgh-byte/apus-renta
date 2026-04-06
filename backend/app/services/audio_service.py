"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/services/audio_service.py
Proposito: Generacion de podcasts educativos con 2 voces (edge-tts).
           Personajes: Sofia (auditora nueva) y Don Carlos (30 anios de experiencia).
Sprint: Capacitacion 2.0
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import asyncio
import io
import logging
import os
import tempfile
import uuid
from typing import Optional

from app.config import configuracion

logger = logging.getLogger("cecilia.services.audio")

# Voces de edge-tts para Colombia
VOZ_SOFIA = os.getenv("TTS_VOICE_FEMALE", "es-CO-SalomeNeural")
VOZ_DON_CARLOS = os.getenv("TTS_VOICE_MALE", "es-CO-GonzaloNeural")

# Prompt para generar el script del podcast
PROMPT_PODCAST = """Eres un guionista experto de podcasts educativos sobre control fiscal colombiano.
Genera un script de podcast conversacional de {duracion} sobre el tema: "{tema}"

PERSONAJES:
- SOFIA: Auditora nueva en la CGR, curiosa, hace preguntas inteligentes desde la ignorancia.
  Habla de manera cercana y natural. Usa expresiones colombianas informales pero respetuosas.
- DON CARLOS: Auditor con 30 anios de experiencia en la CGR, paciente, usa historias
  anonimizadas y analogias cotidianas para explicar. Es profundo pero accesible.

REGLAS:
1. Empieza con Sofia haciendo una pregunta sobre el tema
2. Don Carlos responde con profundidad, citando normatividad REAL (leyes, decretos, circulares)
3. Sofia hace preguntas de seguimiento inteligentes
4. Incluir AL MENOS 3 citas normativas reales
5. Usar analogias con la vida cotidiana para explicar conceptos
6. Terminar con un resumen de Don Carlos y una reflexion de Sofia
7. NO usar datos personales reales — anonimizar todo ejemplo
8. El tono es profesional pero conversacional, como entre colegas

CONTEXTO NORMATIVO DISPONIBLE:
{contexto_rag}

FORMATO DE SALIDA (estricto):
[INTRO]
Breve descripcion de la intro musical

SOFIA: (texto de Sofia)

DON CARLOS: (texto de Don Carlos)

SOFIA: (texto de Sofia)

... (continuar la conversacion)

[CIERRE]
Breve descripcion del cierre
"""


class AudioService:
    """Servicio de generacion de audio educativo con edge-tts."""

    def __init__(self, llm=None, rag_retriever=None):
        self.llm = llm
        self.rag_retriever = rag_retriever

    async def generar_script_podcast(
        self, tema: str, duracion: str = "5 minutos", contexto_extra: str = ""
    ) -> str:
        """Genera el script conversacional usando el LLM + RAG."""
        # Buscar contexto en el RAG
        contexto_rag = ""
        if self.rag_retriever:
            try:
                docs = await asyncio.to_thread(
                    self.rag_retriever.invoke, tema
                )
                contexto_rag = "\n".join(
                    [d.page_content[:500] for d in docs[:5]]
                )
            except Exception as e:
                logger.warning("Error consultando RAG para podcast: %s", e)

        if not contexto_rag:
            contexto_rag = contexto_extra or (
                "Usar conocimiento general sobre control fiscal colombiano, "
                "Ley 42/1993, Ley 610/2000, Decreto 403/2020, Circular 023 CGR."
            )

        prompt = PROMPT_PODCAST.format(
            duracion=duracion, tema=tema, contexto_rag=contexto_rag
        )

        if self.llm:
            try:
                respuesta = await asyncio.to_thread(
                    self.llm.invoke, prompt
                )
                return respuesta.content if hasattr(respuesta, "content") else str(respuesta)
            except Exception as e:
                logger.error("Error generando script con LLM: %s", e)

        # Fallback: script de ejemplo
        return self._script_fallback(tema)

    async def generar_audio_podcast(
        self, script: str
    ) -> tuple[bytes, int]:
        """Convierte script a audio MP3 con 2 voces usando edge-tts.

        Returns:
            tuple[bytes, int]: (audio_mp3_bytes, duracion_estimada_segundos)
        """
        try:
            import edge_tts
        except ImportError:
            logger.error("edge-tts no instalado — pip install edge-tts")
            raise RuntimeError("edge-tts no disponible")

        # Parsear el script en segmentos
        segmentos = self._parsear_script(script)

        if not segmentos:
            raise ValueError("No se pudieron parsear segmentos del script")

        # Generar cada segmento con la voz correspondiente
        archivos_temp = []
        try:
            for personaje, texto in segmentos:
                voz = VOZ_SOFIA if personaje == "SOFIA" else VOZ_DON_CARLOS
                temp_file = tempfile.NamedTemporaryFile(
                    suffix=".mp3", delete=False
                )
                temp_file.close()

                communicate = edge_tts.Communicate(texto, voz)
                await communicate.save(temp_file.name)
                archivos_temp.append(temp_file.name)

            # Combinar archivos con pydub
            audio_final = await self._combinar_audios(archivos_temp)
            duracion = len(audio_final) // 1000  # ms a segundos (aprox)

            # Exportar a bytes
            buffer = io.BytesIO()
            audio_final.export(buffer, format="mp3")
            return buffer.getvalue(), duracion

        finally:
            # Limpiar temporales
            for f in archivos_temp:
                try:
                    os.unlink(f)
                except OSError:
                    pass

    async def generar_explicacion_audio(
        self, tema: str, voz: str = "DON_CARLOS"
    ) -> tuple[bytes, int]:
        """Genera explicacion narrada de un solo locutor (2-3 min)."""
        try:
            import edge_tts
        except ImportError:
            raise RuntimeError("edge-tts no disponible")

        # Generar texto con LLM
        texto = await self._generar_explicacion_texto(tema)

        voice_id = VOZ_DON_CARLOS if voz == "DON_CARLOS" else VOZ_SOFIA
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        temp_file.close()

        try:
            communicate = edge_tts.Communicate(texto, voice_id)
            await communicate.save(temp_file.name)

            with open(temp_file.name, "rb") as f:
                audio_bytes = f.read()

            duracion = len(audio_bytes) // 16000  # estimacion
            return audio_bytes, duracion
        finally:
            try:
                os.unlink(temp_file.name)
            except OSError:
                pass

    def _parsear_script(self, script: str) -> list[tuple[str, str]]:
        """Parsea el script en segmentos (personaje, texto)."""
        segmentos = []
        lineas = script.strip().split("\n")

        for linea in lineas:
            linea = linea.strip()
            if not linea or linea.startswith("["):
                continue

            if linea.startswith("SOFIA:"):
                texto = linea[len("SOFIA:"):].strip()
                if texto:
                    segmentos.append(("SOFIA", texto))
            elif linea.startswith("DON CARLOS:"):
                texto = linea[len("DON CARLOS:"):].strip()
                if texto:
                    segmentos.append(("DON_CARLOS", texto))

        return segmentos

    async def _combinar_audios(self, archivos: list[str]):
        """Combina multiples MP3 en uno solo con pausas entre segmentos."""
        from pydub import AudioSegment

        pausa = AudioSegment.silent(duration=800)  # 800ms entre segmentos
        combinado = AudioSegment.empty()

        for archivo in archivos:
            segmento = AudioSegment.from_mp3(archivo)
            if len(combinado) > 0:
                combinado += pausa
            combinado += segmento

        return combinado

    async def _generar_explicacion_texto(self, tema: str) -> str:
        """Genera texto explicativo corto para narrador unico."""
        if self.llm:
            prompt = (
                f"Eres Don Carlos, un auditor experto de la CGR colombiana con 30 anios de experiencia. "
                f"Explica en 300 palabras de forma clara y didactica: '{tema}'. "
                f"Usa analogias cotidianas y cita normatividad real. "
                f"Habla en primera persona de forma conversacional."
            )
            try:
                resp = await asyncio.to_thread(self.llm.invoke, prompt)
                return resp.content if hasattr(resp, "content") else str(resp)
            except Exception:
                pass

        return (
            f"Hoy vamos a hablar sobre {tema}. "
            f"Este es un tema fundamental en el control fiscal colombiano. "
            f"Como auditores de la Contraloria General de la Republica, "
            f"debemos entenderlo a profundidad para cumplir nuestra mision constitucional."
        )

    def _script_fallback(self, tema: str) -> str:
        """Script de ejemplo cuando el LLM no esta disponible."""
        return f"""[INTRO]
Musica suave institucional de CecilIA

SOFIA: Hola Don Carlos, hoy quisiera entender mejor el tema de {tema}. Es algo que me han mencionado varias veces pero no tengo claro como funciona en la practica.

DON CARLOS: Sofia, excelente pregunta. Mira, {tema} es uno de los conceptos fundamentales del control fiscal en Colombia. La Constitucion en su articulo 267 nos da el marco general, y la Ley 42 de 1993 lo desarrolla en detalle.

SOFIA: Pero como se aplica eso en el dia a dia de una auditoria?

DON CARLOS: Dejame explicarte con un ejemplo. Imagina que estas revisando los estados financieros de una entidad publica. Es como revisar las cuentas de tu hogar — necesitas verificar que cada peso gastado tenga un soporte, que los ingresos cuadren con los registros, y que no haya movimientos sin justificacion.

SOFIA: Eso suena logico. Y que normas especificas aplican?

DON CARLOS: Principalmente la Ley 610 del 2000 para responsabilidad fiscal, el Decreto 403 de 2020 para los principios del control fiscal, y por supuesto la Circular 023 de la CGR que nos orienta sobre el uso de herramientas como CecilIA.

SOFIA: Gracias Don Carlos, ahora entiendo mucho mejor. Es mas complejo de lo que parecia pero tiene toda la logica.

DON CARLOS: Asi es, Sofia. Recuerda que en la Contraloria nuestro trabajo es proteger el patrimonio publico de todos los colombianos. Cada auditoria que hacemos contribuye a la transparencia y la rendicion de cuentas.

[CIERRE]
Esto fue un episodio de CecilIA Aprende. Recuerde que toda informacion debe ser validada por el auditor responsable conforme a la Circular 023 de la CGR.
"""
