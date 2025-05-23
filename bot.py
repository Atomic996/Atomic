import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    AIORateLimiter,
)
from fastapi import FastAPI, Request
from dotenv import load_dotenv
import asyncio

# تحميل المتغيرات من .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# بيانات الدروس
fields = {
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
telegram_app = Application.builder().token(BOT_TOKEN).rate_limiter(AIORateLimiter()).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button_handler))

# إنشاء تطبيق FastAPI
fastapi_app = FastAPI()

@fastapi_app.get("/")
async def root():
    return {"status": "ok"}

@fastapi_app.on_event("startup")
async def on_startup():
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        try:
            await telegram_app.bot.delete_webhook(drop_pending_updates=True)
            await telegram_app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
            print("✅ Webhook configured successfully!")
            break
        except Exception as e:
            retry_count += 1
            print(f"⚠️ Attempt {retry_count} failed: {str(e)}")
            await asyncio.sleep(3)

@fastapi_app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)  # يعمل بدون مشاكل هنا
    await telegram_app.process_update(update)
    return {"ok": True}
