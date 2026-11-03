# CekID

Bot Telegram untuk cek **ID user & chat**. Python + [kurigram](https://pypi.org/project/kurigram/)
(fork pyrogram yang mendukung `ButtonStyle` + rich message).

## Fitur

- `/start` — kartu **User Information** lengkap (ID, nama, username, DC, premium, bot, language, permanent link, bio).
- Kirim foto profil **bareng** kartu kalau user punya PP.
- Keyboard menu berwarna (PRIMARY / SUCCESS). **Sekali tekan langsung buka dialog native**
  Telegram — tidak ada keyboard perantara:
  - 👤 `User` · ⭐️ `Premium` · 🤖 `Bot` (picker user, sudah difilter bot/premium)
  - 💬 `Forum` · 👥 `Group` · 📢 `Channel` (picker chat)
  - 🗂 `My Group` · 📚 `My Channel` — daftar chat yang bot sudah lihat (SQLite)
- **Forum** = supergroup dengan topik (`chat_is_channel=False` + `chat_is_forum=True`),
  bukan channel dan bukan group biasa.
- `/id` — ID chat sekarang; `/id <id|@username>` untuk kartu info chat; `/id` saat balas pesan
  sekalian tampilkan ID user.
- `/cek` — `123456789`, `@username`, atau balas pesan user.
- Semua chat yang bot lihat otomatis disimpan ke SQLite (`cekid.db`), bukan JSON.

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
    ├── store.py             # SQLite: chat yang pernah dilihat
    ├── keyboards.py         # menu request-button (user/chat picker) + inline
    ├── utils.py             # resolve chat + format kartu
    └── plugins/
        ├── start.py         # /start, /help
        ├── lookup.py        # users_shared -> user / premium / bot, /cek
        └── chats.py         # chat_shared -> group / channel / forum, /id, my group/channel
```

## Instalasi

```bash
git clone https://github.com/<kamu>/cekid1 && cd cekid1
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # isi API_ID, API_HASH, BOT_TOKEN
python main.py
```

## Catatan

- **DC ID** diambil dari objek `User`/`Chat`; bisa kosong untuk sebagian chat → `Unknown`.
- **Photo** = `none` kalau user tidak punya foto profil (kartu dikirim sebagai teks saja).
- **Registration Date**: MTProto/TDLib tidak menyimpan tanggal registrasi akun, jadi nilainya
  `Unknown`. Referensi: [TDLib account_info](https://core.telegram.org/tdlib/docs/classtd_1_1td__api_1_1account_info.html),
  [action bar](https://core.telegram.org/api/action-bar).
- **Permanent Link** memakai `https://t.me/<username>` bila ada, kalau tidak `tg://user?id=<id>`
  supaya nama tetap bisa diklik.
