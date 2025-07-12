import telebot
import os
import subprocess
from telebot.types import InputFile

# Get bot token from environment variable for security
BOT_TOKEN = os.getenv('8075723329:AAFyt2HJg1XC7c4-3VDt_MQ9LXKeOr0JgOQ')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set.")

bot = telebot.TeleBot(BOT_TOKEN)

# Define directories for temporary files
TEMP_DIR = "temp_files"
FRAMES_DIR = os.path.join(TEMP_DIR, "frames")
ENHANCED_FRAMES_DIR = os.path.join(TEMP_DIR, "enhanced_frames")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome to 4K Enhancer Bot!\nSend me a photo or video (max 50MB) to upscale.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    bot.reply_to(message, "📤 Downloading photo...")
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # Ensure TEMP_DIR exists
    os.makedirs(TEMP_DIR, exist_ok=True)

    input_path = os.path.join(TEMP_DIR, f"input_{user_id}.jpg")
    output_path = os.path.join(TEMP_DIR, f"enhanced_input_{user_id}.jpg") # Consistent naming for enhanced output

    with open(input_path, 'wb') as f:
        f.write(downloaded_file)

    bot.reply_to(message, "⚙️ Enhancing to 4K... please wait (2–3 min).")

    try:
        # Use subprocess.run for better control and error handling
        result = subprocess.run(
            ["python", "enhance_image.py", input_path, output_path],
            capture_output=True, text=True, check=True
        )
        # Optional: Print stdout/stderr from the subprocess for debugging
        print("enhance_image.py stdout:", result.stdout)
        if result.stderr:
            print("enhance_image.py stderr:", result.stderr)

        if os.path.exists(output_path):
            with open(output_path, 'rb') as f:
                bot.send_photo(chat_id, f, caption="✅ Enhanced to 4K!")
        else:
            bot.reply_to(message, "❌ Enhancement failed: Output image not found.")
            print(f"Error: Output image {output_path} not found after enhancement.")

    except subprocess.CalledProcessError as e:
        bot.reply_to(message, f"❌ An error occurred during enhancement: {e.stderr}")
        print(f"Subprocess error during image enhancement:\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}")
    except Exception as e:
        bot.reply_to(message, f"❌ An unexpected error occurred: {str(e)}")
        print(f"Unexpected error in handle_photo: {e}")
    finally:
        # Clean up files
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
        # Clean up temp_files directory if empty or specific to user
        # (More robust cleanup would be a cron job or startup script)
        if not os.listdir(TEMP_DIR):
            os.rmdir(TEMP_DIR)


@bot.message_handler(content_types=['video'])
def handle_video(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    bot.reply_to(message, "📥 Downloading video...")

    file_id = message.video.file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # Ensure TEMP_DIR and its subdirectories exist
    os.makedirs(FRAMES_DIR, exist_ok=True)
    os.makedirs(ENHANCED_FRAMES_DIR, exist_ok=True)

    input_path = os.path.join(TEMP_DIR, f"input_{user_id}.mp4")
    output_path = os.path.join(TEMP_DIR, f"enhanced_input_{user_id}.mp4")

    with open(input_path, 'wb') as f:
        f.write(downloaded_file)

    bot.reply_to(message, "⚙️ Enhancing video to 4K... This may take a while.")

    try:
        # Use subprocess.run for better control and error handling
        result = subprocess.run(
            ["python", "enhance_video.py", input_path, output_path],
            capture_output=True, text=True, check=True
        )
        print("enhance_video.py stdout:", result.stdout)
        if result.stderr:
            print("enhance_video.py stderr:", result.stderr)

        if os.path.exists(output_path):
            with open(output_path, 'rb') as f:
                bot.send_video(chat_id, f, caption="✅ 4K enhanced video!")
        else:
            bot.reply_to(message, "❌ Video enhancement failed: Output video not found.")
            print(f"Error: Output video {output_path} not found after enhancement.")

    except subprocess.CalledProcessError as e:
        bot.reply_to(message, f"❌ An error occurred during video enhancement: {e.stderr}")
        print(f"Subprocess error during video enhancement:\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}")
    except Exception as e:
        bot.reply_to(message, f"❌ An unexpected error occurred: {str(e)}")
        print(f"Unexpected error in handle_video: {e}")
    finally:
        # Clean up all temporary files and directories
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
        # Use shutil.rmtree for directories to remove contents
        import shutil
        if os.path.exists(FRAMES_DIR):
            shutil.rmtree(FRAMES_DIR)
        if os.path.exists(ENHANCED_FRAMES_DIR):
            shutil.rmtree(ENHANCED_FRAMES_DIR)
        if os.path.exists(TEMP_DIR) and not os.listdir(TEMP_DIR): # Only remove if empty
            os.rmdir(TEMP_DIR)

bot.polling()
