import os
import asyncio
import aiohttp  # <-- إضافة هذه المكتبة
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    AIORateLimiter,
)
from fastapi import FastAPI, Request
from dotenv import load_dotenv

# تحميل المتغيرات من .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# ... (بقية كود الدروس والقوائم والأوامر كما هو)
    "2d3d": {
        "title": "2D & 3D",
        "lessons": {
            "2d_intro": {
                "text": "الدرس 1: مقدمة في التصميم ثنائي الأبعاد",
                "video": "https://youtu.be/2d_intro"
            },
            "3d_intro": {
                "text": "الدرس 2: مقدمة في التصميم ثلاثي الأبعاد",
                "video": "https://youtu.be/3d_intro"
            }
        }
    },
    "algorithms": {
        "title": "الخوارزميات",
        "lessons": {
            "algo1": {
                "text": "الدرس 1: ما هي الخوارزميات؟",
                "video": "https://youtu.be/algo_intro"
            },
            "algo2": {
                "text": "الدرس 2: خوارزميات الفرز",
                "video": "https://youtu.be/sorting_algo"
            }
        }
    },
    "data_modeling": {
        "title": "نمذجة البيانات",
        "lessons": {
            "modeling1": {
                "text": "الدرس 1: مفاهيم النمذجة",
                "video": "https://youtu.be/data_modeling1"
            },
            "modeling2": {
                "text": "الدرس 2: الكيانات والعلاقات",
                "video": "https://youtu.be/data_modeling2"
            }
        }
    },
    "env_setup": {
        "title": "تحضير بيئة التنفيذ",
        "lessons": {
            "setup1": {
                "text": "الدرس 1: إعداد البيئة",
                "video": "https://youtu.be/env_setup1"
            },
            "setup2": {
                "text": "الدرس 2: تثبيت الحزم المطلوبة",
                "video": "https://youtu.be/env_setup2"
            }
        }
    }
}

# القوائم التفاعلية
def main_menu():
    keyboard = [[InlineKeyboardButton(v["title"], callback_data=k)] for k, v in fields.items()]
    return InlineKeyboardMarkup(keyboard)

def lessons_menu(field_key):
    field = fields[field_key]
    keyboard = [
        [InlineKeyboardButton(lesson["text"].split(":")[0], callback_data=k)]
        for k, lesson in field["lessons"].items()
    ]
    keyboard.append([InlineKeyboardButton("رجوع", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)
# أوامر البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبًا بك في بوت تطوير المهارات!\nاختر أحد الأقسام:", reply_markup=main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data in fields:
        await query.edit_message_text(
            f"اختر درسًا من قسم {fields[data]['title']}:",
            reply_markup=lessons_menu(data)
        )
    elif data == "back_to_main":
        await query.edit_message_text("اختر أحد الأقسام:", reply_markup=main_menu())
    else:
        for field in fields.values():
            if data in field["lessons"]:
                lesson = field["lessons"][data]
                buttons = []
                if "video" in lesson:
                    buttons.append([InlineKeyboardButton("مشاهدة الفيديو", url=lesson["video"])])
                if "pdf" in lesson:
                    buttons.append([InlineKeyboardButton("تحميل PDF", url=lesson["pdf"])])
                buttons.append([InlineKeyboardButton("رجوع", callback_data="back_to_main")])
                await query.edit_message_text(
                    text=lesson.get("text", "لا يوجد شرح نصي."),
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                break
# إنشاء تطبيق Telegram
app = ApplicationBuilder().token(BOT_TOKEN).rate_limiter(AIORateLimiter()).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))

# إنشاء تطبيق FastAPI
fastapi_app = FastAPI()  # <-- يجب تعريفه هنا قبل استخدامه

@fastapi_app.on_event("startup")
async def on_startup():
    await asyncio.sleep(10)  # انتظر 10 ثوانٍ لضمان تشغيل الخدمة
    webhook_url = f"{WEBHOOK_URL}/webhook"
    
    try:
        # اختبر اتصال الخدمة أولاً
        async with aiohttp.ClientSession() as session:
            async with session.get(WEBHOOK_URL) as resp:
                if resp.status != 200:
                    print(f"⚠️ Service returned status: {resp.status}")
                    return

        await app.bot.delete_webhook()
        await app.bot.set_webhook(webhook_url)
        print(f"✅ Webhook set successfully at: {webhook_url}")
        
        # إعلام المطور بنجاح التشغيل
        await app.bot.send_message(
            chat_id=YOUR_CHAT_ID,  # <-- استبدلها برقم شاتك
            text=f"✅ البوت يعمل الآن!\nWEBHOOK: {webhook_url}"
        )
    except Exception as e:
        error_msg = f"❌ فشل إعداد الويب هوك: {str(e)}"
        print(error_msg)
        try:
            await app.bot.send_message(
                chat_id=YOUR_CHAT_ID,  # <-- استبدلها برقم شاتك
                text=error_msg
            )
        except:
            print("⚠️ فشل إرسال رسالة الخطأ")

@fastapi_app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, app.bot)
        await app.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        print(f"❌ خطأ في معالجة الطلب: {str(e)}")
        return {"status": "error"}, 500
