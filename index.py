import os
import re
from datetime import datetime
import html
from dotenv import load_dotenv

load_dotenv()


from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHAT = os.getenv("TARGET_CHAT")

STEP_NUMBER = "number"
STEP_TYPE = "type"
STEP_DESC = "description"
STEP_CONFIRM = "confirm"

PROBLEM_TYPES = [
    ["світло/електрика"],
    ["рідини/олії"],
    ["колеса/ходова"],
    ["салон/кузов"],
    ["інше"],
]

CANCEL_KB = ReplyKeyboardMarkup(
    [["❌ Скасувати"], ["🔁 Почати заново"]], resize_keyboard=True
)

CONFIRM_KB = ReplyKeyboardMarkup(
    [
        ["✅ Відправити"],
        ["✏️ Змінити номер", "✏️ Змінити тип"],
        ["✏️ Змінити опис"],
        ["❌ Скасувати"],
    ],
    resize_keyboard=True,
)


def normalize_plate(s: str) -> str:
    s = (s or "").strip().upper()
    s = s.replace(" ", "").replace("-", "")
    return s


def looks_like_plate(s: str) -> bool:
    s = normalize_plate(s)
    return bool(re.fullmatch(r"[A-ZА-ЯІЇЄ0-9]{5,10}", s))


def sender_label(update: Update) -> str:
    u = update.effective_user
    if not u:
        return "невідомий"
    if u.username:
        return f"@{u.username}"
    name = " ".join([p for p in [u.first_name, u.last_name] if p]).strip()
    return f"{name} (id:{u.id})" if name else f"id:{u.id}"


def build_preview(context: ContextTypes.DEFAULT_TYPE) -> str:
    plate = context.user_data.get("number", "-")
    ptype = context.user_data.get("type", "-")
    desc = context.user_data.get("description", "-")

    return (
        "🧾 *Перевірте заявку перед відправкою:*\n"
        f"🚗 *Авто:* `{plate}`\n"
        f"📌 *Тип:* {ptype}\n"
        f"📝 *Опис:* {desc}\n\n"
        "Якщо все ок — натисніть *«✅ Відправити»*."
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["step"] = STEP_NUMBER
    await update.message.reply_text(
        "Вітаю! Введіть державний номер авто у форматі: 110987", reply_markup=CANCEL_KB
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Ок, скасовано. Напишіть /start щоб почати знову.",
        reply_markup=ReplyKeyboardRemove(),
    )


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["step"] = STEP_NUMBER
    await update.message.reply_text(
        "Почнемо заново. Введіть державний номер авто:", reply_markup=CANCEL_KB
    )


async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chat ID: {update.effective_chat.id}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == "❌ Скасувати":
        return await cancel(update, context)
    if text == "🔁 Почати заново":
        return await restart(update, context)

    step = context.user_data.get("step")

    if step == STEP_NUMBER:
        plate = normalize_plate(text)
        context.user_data["number"] = plate
        context.user_data["step"] = STEP_TYPE

        if not looks_like_plate(plate):
            await update.message.reply_text(
                "⚠️ Номер виглядає незвично. Якщо все ок — продовжуй. Якщо ні — натисни «Почати заново».",
                reply_markup=CANCEL_KB,
            )

        await update.message.reply_text(
            "Оберіть тип проблеми:",
            reply_markup=ReplyKeyboardMarkup(
                PROBLEM_TYPES, one_time_keyboard=True, resize_keyboard=True
            ),
        )
        return

    if step == STEP_TYPE:
        allowed = {row[0] for row in PROBLEM_TYPES}
        if text not in allowed:
            await update.message.reply_text(
                "Будь ласка, обери тип проблеми кнопкою нижче 👇",
                reply_markup=ReplyKeyboardMarkup(
                    PROBLEM_TYPES, one_time_keyboard=True, resize_keyboard=True
                ),
            )
            return

        context.user_data["type"] = text
        context.user_data["step"] = STEP_DESC

        await update.message.reply_text(
            "📝 Опишіть проблему.\n\n"
            "Приклади:\n\n"
            "💡 Світло / електрика\n"
            "• перегоріла ліва лампа\n"
            "• перегорів запобіжник\n\n"
            "🛢 Рідини / олії\n"
            "• долити антифриз\n"
            "• долити омивач\n\n"
            "🛞 Колеса / ходова\n"
            "• спустило колесо\n"
            "• стукає стійка\n\n"
            "🚗 Салон / кузов\n"
            "• брудний салон\n"
            "• пошкоджений бампер",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    if step == STEP_DESC:
        context.user_data["description"] = text
        context.user_data["step"] = STEP_CONFIRM

        await update.message.reply_text(
            build_preview(context), parse_mode="Markdown", reply_markup=CONFIRM_KB
        )
        return

    if step == STEP_CONFIRM:
        if text == "✏️ Змінити номер":
            context.user_data["step"] = STEP_NUMBER
            await update.message.reply_text(
                "Ок. Введіть номер авто ще раз:", reply_markup=CANCEL_KB
            )
            return

        if text == "✏️ Змінити тип":
            context.user_data["step"] = STEP_TYPE
            await update.message.reply_text(
                "Ок. Оберіть тип проблеми:",
                reply_markup=ReplyKeyboardMarkup(
                    PROBLEM_TYPES, one_time_keyboard=True, resize_keyboard=True
                ),
            )
            return

        if text == "✏️ Змінити опис":
            context.user_data["step"] = STEP_DESC
            await update.message.reply_text(
                "Ок. Опишіть проблему ще раз:", reply_markup=ReplyKeyboardRemove()
            )
            return

        if text != "✅ Відправити":
            await update.message.reply_text(
                "Оберіть дію кнопкою нижче 👇", reply_markup=CONFIRM_KB
            )
            return

        # ---- тільки тут відправка ----
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        plate = html.escape(context.user_data.get("number", "-"))
        ptype = html.escape(context.user_data.get("type", "-"))
        desc = html.escape(context.user_data.get("description", "-"))
        sender = html.escape(sender_label(update))

        msg = (
            "🛠 <b>Нова заявка</b>\n"
            f"🕒 <b>Час:</b> {created_at}\n"
            f"👤 <b>Від:</b> {sender}\n"
            f"🚗 <b>Авто:</b> <code>{plate}</code>\n"
            f"📌 <b>Тип:</b> {ptype}\n"
            f"📝 <b>Опис:</b> {desc}"
        )

        try:
            if TARGET_CHAT:
                await context.bot.send_message(
                    chat_id=int(TARGET_CHAT), text=msg, parse_mode="HTML"
                )
            else:
                print(msg)

            await update.message.reply_text(
                "Готово ✅ Відправив команді. Для повторного запуску — /start",
                reply_markup=ReplyKeyboardRemove(),
            )
            context.user_data.clear()
        except Exception as e:
            await update.message.reply_text(
                f"⚠️ Помилка відправки: {e}", reply_markup=ReplyKeyboardRemove()
            )

        return


def main():
    if not TOKEN:
        raise RuntimeError("Не задано BOT_TOKEN у змінних середовища.")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("chatid", chatid))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
