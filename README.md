# 🤖 Telegram Desktop Control Bot

### Upper Right Corner Popup Notifications + Remote Control

A powerful Telegram bot that allows you to control your computer
remotely and display modern popup notifications in the **upper-right
corner** of your screen.

Built with: - Python - Telegram Bot API - Tkinter (GUI popups) -
Requests (HTTP polling)

------------------------------------------------------------------------

## 🚀 Features

✅ Upper-right corner popup notifications\
✅ Modern colored popup styles (Info, Warning, Error, Success, Message,
Shutdown)\
✅ Inline button control panel\
✅ Remote message display\
✅ System status monitoring\
✅ Broadcast messaging to subscribers\
✅ Shutdown & Restart (Admin only)\
✅ Stable long polling (no threading conflicts)\
✅ Low CPU usage

------------------------------------------------------------------------

## 🖥️ Popup Behavior

Popups: - Appear in the **upper-right corner** - Stack automatically -
Auto-close after 5 seconds - Include progress bar animation - Show
elapsed time

------------------------------------------------------------------------

## 📦 Requirements

-   Python 3.8+
-   Windows OS (for popup GUI support)
-   `requests` module

Install dependencies:

    pip install requests

------------------------------------------------------------------------

## ⚙️ Setup Guide

### 1️⃣ Create Telegram Bot

1.  Open Telegram
2.  Search **@BotFather**
3.  Create a new bot
4.  Copy your bot token

### 2️⃣ Get Your Chat ID

1.  Search **@userinfobot**
2.  Press Start
3.  Copy your numeric chat ID

### 3️⃣ Configure `bot_config.json`

Example:

{ "bot_token": "YOUR_NEW_BOT_TOKEN", "chat_id": "YOUR_CHAT_ID",
"computer_name": "your_pc_name" }

⚠️ Never upload your real token to public repositories.

------------------------------------------------------------------------

## ▶️ Running the Bot

    python bot_stable_broadcast_updated.py

If successful, you will see:

    Bot is running!
    Use /menu for button controls

And a startup popup will appear.

------------------------------------------------------------------------

## 📱 Telegram Commands

### 🔘 Button Control Panel

    /menu

### 💬 Manual Commands

    msg COMPUTER_NAME Hello World!
    msg all Broadcast message
    status COMPUTER_NAME
    warning COMPUTER_NAME
    alert COMPUTER_NAME
    test COMPUTER_NAME
    demo
    shutdown COMPUTER_NAME
    restart COMPUTER_NAME
    ping
    help

------------------------------------------------------------------------

## 🔐 Admin System

-   Only the configured `chat_id` can control the computer.

-   Other users can subscribe for broadcasts using:

    /start

------------------------------------------------------------------------

## 📢 Broadcast Feature

Send a global message to all subscribers:

    msg all Your message here

------------------------------------------------------------------------

## 🧠 How It Works

-   Uses Telegram Long Polling
-   Background polling thread
-   Tkinter main thread handles popups
-   Thread-safe update queue
-   Automatic subscriber storage
-   Stable HTTP session with retry support

------------------------------------------------------------------------

## ⚠️ Security Warning

This bot can: - Shutdown your PC - Restart your PC - Display emergency
popups

If your bot token is exposed: 1. Go to @BotFather 2. Revoke token 3.
Generate a new one immediately

Never: - Push real tokens to GitHub - Share config publicly - Hardcode
secrets in code

------------------------------------------------------------------------

## 🛑 Stopping the Bot

Press:

    Ctrl + C

Bot will shut down gracefully.

------------------------------------------------------------------------

## 🛠️ File Structure

    bot_stable_broadcast_updated.py
    bot_config.json
    bot_subscribers.json
    bot_popup_fixed.log

------------------------------------------------------------------------

## 📌 OS Compatibility

  OS                Supported
  ----------------- -----------------
  Windows           ✅ Full Support
  Linux (GUI)       ⚠️ Limited
  MacOS             ⚠️ Untested
  Headless Server   ❌ No Popup GUI

------------------------------------------------------------------------

## 📜 License

MIT License (You may modify and distribute freely)

------------------------------------------------------------------------

## 👨‍💻 Author

Telegram Desktop Control Bot -- Remote popup & system control utility.

------------------------------------------------------------------------

# ⭐ If you like this project, consider starring the repo!
