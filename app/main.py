import logging

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse

from app import assistant, config, whatsapp

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("obah-idm")
app = FastAPI(title="Obah Integrated Data Monitoring")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/webhook")
def verify(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == config.WA_VERIFY_TOKEN:
        return PlainTextResponse(params.get("hub.challenge", ""))
    raise HTTPException(status_code=403)


def _handle(number: str, text: str, role: str) -> None:
    try:
        whatsapp.send_text(number, assistant.reply(number, text, role))
    except Exception:
        log.exception("Gagal memproses pesan dari %s", number)
        whatsapp.send_text(number, "Maaf Pak, ada gangguan. Coba lagi sebentar lagi.")


@app.post("/webhook")
async def receive(request: Request, background: BackgroundTasks):
    body = await request.body()
    if not whatsapp.signature_is_valid(body, request.headers.get("X-Hub-Signature-256")):
        raise HTTPException(status_code=401)
    data = await request.json()
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            for msg in change.get("value", {}).get("messages", []):
                number = msg.get("from", "")
                if number == config.OWNER_WA_NUMBER:
                    role = "owner"
                elif number in config.ADMIN_WA_NUMBERS:
                    role = "admin"
                else:
                    log.info("Abaikan pesan dari nomor tidak terdaftar")
                    continue
                if msg.get("type") == "text":
                    background.add_task(_handle, number, msg["text"]["body"], role)
    # Meta needs a fast 200, the reply is sent in the background.
    return {"status": "received"}
