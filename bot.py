
import telebot
import os
from telebot.types import InputFile

BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome to 4K Enhancer Bot!\nSend me a photo or video (max 50MB) to upscale.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "📤 Downloading photo...")
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    input_path = f"input_{message.from_user.id}.jpg"
    with open(input_path, 'wb') as f:
        f.write(downloaded_file)

    bot.reply_to(message, "⚙️ Enhancing to 4K... please wait (2–3 min).")

    os.system(f"python enhance_image.py {input_path}")

    output_path = f"enhanced_{input_path}"
    with open(output_path, 'rb') as f:
        bot.send_photo(message.chat.id, f, caption="✅ Enhanced to 4K!")

    os.remove(input_path)
    os.remove(output_path)

@bot.message_handler(content_types=['video'])
def handle_video(message):
    bot.reply_to(message, "📥 Downloading video...")

    file_id = message.video.file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    input_path = f"input_{message.from_user.id}.mp4"
    with open(input_path, 'wb') as f:
        f.write(downloaded_file)

    bot.reply_to(message, "⚙️ Enhancing video to 4K...")

    os.system(f"python enhance_video.py {input_path}")

    output_path = f"enhanced_{input_path}"
    if os.path.exists(output_path):
        with open(output_path, 'rb') as f:
            bot.send_video(message.chat.id, f, caption="✅ 4K enhanced video!")
        os.remove(output_path)

    os.remove(input_path)

bot.polling()
