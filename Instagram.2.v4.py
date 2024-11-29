import logging
import requests
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import instaloader

# تنظیمات لاگینگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# توکن ربات
TOKEN = '7809646273:AAHfW6rUi4JuAeOYxZHKNsbrYkaaR7-aOG4'

# تابع شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('سلام به ربات دانلودر اینستاگرام خوش اومدید.')

# تابع دریافت لینک و دانلود
async def download_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    post_links = get_instagram_download_links(url)
    
    if post_links:
        await update.message.reply_text('دانلود در حال انجام است...')
        try:
            for index, post_link in enumerate(post_links):
                response = requests.get(post_link)
                response.raise_for_status()

                # تعیین نوع فایل بر اساس پسوند
                if post_link.endswith('.mp4'):
                    file_name = f'instagram_video_{index + 1}.mp4'
                    with open(file_name, 'wb') as f:
                        f.write(response.content)
                    await update.message.reply_video(video=open(file_name, 'rb'))
                else:
                    file_name = f'instagram_post_{index + 1}.jpg'
                    with open(file_name, 'wb') as f:
                        f.write(response.content)
                    await update.message.reply_photo(photo=open(file_name, 'rb'))

                # حذف فایل پس از ارسال
                os.remove(file_name)

            # پیغام تشکر بعد از دانلود موفقیت‌آمیز
            await update.message.reply_text("با تشکر از شما برای انتخاب ما.")
            
        except Exception as e:
            await update.message.reply_text('خطا در دانلود پست.')
            logging.error(f"Error downloading post: {e}")
    else:
        await update.message.reply_text('لینک معتبر نیست.')

def get_instagram_download_links(url):
    L = instaloader.Instaloader()
    
    try:
        post = instaloader.Post.from_shortcode(L.context, url.split('/')[-2])
        download_links = []
        
        # بررسی هر مدیا در پست
        for index, node in enumerate(post.get_sidecar_nodes() or [post]):
            if node.is_video:
                download_links.append(node.video_url)  # لینک ویدیو را برمی‌گرداند
            else:
                download_links.append(node.display_url)  # لینک عکس را برمی‌گرداند
                
        return download_links
    except Exception as e:
        logging.error(f"Error fetching Instagram post: {e}")
        return None

# تابع اصلی
async def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_post))

    await application.run_polling()

if __name__ == '__main__':
    try:
        import nest_asyncio
        nest_asyncio.apply()
        
        asyncio.run(main())
    except RuntimeError as e:
        logging.error(f"RuntimeError: {e}")

