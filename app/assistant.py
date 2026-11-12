from collections import defaultdict, deque
from datetime import datetime
from zoneinfo import ZoneInfo

import anthropic

from app import config
from app.calendar_tools import TOOLS

client = anthropic.Anthropic()

SYSTEM_PROMPT = """Kamu adalah asisten pribadi Pak Ravi, CEO Obah Group, lewat WhatsApp.
Unit bisnis: Obah Institute, Obah Energy (termasuk PT MAS), Cakap, Brandbeat, Canopia, Neksa, Daar Khaira.
Jawab dalam bahasa Indonesia, singkat dan jelas, cocok dibaca di WhatsApp (tanpa tabel markdown).
Untuk jadwal, gunakan alat kalender. Judul agenda selalu berformat "[Unit] Judul", dan akhiri dengan " !" bila prioritas tinggi.
Sebelum membuat agenda, pastikan tanggal, jam, dan unit jelas; bila ragu, tanyakan dulu."""

# Short per-number history kept in memory; moves to the database in a later phase.
_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=20))


def reply(number: str, text: str) -> str:
    now = datetime.now(ZoneInfo(config.TIMEZONE)).strftime("%A, %d %B %Y %H:%M")
    history = _history[number]
    history.append({"role": "user", "content": f"[Waktu sekarang: {now} WIB]\n{text}"})
    messages = list(history)

    runner = client.beta.messages.tool_runner(
        model=config.ANTHROPIC_MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=messages,
        output_config={"effort": "low"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    final = None
    for message in runner:
        final = message

    if final is None or final.stop_reason == "refusal":
        answer = "Maaf Pak, permintaan ini belum bisa saya proses."
    else:
        answer = "".join(b.text for b in final.content if b.type == "text").strip()
        answer = answer or "Sudah saya proses, Pak."
    # Keep only plain text turns in history so the next request stays small.
    history.append({"role": "assistant", "content": answer})
    return answer
