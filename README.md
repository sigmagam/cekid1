# CekID

Bot Telegram untuk cek **ID user & chat**. Python + [kurigram](https://pypi.org/project/kurigram/)
(fork pyrogram yang mendukung `ButtonStyle` + rich message).

## Fitur

- `/start` — kartu **User Information** dalam **rich message** (judul + tabel): ID, First Name,
  Last Name, Username, DC ID, Photo, Premium, Bot, Permanent Link (nama bisa diklik), Bio.
- Kirim foto profil **bareng** kartu kalau user punya PP.
- **Efek animasi pesan** (`effect_id`) di chat pribadi.
- Keyboard menu berwarna. **Sekali tekan langsung buka dialog native** Telegram:
  - 👤 `User` (khusus non-bot) · ⭐️ `Premium` (non-bot + premium) · 🤖 `Bot`
  - 💬 `Forum` (supergroup bertopik) · 👥 `Group` · 📢 `Channel`
  - 🗂 `My Group` · 📚 `My Channel` — **chat yang kamu sendiri owner-nya**
    (`chat_is_created=True` + `bot_is_member=True`)
- `/id` — ID chat sekarang · `/id <id|@username>` — kartu info chat.
- `/cek` — `123456789`, `@username`, atau balas pesan user.
- `/broadcast` **(admin)** — balas sebuah pesan, atau `/broadcast teks` → kirim ke semua user
  yang pernah `/start`.
- `/stats` **(admin)** — jumlah user + path database.
- **Backup otomatis tiap 00:00 WIB** — file database dikirim ke admin (`ADMIN_IDS`).
  Salinannya konsisten (SQLite backup API), aman walau bot sedang jalan.
- Kalau Telegram menolak rich message → otomatis fallback ke HTML biasa.

## Contoh kartu

```
👤 User Information

🆔 ID: 123456789
👤 First Name: Budi
👥 Last Name: N/A
🔗 Username: @budi
🌐 DC ID: 2
🖼 Photo: ✅
⭐️ Premium: Yes
🤖 Bot: No
🌍 Language: id
🗓 Registration Date: Unknown
🔗 Permanent Link: Budi Santoso   (bisa diklik walau tanpa username)
📝 Bio: ...
```

## Struktur

```
cekid1/
├── main.py                  # entry point
├── requirements.txt
├── .env.example
└── cekid/
    ├── __init__.py          # kelas Client + command menu
    ├── config.py            # baca .env
    ├── store.py             # SQLite: user yang pernah /start
    ├── rich.py              # rich message + efek animasi + fallback HTML
    ├── keyboards.py         # menu request-button (user/chat picker) + inline
    ├── utils.py             # format kartu (rich + teks) + resolve chat
    ├── tasks.py             # backup database harian 00:00 WIB
    └── plugins/
        ├── start.py         # /start, /help, catat user
        ├── lookup.py        # users_shared -> user / premium / bot, /cek
        ├── chats.py         # chat_shared -> group / channel / forum / my group / my channel
        └── admin.py         # /broadcast, /stats
```

## Instalasi

```bash
git clone https://github.com/<kamu>/cekid1 && cd cekid1
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # isi API_ID, API_HASH, BOT_TOKEN, ADMIN_IDS
python main.py
```

### Auto restart (screen)

```bash
./start.sh    # jalankan di screen "cekid1" (auto-restart lewat run.sh)
./status.sh   # cek status + 15 baris log terakhir
./stop.sh     # hentikan
```

`screen -r cekid1` untuk lihat langsung, `Ctrl+A D` untuk keluar tanpa mematikan.

### Environment

| var | default | keterangan |
|---|---|---|
| `API_ID` / `API_HASH` / `BOT_TOKEN` | — | wajib |
| `ADMIN_IDS` (atau `ADMIN_ID`) | `728397761` | penerima backup, boleh banyak dipisah koma |
| `DB_PATH` | `cekid.db` | lokasi database SQLite |
| `RICH_MESSAGE` | `1` | set `0` untuk pakai HTML biasa |
| `EFFECTS` | `1` | set `0` untuk matikan efek animasi |

## Catatan

- **DC ID** diambil dari objek `User`/`Chat`; bisa kosong untuk sebagian chat → `Unknown`.
- **Photo** = `none` kalau user tidak punya foto profil (kartu dikirim sebagai teks saja).
- **Registration Date**: MTProto/TDLib tidak menyimpan tanggal registrasi akun, jadi nilainya
  `Unknown`. Referensi: [TDLib account_info](https://core.telegram.org/tdlib/docs/classtd_1_1td__api_1_1account_info.html),
  [action bar](https://core.telegram.org/api/action-bar).
- **Permanent Link** memakai `https://t.me/<username>` bila ada, kalau tidak `tg://user?id=<id>`
  supaya nama tetap bisa diklik.
