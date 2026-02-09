# 🚗 Car Service Telegram Bot

A Telegram bot for collecting and processing car service requests.

The bot guides users through a simple request flow:
1. Enter vehicle license plate
2. Select problem type
3. Describe the issue

After submission, the request is automatically forwarded to a service Telegram channel where operators can process incoming requests.

---

## ✨ Features

- Simple step-by-step user interaction
- Clean mobile-friendly message formatting
- Problem categories selection
- Automatic request delivery to service staff
- Easy deployment
- Lightweight and fast
- No database required

---

## 🧩 Request Flow

User interaction in Telegram:

Start bot
↓
Enter vehicle plate
↓
Choose problem category
↓
Describe issue
↓
Request sent to service channel


Service team receives formatted requests like:

🛠 New request
🕒 Time: 2026-02-05 16:20
👤 From: @username
🚗 Vehicle: AA1234BB
📌 Type: Electrical
📝 Description:
Left headlight not working

---

## ⚙️ Requirements

- Python 3.9+
- Telegram Bot Token
- Telegram channel/group for receiving requests

---

## 📦 Installation

Clone repository:
```
git clone https://github.com/yourusername/repository-name.git
cd repository-name
```

Create virtual environment:
```
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```
pip install -r requirements.txt
```

🔐 Environment Configuration (.env)

Sensitive data must not be stored in code.
All secrets are stored in a .env file.

Create a .env file in the project root:
```
touch .env
```

Add the following:
```
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
CHANNEL_ID=-100XXXXXXXXXX
```
Variables explanation
Variable	Description
BOT_TOKEN	Telegram bot token from BotFather
CHANNEL_ID	Telegram channel/group ID where requests are sent
How to get BOT_TOKEN

Open Telegram

Find @BotFather

Create bot using /newbot

Copy API token

How to get CHANNEL_ID

Add bot to your channel/group as admin

Send a message

Use @RawDataBot or similar tools to see chat ID

Channel IDs usually look like:
```
-1001234567890
```
▶️ Running the bot

Start the bot:
```
python index.py
```
Bot will start polling Telegram and become active.
