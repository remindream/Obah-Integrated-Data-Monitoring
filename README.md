# Obah Integrated Data Monitoring

Sistem asisten dan pemantauan data Obah Group. Tahap 1: asisten WhatsApp pribadi Pak Ravi yang menjawab chat dengan Claude dan membaca/menambah agenda di Google Calendar.

## Rencana tahap
1. Bot WA membalas chat + baca/tambah Google Calendar (tahap ini)
2. Ringkasan pagi otomatis
3. Kabar bisnis dari Sheet PT MAS (Work Order, Material Order List, Keuangan)
4. Panel web untuk admin (login, riwayat kabar, pengaturan)
5. Target dan unit bisnis lain

## Menjalankan di Railway
1. Buat proyek baru dari repo ini.
2. Isi semua variabel di `.env.example` lewat menu **Variables** (nilai rahasia hanya diisi oleh pemilik).
3. Setelah deploy, pakai alamat `https://<domain-railway>/webhook` sebagai Callback URL di Meta, dengan Verify token sama dengan `WA_VERIFY_TOKEN`, lalu langganan field `messages`.

Konvensi judul agenda: `[Unit] Judul`, akhiri dengan ` !` untuk prioritas tinggi.
