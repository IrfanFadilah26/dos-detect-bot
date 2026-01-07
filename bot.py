import telebot
import joblib
import numpy as np
import pandas as pd

# 1. IDENTITAS BOT (Masukkan Token dari BotFather)
TOKEN = '8582399104:AAFw6Qm02IXzIMRYwwZq_1Lo0xiNg0xl6mo' 
bot = telebot.TeleBot(TOKEN)

# 2. MUAT MODEL & FITUR
try:
    print("Sedang memuat model...")
    model = joblib.load('model_dos_top10.pkl')
    scaler = joblib.load('scaler_top10.pkl')
    # Daftar 10 fitur urut yang kamu dapatkan tadi
    feature_names = ['sload: Laju beban bit sumber (bit/detik)', 'smean: Ukuran rata-rata paket pengirim', 'rate: Total paket per detik', 'sbytes: Total byte dikirim sumber', 'proto: Kode numerik protokol', 'dmean: Ukuran rata-rata paket tujuan', 'dload: Laju beban bit tujuan (bit/detik)', 'sttl: Time to Live sumber ke tujuan', 'dttl: Time to Live tujuan ke sumber', 'ct_srv_dst: Koneksi layanan & alamat tujuan sama']
    print("✅ Model & Scaler berhasil dimuat!")
except Exception as e:
    print(f"❌ Gagal memuat file: {e}")

# 3. PERINTAH /START
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    list_f = "\n".join([f"{i+1}. {name}" for i, name in enumerate(feature_names)])
    msg = (
        "🤖 **Bot Deteksi DoS Aktif!**\n\n"
        "Silakan kirimkan 10 nilai fitur (pisahkan dengan koma) sesuai urutan ini:\n\n"
        f"{list_f}\n\n"
        "Contoh: 150.5, 60, 1.2, 500, 113, 40, 20.5, 31, 29, 2"
    )
    bot.reply_to(message, msg, parse_mode='Markdown')

# 4. PERINTAH /INFO
@bot.message_handler(commands=['info_proto'])
def info_proto(message):
    pesan = (
        "<b>📚 Panduan Kode Protokol (proto)</b>\n\n"
        "Gunakan kode angka berikut untuk input:\n"
        "🔹 <b>Umum:</b>\n"
        "- 113: tcp\n"
        "- 119: udp\n"
        "- 37: icmp\n"
        "- 42: igmp\n\n"
        "🔹 <b>Lainnya:</b>\n"
        "- 6: arp\n"
        "- 120: unas\n"
        "- 132: zero\n\n"
        "<i>Untuk daftar lengkap (0-132), silakan hubungi Admin.</i>"
    )
    bot.reply_to(message, pesan, parse_mode='HTML')

# 5. PROSES PREDIKSI
@bot.message_handler(func=lambda m: True)
def predict(message):
    try:
        # Mengubah teks menjadi list angka
        input_data = [float(i.strip()) for i in message.text.split(',')]
        
        if len(input_data) != 10:
            bot.reply_to(message, f"❌ Harus 10 angka! Kamu baru mengirim {len(input_data)} angka.")
            return

        # Array & Scaling
        arr = np.array(input_data).reshape(1, -1)
        scaled_data = scaler.transform(arr) # Menggunakan scaler khusus 10 fitur
        
        # Prediksi
        prediction = model.predict(scaled_data)

        if prediction[0] == 1:
            bot.reply_to(message, "🚨 **PERINGATAN: TERDETEKSI SERANGAN DoS!** 🚨")
        else:
            bot.reply_to(message, "✅ **HASIL: TRAFIK NORMAL (AMAN).**")

    except ValueError:
        bot.reply_to(message, "⚠️ Format salah! Pastikan hanya mengirim angka yang dipisahkan koma.")
    except Exception as e:
        bot.reply_to(message, f"Terjadi kesalahan: {e}")

print("Bot sedang berjalan... (Tekan Ctrl+C untuk berhenti)")
bot.polling()