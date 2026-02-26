#!/usr/bin/env python3
"""
TELEGRAM BOT - UPPER RIGHT CORNER POPUPS WITH BUTTONS
FIXED VERSION - NO THREADING ERRORS
CONFIGURATION LOADED FROM FILE ONLY
"""

import os
import sys
import time
import json
import platform
import socket
from datetime import datetime
import logging
import threading
import ctypes
import requests
import tkinter as tk

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from tkinter import font
import queue

# Setup logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("bot_popup_fixed.log")]
)

print("=" * 60)
print("🤖 TELEGRAM BOT WITH UPPER RIGHT POPUPS - FIXED")
print("=" * 60)

class UpperRightPopup:
    """Fixed version - no threading issues"""
    
    def __init__(self):
        self.popup_queue = queue.Queue()
        self.active_popups = []
        self.running = True
        self.popup_id_counter = 0
        
        # Get screen size
        try:
            self.root = tk.Tk()
            self.root.withdraw()  # Hide the main window
            self.screen_width = self.root.winfo_screenwidth()
            self.screen_height = self.root.winfo_screenheight()
        except:
            self.screen_width = 1920
            self.screen_height = 1080
        
        print(f"[POPUP] Screen: {self.screen_width}x{self.screen_height}")
        
        # Colors for different styles
        self.colors = {
            "info": {"bg": "#2196F3", "fg": "white", "icon": "💡"},
            "warning": {"bg": "#FF9800", "fg": "white", "icon": "⚠️"},
            "error": {"bg": "#F44336", "fg": "white", "icon": "❌"},
            "success": {"bg": "#4CAF50", "fg": "white", "icon": "✅"},
            "message": {"bg": "#9C27B0", "fg": "white", "icon": "📨"},
            "shutdown": {"bg": "#607D8B", "fg": "white", "icon": "🖥️"}
        }
        
        # Start popup checker in main thread
        self.root.after(100, self._check_popup_queue)
        
        print("[POPUP] System ready - Popups will appear in UPPER RIGHT")
    
    def show(self, title: str, message: str, style: str = "info"):
        """Show popup in upper right corner"""
        print(f"[POPUP] Queued: {title}")
        self.popup_queue.put((title, message, style))
        return True
    
    def _check_popup_queue(self):
        """Check for new popups - runs in main thread"""
        try:
            # Process all queued popups
            while not self.popup_queue.empty():
                title, message, style = self.popup_queue.get_nowait()
                self._create_popup(title, message, style)
                self.popup_queue.task_done()
        except queue.Empty:
            pass
        except Exception as e:
            print(f"[POPUP] Queue error: {e}")
        
        # Schedule next check
        if self.running:
            self.root.after(100, self._check_popup_queue)
    
    def _create_popup(self, title: str, message: str, style: str):
        """Create popup - ALL in main thread"""
        try:
            # Get colors for this style
            colors = self.colors.get(style, self.colors["info"])
            
            # Create the popup window
            popup = tk.Toplevel()
            popup.overrideredirect(True)  # Remove window decorations
            popup.attributes('-topmost', True)  # Always on top
            
            # Set position - UPPER RIGHT CORNER
            popup_width = 350
            popup_height = 140
            
            # Calculate position
            x_position = self.screen_width - popup_width - 20  # 20px from right edge
            y_position = 20  # 20px from top
            
            # If we have active popups, stack them
            if self.active_popups:
                y_position = 20 + (len(self.active_popups) * (popup_height + 10))
            
            popup.geometry(f"{popup_width}x{popup_height}+{x_position}+{y_position}")
            
            print(f"[POPUP] Creating at position: {x_position}, {y_position}")
            
            # Configure window
            popup.configure(bg=colors["bg"])
            
            # Create main frame
            main_frame = tk.Frame(popup, bg=colors["bg"])
            main_frame.pack(fill="both", expand=True, padx=1, pady=1)
            
            # Title bar with icon
            title_frame = tk.Frame(main_frame, bg=colors["bg"])
            title_frame.pack(fill="x", padx=15, pady=(10, 5))
            
            # Icon
            tk.Label(
                title_frame,
                text=colors["icon"],
                font=("Arial", 14),
                bg=colors["bg"],
                fg=colors["fg"]
            ).pack(side="left", padx=(0, 10))
            
            # Title
            tk.Label(
                title_frame,
                text=title,
                font=("Arial", 12, "bold"),
                bg=colors["bg"],
                fg=colors["fg"]
            ).pack(side="left", fill="x", expand=True)
            
            # Close button (X)
            close_btn = tk.Label(
                title_frame,
                text="✕",
                font=("Arial", 12, "bold"),
                bg=colors["bg"],
                fg=colors["fg"],
                cursor="hand2"
            )
            close_btn.pack(side="right")
            close_btn.bind("<Button-1>", lambda e, p=popup: self._close_popup(p))
            
            # Message content
            tk.Label(
                main_frame,
                text=message,
                font=("Arial", 10),
                bg=colors["bg"],
                fg=colors["fg"],
                wraplength=popup_width - 30,
                justify="left"
            ).pack(padx=15, pady=(0, 10), fill="x")
            
            # Progress bar frame
            progress_frame = tk.Frame(main_frame, bg=colors["bg"])
            progress_frame.pack(fill="x", padx=15, pady=(0, 10))
            
            # Progress bar background
            progress_bg = tk.Frame(progress_frame, bg="#444", height=3)
            progress_bg.pack(fill="x")
            progress_bg.pack_propagate(False)
            
            # Progress bar (will be animated)
            progress_var = tk.IntVar(value=0)
            progress_bar = tk.Frame(progress_bg, bg=colors["fg"], height=3, width=0)
            progress_bar.place(relx=0, rely=0, anchor="nw")
            
            # Time label
            time_label = tk.Label(
                main_frame,
                text="Just now",
                font=("Arial", 8),
                bg=colors["bg"],
                fg=colors["fg"]
            )
            time_label.pack(side="left", padx=15)
            
            # Store popup data
            popup_data = {
                "window": popup,
                "progress_bar": progress_bar,
                "time_label": time_label,
                "start_time": time.time(),
                "created": time.time()
            }
            self.active_popups.append(popup_data)
            
            # Start animations using after() - NO THREADING
            self._start_animations(popup_data)
            
            print(f"[POPUP] ✓ Popup shown: {title}")
            
        except Exception as e:
            print(f"[POPUP] Failed: {e}")
            self._fallback_popup(title, message)
    
    def _start_animations(self, popup_data):
        """Start all animations for a popup"""
        popup = popup_data["window"]
        
        if not popup.winfo_exists():
            return
        
        # Animate progress bar
        def animate_progress(step=0):
            if step <= 100 and popup.winfo_exists():
                width = int(320 * (step / 100))
                popup_data["progress_bar"].configure(width=width)
                popup.after(50, lambda: animate_progress(step + 1))
            elif popup.winfo_exists():
                popup.destroy()
                if popup_data in self.active_popups:
                    self.active_popups.remove(popup_data)
        
        # Update time label
        def update_time():
            if popup.winfo_exists():
                elapsed = int(time.time() - popup_data["start_time"])
                if elapsed < 60:
                    time_text = f"{elapsed}s ago"
                else:
                    time_text = f"{elapsed//60}m ago"
                
                popup_data["time_label"].config(text=time_text)
                popup.after(1000, update_time)
        
        # Start animations
        popup.after(100, lambda: animate_progress())
        popup.after(100, update_time)
        
        # Auto close after 5 seconds
        popup.after(5000, lambda: self._close_popup(popup))
    
    def _close_popup(self, popup):
        """Close popup"""
        if popup.winfo_exists():
            # Find and remove from active popups
            for popup_data in self.active_popups[:]:
                if popup_data["window"] == popup:
                    self.active_popups.remove(popup_data)
                    break
            
            # Destroy the window
            try:
                popup.destroy()
            except:
                pass
    
    def _fallback_popup(self, title: str, message: str):
        """Simple fallback"""
        try:
            print(f"\n[POPUP] {title}: {message}\n")
        except:
            pass
    
    def cleanup(self):
        """Cleanup"""
        self.running = False
        for popup_data in self.active_popups:
            try:
                popup_data["window"].destroy()
            except:
                pass
    
    def update(self):
        """Update the tkinter mainloop"""
        try:
            self.root.update()
        except:
            pass

