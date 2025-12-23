from telethon import TelegramClient, events
import asyncio
import aiohttp
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

api_id = 21486690
api_hash = '0212fe8d0ecb9ddd51591024e3c01af2'
session_name = 'sajjad'
phone_number = "+989123456789"

source_channel_id = [-1002844293070, -1001345567481, -1001882955751, -1001999800440]
target_users = [67675841, 2064817028, 6771293222, 1709517759]

logger.info("شروع برنامه...")
client = TelegramClient(session_name, api_id, api_hash)
logger.info("Client ساخته شد.")


# ===============================
#  تابع استخراج دکمه‌های شیشه‌ای
# ===============================
def extract_buttons(message):
    if not message.reply_markup:
        return ""

    text = "\n\n🔘 *دکمه‌های شیشه‌ای:* \n"

    try:
        for row in message.reply_markup.rows:
            for button in row.buttons:
                btn_text = getattr(button, 'text', '')
                btn_url = getattr(button, 'url', None)
                btn_data = None

                # اگر دکمه دیتا داشته باشد (callback)
                if hasattr(button, 'data') and button.data:
                    btn_data = button.data.decode(errors="ignore")

                # ساخت قالب متن دکمه
                if btn_url:
                    text += f"• {btn_text} → {btn_url}\n"
                elif btn_data:
                    text += f"• {btn_text} → (data: {btn_data})\n"
                else:
                    text += f"• {btn_text}\n"

        return text

    except Exception as e:
        logger.error("خطا در استخراج دکمه‌ها: %s", str(e))
        return ""


# ===============================
#  Handler اصلی
# ===============================
@client.on(events.NewMessage(chats=source_channel_id))
async def forward_handler(event):
    logger.info("پیام جدید دریافت شد از %s", event.chat_id)

    message = event.message

    # استخراج دکمه‌ها
    button_text = extract_buttons(message)

    # ساخت پیام نهایی
    final_text = (message.text or "") + button_text

    for user_id in target_users:
        try:
            if message.media:
                logger.info("دانلود فایل از پیام...")
                file_path = await message.download_media()
                logger.info("فایل دانلود شد: %s", file_path)

                await client.send_file(user_id, file_path, caption=final_text)
                logger.info("فایل برای %s ارسال شد.", user_id)

                os.remove(file_path)
            else:
                await client.send_message(user_id, final_text)
                logger.info("پیام متنی برای %s ارسال شد.", user_id)

        except Exception as e:
            logger.error("خطا در ارسال پیام به %s: %s", user_id, str(e))


# Keep Alive
async def keep_alive():
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                await session.get("https://google.com")
        except:
            pass
        await asyncio.sleep(300)


# Main
async def main():
    try:
        await client.start(phone=phone_number)
        logger.info("Client شروع شد...")
        await asyncio.gather(
            keep_alive(),
            client.run_until_disconnected()
        )
    except Exception as e:
        logger.critical("خطا در main: %s", str(e))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical("خطای خارج از asyncio.run: %s", str(e))

