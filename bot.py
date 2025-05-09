
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# تعريف المحتوى
fields = {
    "frontend": {
        "title": "HTML & CSS",
        "lessons": {
            "html1": "الدرس 1: مقدمة في HTML...",
            "css1": "الدرس 2: تنسيقات CSS..."
        }
    },
    "js": {
        "title": "JavaScript",
        "lessons": {
            "js1": "الدرس 1: المتغيرات والدوال في JavaScript...",
            "js2": "الدرس 2: التعامل مع DOM..."
        }
    },
    "backend": {
        "title": "Backend",
        "lessons": {
            "php1": "الدرس 1: مقدمة في PHP...",
            "db1": "الدرس 2: قواعد البيانات MySQL..."
        }
    }
}

# القائمة الرئيسية
def main_menu():
    keyboard = [
        [InlineKeyboardButton(v["title"], callback_data=k)] for k, v in fields.items()
    ]
    return InlineKeyboardMarkup(keyboard)

# قائمة دروس المجال
def lessons_menu(field_key):
    field = fields[field_key]
    keyboard = [
        [InlineKeyboardButton(title, callback_data=lesson_key)] for lesson_key, title in field["lessons"].items()
    ]
    keyboard.append([InlineKeyboardButton("رجوع", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبًا بك في بوت تطوير الويب!\nاختر أحد المجالات:", reply_markup=main_menu())

# التعامل مع الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data in fields:
        await query.edit_message_text(
            f"اختر درسًا من مجال {fields[data]['title']}:",
            reply_markup=lessons_menu(data)
        )
    elif data == "back_to_main":
        await query.edit_message_text("اختر أحد المجالات:", reply_markup=main_menu())
    else:
        # إظهار الدرس
        for field in fields.values():
            if data in field["lessons"]:
                await query.edit_message_text(
                    text=f"{field['lessons'][data]}",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("رجوع", callback_data="back_to_main")]
                    ])
                )
                break

# شغّل التطبيق
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()