class TelegramBot:
    def __init__(self):
        """Initialize bot"""
        self.config = self._load_config()
        self.bot_token = self.config.get('bot_token', '')
        self.chat_id = str(self.config.get('chat_id', ''))
        self.computer_name = self.config.get('computer_name', platform.node())
        self.running = True
        self.last_update_id = 0
        self._update_id_lock = threading.Lock()
        self.popup = UpperRightPopup()
        self.http = self._build_http_session()
        self.update_queue = queue.Queue()
        self._poller_thread = None

        # Multi-chat (broadcast) support
        # - chat_id in config is treated as the ADMIN chat (full control)
        # - any chat that messages the bot can be registered as a subscriber
        # - "msg all <text>" broadcasts to all subscribers
        self.admin_chat_id = str(self.chat_id)
        self.subscribers_file = "bot_subscribers.json"
        self.subscribers = self._load_subscribers()
        # Ensure admin is always subscribed
        self._register_subscriber(self.admin_chat_id)
        
        # Validate critical configuration
        if not self.bot_token:
            print("❌ ERROR: bot_token not found in config file")
            sys.exit(1)
        
        if not self.chat_id or self.chat_id == "YOUR_CHAT_ID_HERE":
            print("❌ ERROR: chat_id not configured in config file")
            print("📱 Get Chat ID from @userinfobot on Telegram")
            print(f"💡 Edit bot_config.json and set your chat_id")
            sys.exit(1)
        
        print(f"Computer: {self.computer_name}")
        print(f"System: {platform.system()}")
        print(f"Popups: UPPER RIGHT CORNER")
        print("=" * 60)
    
    def _load_config(self):
        """Load configuration from file ONLY"""
        config_file = "bot_config.json"
        
        if not os.path.exists(config_file):
            print(f"❌ Config file not found: {config_file}")
            print(f"📝 Creating {config_file}...")
            
            # Get bot token from user input
            print("\n" + "=" * 60)
            print("🤖 BOT SETUP REQUIRED")
            print("=" * 60)
            print("\nTo get started, you need:")
            print("1. Create a bot with @BotFather on Telegram")
            print("2. Get your bot token (looks like: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz)")
            print("3. Get your Chat ID from @userinfobot")
            print("\n" + "=" * 60)
            
            bot_token = input("\nEnter your bot token: ").strip()
            
            if not bot_token:
                print("❌ Bot token is required!")
                sys.exit(1)
            
            # Create config with user input
            config = {
                "bot_token": bot_token,
                "chat_id": "YOUR_CHAT_ID_HERE",
                "computer_name": platform.node()
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Created {config_file}")
            print("⚠️ Please edit it and add your Chat ID")
            print("📱 Get Chat ID from @userinfobot on Telegram")
            print("\nSteps:")
            print("1. Message @userinfobot on Telegram")
            print("2. It will reply with your Chat ID")
            print("3. Copy the ID and paste in bot_config.json")
            print("4. Run this script again")
            input("\nPress Enter to exit...")
            sys.exit(0)
        
        try:
            # Read and clean the config file
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove any control characters
            import re
            content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)
            
            config = json.loads(content)
            
            print(f"✓ Config loaded from: {config_file}")
            return config
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {config_file}: {e}")
            print("💡 Try deleting the file and running the script again")
            sys.exit(1)

        except Exception as e:
            print(f"❌ Error loading config: {e}")
            sys.exit(1)

    def _load_subscribers(self):
        """Load subscriber chat IDs from a local JSON file."""
        try:
            if not os.path.exists(self.subscribers_file):
                return set()
            with open(self.subscribers_file, 'r', encoding='utf-8') as f:
                data = json.load(f) or {}
            ids = data.get('subscribers', [])
            return set(str(x) for x in ids if str(x).strip())
        except Exception:
            return set()

    def _save_subscribers(self):
        """Persist subscriber chat IDs to disk."""
        try:
            payload = {
                'subscribers': sorted(self.subscribers),
                'updated_at': datetime.now().isoformat(timespec='seconds')
            }
            with open(self.subscribers_file, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _register_subscriber(self, chat_id: str):
        """Register a chat as a subscriber (for broadcast)."""
        cid = str(chat_id).strip()
        if not cid:
            return False
        if cid not in self.subscribers:
            self.subscribers.add(cid)
            self._save_subscribers()
            return True
        return False

    def _unregister_subscriber(self, chat_id: str):
        """Remove a chat from subscribers."""
        cid = str(chat_id).strip()
        if cid in self.subscribers:
            self.subscribers.remove(cid)
            self._save_subscribers()
            return True
        return False
    

    def _build_http_session(self) -> requests.Session:
        """Create a requests session with retries and connection pooling (more stable, less lag)."""
        session = requests.Session()
        retry = Retry(
            total=5,
            connect=5,
            read=5,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET", "POST")
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        # Telegram API prefers keep-alive; Session handles this automatically.
        return session

    def _safe_post(self, url: str, **kwargs):
        """Wrapper around session.post with sane defaults."""
        kwargs.setdefault("timeout", 15)
        return self.http.post(url, **kwargs)

    def _safe_get(self, url: str, **kwargs):
        """Wrapper around session.get with sane defaults."""
        kwargs.setdefault("timeout", 45)
        return self.http.get(url, **kwargs)


    def _schedule_popup(self, delay_s: float, title: str, message: str, style: str):
        """Schedule a popup from the Tk main thread without spawning extra threads."""
        try:
            ms = int(max(0, delay_s) * 1000)
            self.popup.root.after(ms, lambda: self.show_notification(title, message, style))
        except Exception:
            # Fallback: just queue immediately
            self.show_notification(title, message, style)

    def show_notification(self, title: str, message: str, style: str = "info"):
        """Show notification"""
        return self.popup.show(title, message, style)
    
    def send_telegram_to(self, chat_id: str, text: str, reply_markup=None):
        """Send a Telegram message to a specific chat_id."""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': str(chat_id),
                'text': text,
                'parse_mode': 'HTML'
            }
            if reply_markup:
                payload['reply_markup'] = reply_markup
            response = self._safe_post(url, json=payload, timeout=15)
            return response.status_code == 200
        except Exception as e:
            print(f"[TELEGRAM] Error: {e}")
            return False

    def send_telegram(self, text: str, reply_markup=None):
        """Send Telegram message to the configured admin chat (backwards compatible)."""
        return self.send_telegram_to(self.admin_chat_id, text, reply_markup)

    def broadcast_telegram(self, text: str):
        """Broadcast a Telegram message to all registered subscriber chats."""
        ok_any = False
        for cid in sorted(self.subscribers):
            ok_any = self.send_telegram_to(cid, text) or ok_any
        return ok_any
    
    def send_buttons_to(self, chat_id: str, text: str, buttons: list):
        """Send message with inline keyboard buttons to a specific chat."""
        try:
            keyboard = []
            row = []

            for i, button in enumerate(buttons):
                row.append({
                    "text": button["text"],
                    "callback_data": button["data"]
                })

                # Add new row after every 2 buttons for better layout
                if len(row) == 2 or i == len(buttons) - 1:
                    keyboard.append(row)
                    row = []

            reply_markup = {
                "inline_keyboard": keyboard
            }

            return self.send_telegram_to(chat_id, text, reply_markup)

        except Exception as e:
            print(f"[BUTTONS] Error: {e}")
            return self.send_telegram_to(chat_id, text)  # Fallback to plain text

    def send_buttons(self, text: str, buttons: list):
        """Send buttons to the configured admin chat (backwards compatible)."""
        return self.send_buttons_to(self.admin_chat_id, text, buttons)
    
    def get_updates(self):
        """Get Telegram updates"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"

            with self._update_id_lock:
                offset = self.last_update_id + 1

            params = {
                'offset': offset,
                'timeout': 30
            }

            response = self._safe_get(url, params=params, timeout=45)
            data = response.json()

            if data.get('ok') and data.get('result'):
                return data['result']

        except Exception as e:
            print(f"[UPDATES] Error: {e}")

        return []

    def answer_callback_query(self, callback_query_id: str):
        """Answer callback query to remove loading state"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/answerCallbackQuery"
            payload = {
                'callback_query_id': callback_query_id
            }
            
            response = self._safe_post(url, json=payload, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def process_command(self, command: str, update_id: int, sender_chat_id: str):
        """Process Telegram command.

        - Admin chat (config chat_id) can control the PC.
        - Non-admin chats are allowed to /start (subscribe) and receive broadcasts.
        """
        sender_chat_id = str(sender_chat_id)
        is_admin = sender_chat_id == self.admin_chat_id

        # Auto-register anyone who messages the bot (for broadcast)
        self._register_subscriber(sender_chat_id)

        print(f"📨 Command from {sender_chat_id}: {command}")
        
        # Split command
        parts = command.strip().split(maxsplit=2)
        if len(parts) < 1:
            return
        
        action = parts[0].lower()
        
        # Handle button commands (start with /)
        if action.startswith('/'):
            action = action[1:]  # Remove the slash
        
        # /start works for everyone (subscribe) and shows info.
        if action == "start":
            self.send_telegram_to(
                sender_chat_id,
                "✅ Subscribed! You will receive global broadcasts from this bot.\n\n"
                "If you are the admin, use /menu for controls."
            )
            if is_admin:
                # Admin gets the full control panel.
                self.process_command("/menu", update_id, sender_chat_id)
            return

        # /menu is admin-only
        if action == "menu":
            if not is_admin:
                self.send_telegram_to(sender_chat_id, "⛔ Unauthorized. Only the admin chat can open the control panel.")
                return

            self.send_buttons(
                f"🤖 <b>{self.computer_name} Control Panel</b>\n\n"
                "Select an option below:",
                [
                    {"text": "📊 Status", "data": "status"},
                    {"text": "📨 Send Message", "data": "send_msg"},
                    {"text": "⚠️ Warning", "data": "warning"},
                    {"text": "🚨 Alert", "data": "alert"},
                    {"text": "🧪 Test Popups", "data": "test"},
                    {"text": "🎬 Demo", "data": "demo"},
                    {"text": "🖥️ Shutdown", "data": "shutdown_confirm"},
                    {"text": "🔄 Restart", "data": "restart_confirm"},
                    {"text": "📋 Help", "data": "help"},
                    {"text": "🏓 Ping", "data": "ping"}
                ]
            )
            return

        # Non-admins can still ask for basic info
        if not is_admin:
            if action in {"help", "ping", "status"}:
                # treat like "status all" etc is not required for these
                if action == "ping":
                    self.send_telegram_to(sender_chat_id, "🏓 Pong! You are subscribed for broadcasts.")
                    return
                if action == "help":
                    self.send_telegram_to(sender_chat_id,
                        "<b>Bot commands</b>\n\n"
                        "<code>/start</code> - Subscribe to broadcasts\n"
                        "<code>msg all &lt;text&gt;</code> - (Admin only) broadcast to everyone\n"
                        "\nIf you need admin access, ask the owner to add you.")
                    return
                if action == "status":
                    # For non-admins, just show that bot is running (no device control)
                    ip = self.get_local_ip()
                    self.send_telegram_to(sender_chat_id,
                        f"<b>{self.computer_name}</b> is online.\n"
                        f"🌐 IP: {ip}\n"
                        f"🕐 Time: {datetime.now().strftime('%H:%M:%S')}")
                    return

            self.send_telegram_to(sender_chat_id, "⛔ Unauthorized. Use /start to subscribe, or contact the admin.")
            return
            
        # Check if command has target
        if len(parts) < 2:
            return
        
        target = parts[1].lower()
        
        # Check if command is for this computer
        if target not in [self.computer_name.lower(), "all"]:
            print(f"⚠️ Command not for us: {target}")
            return
        
        # Process different commands
        if action == "msg":
            if len(parts) >= 3:
                message = parts[2]

                # Global broadcast: msg all <text>
                if target == "all":
                    self.broadcast_telegram(f"📢 <b>Broadcast</b>\n{message}")
                    self.send_telegram(f"✅ Broadcast sent to {len(self.subscribers)} subscriber(s).")
                    # Local popup on this device (admin machine)
                    self.show_notification("📢 BROADCAST", message, "message")
                    return

                # Regular per-device message: msg <computer_name> <text>
                self.send_telegram(f"📨 Message sent to {self.computer_name}")
                self.show_notification(
                    "📩 NEW MESSAGE",
                    f"From Admin:\n{message}",
                    "message"
                )
                
        elif action == "warning":
            self.send_telegram(f"⚠️ Warning on {self.computer_name}")
            self.show_notification("⚠️ SECURITY WARNING", 
                                 "Autoshutdown Turn On!",
                                 "warning")
            
        elif action == "alert":
            self.send_telegram(f"🚨 Alert on {self.computer_name}")
            self.show_notification("🚨 EMERGENCY", 
                                 "URGENT ACTION REQUIRED!\nSystem security alert",
                                 "error")
            
        elif action == "test":
            self.send_telegram(f"🧪 Testing popups on {self.computer_name}")
            self.show_notification("✅ POPUP TEST", 
                                 "Testing popup system!\nPopups should appear in UPPER RIGHT CORNER\nIf you see this, it's working!",
                                 "success")
            
            # Show multiple test popups with delays (no extra threads)
            self._schedule_popup(0.5, "💡 INFO TEST", "Info style popup", "info")
            self._schedule_popup(1.0, "⚠️ WARNING TEST", "Warning style popup", "warning")
            self._schedule_popup(1.5, "✅ SUCCESS TEST", "Success style popup", "success")
            
        elif action == "status":
            ip = self.get_local_ip()
            status_msg = f"""
<b>{self.computer_name} Status</b>
🏢 OS: {platform.system()}
🌐 IP: {ip}
🕐 Time: {datetime.now().strftime('%H:%M:%S')}
🤖 Bot: 🟢 ONLINE
📍 Popups: UPPER RIGHT CORNER
"""
            self.send_telegram(status_msg)
            
        elif action == "shutdown":
            self.send_telegram(f"🖥️ Shutdown command for {self.computer_name}")
            self.show_notification("🖥️ SHUTDOWN", 
                                 "Computer will shutdown in 5 seconds!\n\n⚠️ SAVE YOUR WORK NOW!",
                                 "shutdown")
            threading.Thread(target=self.shutdown_computer, daemon=True).start()
            
        elif action == "restart":
            self.send_telegram(f"🔄 Restart command for {self.computer_name}")
            self.show_notification("🔄 RESTART", 
                                 "Computer will restart in 5 seconds!\n\n⚠️ SAVE YOUR WORK NOW!",
                                 "warning")
            threading.Thread(target=self.restart_computer, daemon=True).start()
            
        elif action == "ping":
            self.send_telegram(f"🏓 Pong! {self.computer_name} is alive!")
            
        elif action == "demo":
            self.send_telegram(f"🎬 Popup demo on {self.computer_name}")
            self.show_notification("🎬 DEMO START", "Showing popup demo...", "info")
            
            # Show all popup styles with delays (no extra threads)
            styles = ["info", "warning", "error", "success", "message", "shutdown"]
            for i, style in enumerate(styles):
                self._schedule_popup(i * 0.8, f"{style.upper()} DEMO", f"This is {style} style popup", style)
            
        elif action == "help":
            help_text = f"""
<b>{self.computer_name} Control Bot</b>

<code>msg {self.computer_name} [text]</code> - Send message
<code>msg all [text]</code> - Broadcast message to all subscribers
<code>warning {self.computer_name}</code> - Show warning
<code>alert {self.computer_name}</code> - Emergency alert
<code>status {self.computer_name}</code> - System status
<code>shutdown {self.computer_name}</code> - Shutdown computer
<code>restart {self.computer_name}</code> - Restart computer
<code>ping</code> - Check bot status
<code>test {self.computer_name}</code> - Test popups
<code>demo</code> - Show popup demo
<code>help</code> - Show this help

📍 Popups appear in UPPER RIGHT CORNER

🔘 <b>Use /menu for button controls!</b>
"""
            self.send_telegram(help_text)
            
        else:
            self.send_telegram(f"❌ Unknown command: {action}")
    
    def process_callback_query(self, callback_data: str, callback_query_id: str):
        """Process button callback queries"""
        print(f"🔘 Button pressed: {callback_data}")
        
        # Answer the callback query to remove loading state
        self.answer_callback_query(callback_query_id)
        
        if callback_data == "status":
            ip = self.get_local_ip()
            status_msg = f"""
<b>{self.computer_name} Status</b>
🏢 OS: {platform.system()}
🌐 IP: {ip}
🕐 Time: {datetime.now().strftime('%H:%M:%S')}
🤖 Bot: 🟢 ONLINE
📍 Popups: UPPER RIGHT CORNER
"""
            self.send_telegram(status_msg)
            
        elif callback_data == "send_msg":
            self.send_buttons(
                f"📨 Send message to {self.computer_name}\n\n"
                "Choose a message type:",
                [
                    {"text": "ℹ️ Info", "data": "msg_info"},
                    {"text": "⚠️ Warning", "data": "msg_warning"},
                    {"text": "✅ Success", "data": "msg_success"},
                    {"text": "🚨 Emergency", "data": "msg_emergency"},
                    {"text": "🔙 Back", "data": "menu"}
                ]
            )
            
        elif callback_data == "msg_info":
            self.send_telegram(f"📨 Sending info message to {self.computer_name}")
            self.show_notification("ℹ️ INFO MESSAGE", 
                                 "This is an information message from Telegram!\nSent via buttons.",
                                 "info")
            
        elif callback_data == "msg_warning":
            self.send_telegram(f"⚠️ Sending warning to {self.computer_name}")
            self.show_notification("⚠️ WARNING MESSAGE", 
                                 "Warning! System check required!\nSent via buttons.",
                                 "warning")
            
        elif callback_data == "msg_success":
            self.send_telegram(f"✅ Sending success message to {self.computer_name}")
            self.show_notification("✅ SUCCESS MESSAGE", 
                                 "Operation completed successfully!\nSent via buttons.",
                                 "success")
            
        elif callback_data == "msg_emergency":
            self.send_telegram(f"🚨 Sending emergency alert to {self.computer_name}")
            self.show_notification("🚨 EMERGENCY ALERT", 
                                 "EMERGENCY! Immediate action required!\nSent via buttons.",
                                 "error")
            
        elif callback_data == "warning":
            self.send_telegram(f"⚠️ Warning on {self.computer_name}")
            self.show_notification("⚠️ SECURITY WARNING", 
                                 "Security alert triggered via button!\nAutoshutdown protocols active!",
                                 "warning")
            
        elif callback_data == "alert":
            self.send_telegram(f"🚨 Alert on {self.computer_name}")
            self.show_notification("🚨 EMERGENCY ALERT", 
                                 "URGENT ACTION REQUIRED!\nEmergency alert triggered via button!",
                                 "error")
            
        elif callback_data == "test":
            self.send_telegram(f"🧪 Testing popups on {self.computer_name}")
            self.show_notification("✅ BUTTON TEST", 
                                 "Testing popup system via buttons!\nPopups should appear in UPPER RIGHT CORNER",
                                 "success")
            
            # Show test popups (no extra threads)
            self._schedule_popup(0.5, "💡 BUTTON TEST", "Info popup via button", "info")
            self._schedule_popup(1.0, "⚠️ BUTTON TEST", "Warning popup via button", "warning")
            self._schedule_popup(1.5, "✅ BUTTON TEST", "Success popup via button", "success")
            
        elif callback_data == "demo":
            self.send_telegram(f"🎬 Popup demo on {self.computer_name}")
            self.show_notification("🎬 BUTTON DEMO", "Showing popup demo via buttons...", "info")
            
            # Show all popup styles with delays (no extra threads)
            styles = ["info", "warning", "error", "success", "message", "shutdown"]
            for i, style in enumerate(styles):
                self._schedule_popup(i * 0.8, f"{style.upper()} DEMO", f"This is {style} style popup", style)
            
        elif callback_data == "shutdown_confirm":
            self.send_buttons(
                f"🖥️ Confirm Shutdown for {self.computer_name}\n\n"
                "⚠️ <b>WARNING:</b> This will shutdown the computer immediately!",
                [
                    {"text": "✅ Yes, Shutdown Now", "data": "shutdown_now"},
                    {"text": "❌ Cancel", "data": "menu"}
                ]
            )
            
        elif callback_data == "shutdown_now":
            self.send_telegram(f"🖥️ Shutdown command for {self.computer_name}")
            self.show_notification("🖥️ SHUTDOWN", 
                                 "Computer will shutdown in 5 seconds!\n\n⚠️ SAVE YOUR WORK NOW!\nTriggered via button.",
                                 "shutdown")
            threading.Thread(target=self.shutdown_computer, daemon=True).start()
            
        elif callback_data == "restart_confirm":
            self.send_buttons(
                f"🔄 Confirm Restart for {self.computer_name}\n\n"
                "⚠️ <b>WARNING:</b> This will restart the computer immediately!",
                [
                    {"text": "✅ Yes, Restart Now", "data": "restart_now"},
                    {"text": "❌ Cancel", "data": "menu"}
                ]
            )
            
        elif callback_data == "restart_now":
            self.send_telegram(f"🔄 Restart command for {self.computer_name}")
            self.show_notification("🔄 RESTART", 
                                 "Computer will restart in 5 seconds!\n\n⚠️ SAVE YOUR WORK NOW!\nTriggered via button.",
                                 "warning")
            threading.Thread(target=self.restart_computer, daemon=True).start()
            
        elif callback_data == "ping":
            self.send_telegram(f"🏓 Pong! {self.computer_name} is alive and responding to buttons!")
            
        elif callback_data == "help":
            help_text = f"""
<b>{self.computer_name} Control Bot - Buttons Edition</b>

🔘 <b>Button Controls:</b>
• 📊 Status - Check system status
• 📨 Send Message - Send different message types
• ⚠️ Warning - Show warning popup
• 🚨 Alert - Show emergency alert
• 🧪 Test Popups - Test popup system
• 🎬 Demo - Show all popup styles
• 🖥️ Shutdown - Shutdown computer
• 🔄 Restart - Restart computer
• 📋 Help - Show this help
• 🏓 Ping - Check if bot is alive

📍 Popups appear in UPPER RIGHT CORNER

💡 <b>You can still type commands:</b>
<code>/menu</code> - Show control panel
<code>test {self.computer_name}</code> - Test popups
<code>status {self.computer_name}</code> - Get status
"""
            self.send_telegram(help_text)
            
        elif callback_data == "menu":
            # Return to main menu
            self.send_buttons(
                f"🤖 <b>{self.computer_name} Control Panel</b>\n\n"
                "Select an option below:",
                [
                    {"text": "📊 Status", "data": "status"},
                    {"text": "📨 Send Message", "data": "send_msg"},
                    {"text": "⚠️ Warning", "data": "warning"},
                    {"text": "🚨 Alert", "data": "alert"},
                    {"text": "🧪 Test Popups", "data": "test"},
                    {"text": "🎬 Demo", "data": "demo"},
                    {"text": "🖥️ Shutdown", "data": "shutdown_confirm"},
                    {"text": "🔄 Restart", "data": "restart_confirm"},
                    {"text": "📋 Help", "data": "help"},
                    {"text": "🏓 Ping", "data": "ping"}
                ]
            )
    
    def get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.5)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "Unknown"
    
    def shutdown_computer(self):
        """Shutdown the computer"""
        time.sleep(5)
        if platform.system() == 'Windows':
            os.system("shutdown /s /f /t 1")
        elif platform.system() == 'Linux':
            os.system("shutdown -h now")
    
    def restart_computer(self):
        """Restart the computer"""
        time.sleep(5)
        if platform.system() == 'Windows':
            os.system("shutdown /r /f /t 1")
        elif platform.system() == 'Linux':
            os.system("reboot")
    

    def _poll_updates_forever(self):
        """Background long-polling loop that pushes Telegram updates into a thread-safe queue."""
        backoff = 1.0
        while self.running:
            try:
                updates = self.get_updates()
                if updates:
                    # Advance last_update_id here to prevent duplicates caused by re-fetching the same updates
                    max_id = 0
                    for u in updates:
                        uid = u.get("update_id") or 0
                        if uid > max_id:
                            max_id = uid

                    if max_id:
                        with self._update_id_lock:
                            if max_id > self.last_update_id:
                                self.last_update_id = max_id

                    self.update_queue.put(updates)

                backoff = 1.0  # reset after a successful call
            except Exception as e:
                # Avoid tight retry loops on network issues
                print(f"[POLL] Error: {e}")
                time.sleep(backoff)
                backoff = min(backoff * 2, 30)



    def _drain_updates_queue(self):
        """Process queued updates in the Tk main thread."""
        try:
            while True:
                updates = self.update_queue.get_nowait()
                for update in updates:
                    update_id = update.get('update_id')
                    self.last_update_id = max(self.last_update_id, update_id or 0)

                    # Buttons
                    if 'callback_query' in update:
                        callback_query = update['callback_query']
                        callback_data = callback_query.get('data', '')
                        callback_query_id = callback_query.get('id', '')
                        if callback_data:
                            self.process_callback_query(callback_data, callback_query_id)

                    # Messages
                    message = update.get('message', {})
                    text = (message.get('text') or '').strip()
                    chat_id = str(message.get('chat', {}).get('id', ''))
                    if text and chat_id:
                        self.process_command(text, update_id, chat_id)

                self.update_queue.task_done()
        except queue.Empty:
            pass
        except Exception as e:
            print(f"[MAIN] Update processing error: {e}")

        # Schedule next drain
        if self.running:
            self.popup.root.after(100, self._drain_updates_queue)

    def _graceful_stop(self):
        """Stop bot + clean up UI."""
        if not self.running:
            return
        self.running = False
        try:
            self.send_telegram(f"⏹️ Bot stopped: {self.computer_name}")
        except Exception:
            pass
        try:
            self.show_notification("🤖 BOT STOPPED", "Telegram bot has been stopped", "info")
        except Exception:
            pass
        try:
            self.popup.cleanup()
        except Exception:
            pass
        try:
            self.popup.root.quit()
        except Exception:
            pass

    def run(self):
        """Run bot using Tk's event loop (low CPU, stable)."""
        # Startup notifications
        self.show_notification(
            "🤖 BOT STARTED",
            f"{self.computer_name} is now active!\n\nUse /menu for button controls!",
            "info"
        )

        startup_msg = f"""
🚀 {self.computer_name} is online!
📍 Popups enabled in UPPER RIGHT CORNER

💡 <b>New Feature:</b> Button Controls!
Type <code>/menu</code> or use buttons below:
        """

        self.send_buttons(startup_msg, [
            {"text": "📋 Open Control Panel", "data": "menu"},
            {"text": "🧪 Test Popups", "data": "test"},
            {"text": "📊 System Status", "data": "status"}
        ])

        print("\n✅ Bot is running!")
        print("📍 Popups will appear in UPPER RIGHT CORNER")
        print("🔘 Button controls available!")
        print("\n📱 Try these commands from Telegram:")
        print("  /menu - Show control panel with buttons")
        print(f"  test {self.computer_name}")
        print(f"  msg {self.computer_name} Hello World!")
        print(f"  status {self.computer_name}")
        print("  demo")
        print("\n🛑 Press Ctrl+C to stop")
        print("=" * 60)

        # Start background poller (Telegram long polling; doesn't block UI)
        self._poller_thread = threading.Thread(target=self._poll_updates_forever, daemon=True)
        self._poller_thread.start()

        # Drain updates in main thread
        self.popup.root.after(100, self._drain_updates_queue)

        # Handle Ctrl+C / terminal close
        try:
            import signal
            signal.signal(signal.SIGINT, lambda *_: self._graceful_stop())
            signal.signal(signal.SIGTERM, lambda *_: self._graceful_stop())
        except Exception:
            pass

        # Run Tk event loop (very low CPU compared to manual root.update loop)
        try:
            self.popup.root.mainloop()
        finally:
            self._graceful_stop()

def check_requirements():
    """Check if requests is installed"""
    try:
        import requests
        print("✅ requests module is installed")
        return True
    except ImportError:
        print("📦 Installing requests module...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"], 
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
            print("✅ requests installed successfully")
            return True
        except:
            print("❌ Failed to install requests")
            return False

def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("🤖 TELEGRAM BOT WITH UPPER RIGHT POPUPS & BUTTONS")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        print("❌ Cannot continue without requests module")
        return
    
    # Create and run bot
    try:
        bot = TelegramBot()
        bot.run()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print("\n💡 Try deleting bot_config.json and running again")

if __name__ == "__main__":
    main()
