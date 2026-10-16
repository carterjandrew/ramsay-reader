import asyncio
import numpy as np
from aiohttp import web, WSMsgType
from f5_tts.socket_server import TTSStreamingProcessor


class WSSocketAdapter:
    def __init__(self, ws, loop=None):
        self.ws = ws
        # capture the event‐loop so we can schedule sends from another thread
        self.loop = loop or asyncio.get_event_loop()

    def sendall(self, data: bytes):
        """Emulate a socket.sendall by scheduling a WS send."""
        # if you’re sending your "END" sentinel as bytes:
        if data == b"END":
            # schedule an async send_str on the WS
            asyncio.run_coroutine_threadsafe(
                self.ws.send_str("END"), self.loop)
        else:
            # schedule sending the raw audio bytes
            asyncio.run_coroutine_threadsafe(
                self.ws.send_bytes(data), self.loop)


async def ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # capture the loop so our adapter can post back into it
    loop = asyncio.get_running_loop()

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            text = msg.data.strip()

            # build our adapter
            adapter = WSSocketAdapter(ws, loop)

            # run the blocking generate_stream in a thread,
            # passing our socket‐like adapter
            await loop.run_in_executor(
                None,
                lambda: processor.generate_stream(text, adapter)
            )

    return ws

app = web.Application()
app.router.add_get("/ws", ws_handler)

if __name__ == "__main__":
    # initialize your TTS processor once
    processor = TTSStreamingProcessor(
        model="F5TTS_Base",
        ckpt_file="finetuned_10000_f5_v1/last.safetensors",
        vocab_file="finetuned_10000_f5_v1/vocab.txt",
        ref_audio="data/ref/1.wav",
        ref_text="data/ref/1.txt"
    )
    web.run_app(app, host="0.0.0.0", port=8765)
