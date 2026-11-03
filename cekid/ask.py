"""`ask()` sendiri — tanpa pyromod, biar tidak bentrok dengan kurigram.

Pyromod menarik distribusi `pyrogram` upstream sehingga menimpa file
kurigram (mis. run.py jadi beda versi). Helper ini cuma butuh handler
sementara + Future.
"""

import asyncio

from pyrogram import filters
from pyrogram.handlers import MessageHandler

ASK_GROUP = 1


async def ask(client, chat_id, text, *, filter=None, reply_markup=None,
              timeout: float = 300, **kwargs):
    """Kirim `text`, lalu tunggu satu pesan balasan yang cocok. -> Message | None."""
    loop = asyncio.get_running_loop()
    future = loop.create_future()

    async def waiter(_, message):
        if not future.done():
            future.set_result(message)

    handler = MessageHandler(
        waiter, filters.chat(chat_id) & (filter or filters.all)
    )
    client.add_handler(handler, ASK_GROUP)
    try:
        if text:
            await client.send_message(chat_id, text, reply_markup=reply_markup, **kwargs)
        return await asyncio.wait_for(future, timeout)
    except asyncio.TimeoutError:
        return None
    finally:
        client.remove_handler(handler, ASK_GROUP)


if __name__ == "__main__":  # self-check: `python -m cekid.ask`
    import types as _types

    class _FakeClient:
        def __init__(self):
            self.groups = {}
            self.sent = []

        def add_handler(self, handler, group=0):
            self.groups.setdefault(group, []).append(handler)

        def remove_handler(self, handler, group=0):
            self.groups[group].remove(handler)

        async def send_message(self, chat_id, text, **kwargs):
            self.sent.append((chat_id, text))
            # Simulasi user cepat membalas: panggil handler yang terdaftar.
            msg = _types.SimpleNamespace(chat=chat_id, text="ok", id=1)
            for h in list(self.groups.get(ASK_GROUP, [])):
                await h.callback(self, msg)

    async def _check():
        client = _FakeClient()
        msg = await ask(client, 42, "prompt")
        assert msg is not None and msg.text == "ok", msg
        assert client.groups.get(ASK_GROUP) == [], "handler harus dibersihkan"
        assert client.sent == [(42, "prompt")]
        # timeout tidak boleh menggantung
        client2 = _FakeClient()
        client2.send_message = lambda *a, **k: _noop()
        assert await ask(client2, 1, "x", timeout=0.01) is None
        assert client2.groups.get(ASK_GROUP) == []
        print("ask self-check OK")

    async def _noop():
        return None

    import asyncio as _aio
    _aio.run(_check())
