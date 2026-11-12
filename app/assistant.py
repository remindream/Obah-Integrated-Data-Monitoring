from collections import defaultdict, deque
from datetime import datetime
from zoneinfo import ZoneInfo

import anthropic

from app import config
from app.calendar_tools import TOOLS as CALENDAR_TOOLS

client = anthropic.Anthropic()

OWNER_PROMPT = """Kamu adalah asisten pribadi Pak Ravi, CEO Obah Group, lewat WhatsApp.
Unit bisnis: Obah Institute, Obah Energy (termasuk PT MAS), Cakap, Brandbeat, Canopia, Neksa, Daar Khaira.
Jawab dalam bahasa Indonesia, singkat dan jelas, cocok dibaca di WhatsApp (tanpa tabel markdown).
Untuk jadwal, gunakan alat kalender. Judul agenda selalu berformat "[Unit] Judul", dan akhiri dengan " !" bila prioritas tinggi.
Sebelum membuat agenda, pastikan tanggal, jam, dan unit jelas; bila ragu, tanyakan dulu."""

ADMIN_PROMPT = """Kamu adalah asisten bisnis Obah Group lewat WhatsApp, sedang melayani admin.
Jawab dalam bahasa Indonesia, singkat dan jelas, cocok dibaca di WhatsApp.
Kamu tidak punya akses ke agenda pribadi Pak Ravi dan tidak boleh membahasnya.
Data bisnis (PO, work order, material) belum tersambung; bila ditanya, sampaikan bahwa fitur itu segera tersedia."""

# Tools per role: the personal calendar is owner-only.
ROLE_SETUP = {
    "owner": (OWNER_PROMPT, CALENDAR_TOOLS),
    "admin": (ADMIN_PROMPT, []),
}

# Short per-number history kept in memory; moves to the database in a later phase.
_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=20))


def reply(number: str, text: str, role: str) -> str:
    system_prompt, tools = ROLE_SETUP[role]
    now = datetime.now(ZoneInfo(config.TIMEZONE)).strftime("%A, %d %B %Y %H:%M")
    history = _history[number]
    history.append({"role": "user", "content": f"[Waktu sekarang: {now} WIB]\n{text}"})
    messages = list(history)

    request = dict(
        model=config.ANTHROPIC_MODEL,
        max_tokens=16000,
        system=system_prompt,
        messages=messages,
        output_config={"effort": "low"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if tools:
        final = None
        for message in client.beta.messages.tool_runner(tools=tools, **request):
            final = message
    else:
        final = client.beta.messages.create(**request)

    if final is None or final.stop_reason == "refusal":
        answer = "Maaf Pak, permintaan ini belum bisa saya proses."
    else:
        answer = "".join(b.text for b in final.content if b.type == "text").strip()
        answer = answer or "Sudah saya proses, Pak."
    # Keep only plain text turns in history so the next request stays small.
    history.append({"role": "assistant", "content": answer})
    return answer
