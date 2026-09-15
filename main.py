import os
import json
import time
import threading
import requests
import telebot
from telebot import types
from flask import Flask

# 1. 24/7 Web Server
app = Flask(__name__)

@app.route('/')
def home():
    return "BOT RUNNING 24/7"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# 2. Configurations
BOT_TOKEN = "8600453122:AAHplw4g0dNZ8Es_6oXRX6LdPv6I_aQqIV4"
ADMIN_ID = 8671410379
ADMIN_USER = "OxRehann"

CH1_ID = "@OxRehanCyber"
CH1_LINK = "https://t.me/OxRehanCyber"
CH2_LINK = "https://t.me/+852hkOgj0UNlZGU9"
INSTA_LINK = "https://instagram.com/ox.mods"

KV_URL = "https://api.keyval.org/ox_refer_earn_fresh_vault_2026"
DB_FILE = "refer_earn_fresh_db.json"

bot = telebot.TeleBot(BOT_TOKEN)
user_states = {}

# 3. Database
def load_db():
    try:
        r = requests.get(KV_URL, timeout=4).json()
        if isinstance(r, dict) and "users" in r:
            return r
    except:
        pass
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"users": {}, "gift_codes": {}}

def save_db(data):
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass
    try:
        requests.post(KV_URL, json=data, timeout=4)
    except:
        pass

db = load_db()

def get_user(uid):
    s = str(uid)
    if s not in db["users"]:
        db["users"][s] = {
            "balance": 0.0,
            "referrals": 0,
            "total_withdrawn": 0.0,
            "verified": False
        }
        save_db(db)
    return db["users"][s]

def check_channel_member(uid):
    try:
        # Check primary public channel
        status = bot.get_chat_member(CH1_ID, uid).status
        if status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        # Agar bot admin na ho toh block na kare, user pass ho sake
        print(f"Channel Check Bypass/Error: {e}")
        return True

# 4. Colorful Keyboards (Blue theme for links, Green theme for Unlock)
def verify_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("🔵 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝟭 🔹", url=CH1_LINK),
        types.InlineKeyboardButton("🔵 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝟮 🔹", url=CH2_LINK),
        types.InlineKeyboardButton("🔵 𝗙𝗢𝗟𝗟𝗢𝗪 𝗜𝗡𝗦𝗧𝗔𝗚𝗥𝗔𝗠 🔹", url=INSTA_LINK),
        types.InlineKeyboardButton("🟢 ⚡ 𝗩𝗘𝗥𝗜𝗙𝗬 & 𝗨𝗡𝗟𝗢𝗖𝗞 ⚡ 🟢", callback_data="check_joined")
    )
    return kb

# Multi-Color Keyboard Menu
def main_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    b1 = types.KeyboardButton("🟡 💰 𝗠𝗬 𝗪𝗔𝗟𝗟𝗘𝗧")
    b2 = types.KeyboardButton("🟢 👥 𝗥𝗘𝗙𝗘𝗥 & 𝗘𝗔𝗥𝗡 (₹𝟯)")
    b3 = types.KeyboardButton("🔴 💳 𝗪𝗜𝗧𝗛𝗗𝗥𝗔𝗪 𝗠𝗢𝗡𝗘𝗬")
    b4 = types.KeyboardButton("🟣 🎁 𝗥𝗘𝗗𝗘𝗘𝗠 𝗖𝗢𝗗𝗘")
    b5 = types.KeyboardButton("🔵 📊 𝗟𝗜𝗩𝗘 𝗦𝗧𝗔𝗧𝗦")
    b6 = types.KeyboardButton("🟠 📞 𝟮𝟰/𝟳 𝗦𝗨𝗣𝗣𝗢𝗥𝗧")
    kb.add(b1, b2)
    kb.add(b3, b4)
    kb.add(b5, b6)
    return kb

def withdraw_choice_kb():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🔵 📱 UPI ID", callback_data="wth_upi"),
        types.InlineKeyboardButton("🔵 📞 PhonePe / Paytm", callback_data="wth_num"),
        types.InlineKeyboardButton("🟣 🖼️ Upload QR Code", callback_data="wth_qr"),
        types.InlineKeyboardButton("🔴 ❌ Cancel", callback_data="wth_cancel")
    )
    return kb

# 5. Handlers
@bot.message_handler(commands=['start'])
def start_cmd(m):
    uid = m.from_user.id
    s = str(uid)
    text = m.text.split()

    if s not in db["users"]:
        ref_id = text[1] if len(text) > 1 and text[1].isdigit() and text[1] != s else None
        db["users"][s] = {
            "balance": 0.0,
            "referrals": 0,
            "total_withdrawn": 0.0,
            "verified": False,
            "referrer": ref_id
        }
        save_db(db)

    u = db["users"][s]

    if not u.get("verified", False):
        rm = types.ReplyKeyboardRemove()
        msg_text = (
            f"👋 *Welcome {m.from_user.first_name}!* 🎮\n\n"
            "🔒 *Bot unlock karne ke liye steps complete karein:*\n\n"
            "🔹 Channel 1 aur Channel 2 join karein\n"
            "🔹 Instagram (@ox.mods) ko follow karein\n\n"
            "Uske baad niche **🟢 VERIFY & UNLOCK 🟢** dabayein!"
        )
        bot.send_message(m.chat.id, "🔒 *Verification Required*", reply_markup=rm)
        bot.send_message(m.chat.id, msg_text, reply_markup=verify_keyboard(), parse_mode='Markdown')
        return

    bot.send_message(
        m.chat.id,
        f"🔥 *WELCOME TO REFER & EARN BOT* 🔥\n\n"
        f"👋 Welcome back, *{m.from_user.first_name}*!\n"
        f"💸 *Per Refer:* `₹3.0 Real Cash`\n"
        f"🎯 *Minimum Withdraw:* `₹100`\n\n"
        "Apna option select karein 👇",
        parse_mode='Markdown',
        reply_markup=main_keyboard()
    )

@bot.callback_query_handler(func=lambda c: c.data == "check_joined")
def check_join_callback(c):
    uid = c.from_user.id
    s = str(uid)
    u = get_user(uid)

    is_valid = check_channel_member(uid)
    if is_valid:
        u["verified"] = True

        ref_id = u.get("referrer")
        if ref_id and ref_id in db["users"]:
            db["users"][ref_id]["balance"] += 3.0
            db["users"][ref_id]["referrals"] += 1
            u["referrer"] = None
            try:
                bot.send_message(
                    int(ref_id),
                    f"🎉 *New Referral Verified!*\n\n"
                    f"👤 Member: `{c.from_user.first_name}`\n"
                    f"💵 *+₹3.0 Cash* aapke wallet me credit ho gaya!",
                    parse_mode='Markdown'
                )
            except:
                pass

        save_db(db)
        
        # Purana join message delete karein
        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        # Naya success message with colorful keyboard
        bot.send_message(
            c.message.chat.id,
            "✅ *Verification Successful!*\n\nAapka account activate ho gaya hai. Dashboard se earning start karein 👇",
            parse_mode='Markdown',
            reply_markup=main_keyboard()
        )
    else:
        bot.answer_callback_query(
            c.id,
            "❌ Pehle channel join karein!",
            show_alert=True
        )

# Button Handlers
@bot.message_handler(func=lambda m: "MY WALLET" in m.text)
def wallet_cmd(m):
    u = get_user(m.from_user.id)
    text = (
        "╔════════════════════╗\n"
        "       💼  *USER WALLET*  💼\n"
        "╚════════════════════╝\n\n"
        f"👤 *Account:* {m.from_user.first_name}\n"
        f"🆔 *User ID:* `{m.from_user.id}`\n\n"
        f"🟡 *Balance:* `₹{u['balance']:.2f}`\n"
        f"🟢 *Total Referrals:* `{u['referrals']}`\n"
        f"🔴 *Total Withdrawn:* `₹{u['total_withdrawn']:.2f}`\n\n"
        "📌 *Minimum Withdraw:* `₹100.00`"
    )
    bot.reply_to(m, text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: "REFER & EARN" in m.text)
def refer_cmd(m):
    uid = m.from_user.id
    bot_user = bot.get_me().username
    text = (
        "🚀 *REFER & EARN CASH* 🚀\n\n"
        "💵 *Reward:* ₹3.0 per verified invite!\n"
        "🎯 *Goal:* 34 refers = ₹100 instant cash!\n\n"
        "🔗 *Invite Link:*\n"
        f"`https://t.me/{bot_user}?start={uid}`\n\n"
        "📌 *Is link ko doston ko bhejein!*"
    )
    bot.reply_to(m, text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: "WITHDRAW MONEY" in m.text)
def withdraw_prompt(m):
    u = get_user(m.from_user.id)
    if u["balance"] < 100.0:
        bot.reply_to(
            m,
            f"⚠️ *Insufficient Balance!*\n\n"
            f"Aapka current balance: `₹{u['balance']:.2f}`\n"
            f"Withdraw ke liye kam se kam **₹100** hona zaroori hai.\n\n"
            f"👉 Aur `₹{100.0 - u['balance']:.2f}` kamane ke liye refer karein!",
            parse_mode='Markdown'
        )
        return

    bot.reply_to(
        m,
        f"✅ *Eligible for Withdrawal!*\n\n"
        f"💰 Available Balance: `₹{u['balance']:.2f}`\n\n"
        "Payment receive karne ka method chunein:",
        parse_mode='Markdown',
        reply_markup=withdraw_choice_kb()
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("wth_"))
def handle_withdraw_choice(c):
    action = c.data
    uid = c.from_user.id

    if action == "wth_cancel":
        bot.delete_message(c.message.chat.id, c.message.message_id)
        bot.send_message(c.message.chat.id, "❌ Cancelled.", reply_markup=main_keyboard())
        return

    user_states[uid] = action
    bot.delete_message(c.message.chat.id, c.message.message_id)

    if action == "wth_upi":
        bot.send_message(c.message.chat.id, "📱 Apni valid **UPI ID** bhejein (Jaise: `user@upi`):")
    elif action == "wth_num":
        bot.send_message(c.message.chat.id, "📞 Apna **Paytm / PhonePe Mobile Number** bhejein:")
    elif action == "wth_qr":
        bot.send_message(c.message.chat.id, "🖼️ Apna **QR Code Photo** send karein:")

@bot.message_handler(content_types=['photo'], func=lambda m: user_states.get(m.from_user.id) == "wth_qr")
def handle_qr_upload(m):
    uid = m.from_user.id
    user_states.pop(uid, None)
    u = get_user(uid)

    if u["balance"] < 100.0:
        bot.reply_to(m, "⚠️ Balance kam hai.")
        return

    amount = u["balance"]
    u["balance"] = 0.0
    u["total_withdrawn"] += amount
    save_db(db)

    photo_id = m.photo[-1].file_id

    admin_kb = types.InlineKeyboardMarkup()
    admin_kb.add(
        types.InlineKeyboardButton("✅ APPROVE", callback_data=f"adm_ok_{uid}_{amount}"),
        types.InlineKeyboardButton("❌ REJECT & REFUND", callback_data=f"adm_no_{uid}_{amount}")
    )

    bot.send_photo(
        ADMIN_ID,
        photo_id,
        caption=(
            "🚨 *NEW WITHDRAW REQUEST (QR CODE)* 🚨\n\n"
            f"👤 User: {m.from_user.first_name} (`{uid}`)\n"
            f"💵 Amount: `₹{amount:.2f}`\n"
            f"Method: QR Code Scan"
        ),
        parse_mode='Markdown',
        reply_markup=admin_kb
    )

    bot.reply_to(
        m,
        f"✅ *Withdrawal Request Submitted!*\n\n"
        f"💵 Amount: `₹{amount:.2f}`\n"
        "Admin check karke payment dispatch kar denge.",
        parse_mode='Markdown',
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda m: "REDEEM CODE" in m.text)
def redeem_prompt(m):
    user_states[m.from_user.id] = "redeem_code"
    bot.reply_to(m, "🎁 Apna **Redeem Code** yahan enter karein:\n\n_(Cancel: /cancel)_")

@bot.message_handler(func=lambda m: "LIVE STATS" in m.text)
def stats_view(m):
    total_users = len(db.get("users", {}))
    bot.reply_to(
        m,
        "📊 *BOT LIVE STATISTICS* 📊\n\n"
        f"👥 Total Users: `{total_users}`\n"
        "⚡ Payout: UPI / Number / QR Code\n"
        "🔒 Cloud Sync: 24/7 Active",
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda m: "24/7 SUPPORT" in m.text)
def support_view(m):
    bot.reply_to(
        m,
        f"📞 *OFFICIAL SUPPORT*\n\n"
        f"Admin: @{ADMIN_USER}",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['cancel'])
def cancel_cmd(m):
    user_states.pop(m.from_user.id, None)
    bot.reply_to(m, "❌ Canceled.", reply_markup=main_keyboard())

# 6. Inputs Processing
@bot.message_handler(func=lambda m: m.from_user.id in user_states)
def process_user_inputs(m):
    uid = m.from_user.id
    st = user_states.pop(uid, None)
    u = get_user(uid)

    if st in ["wth_upi", "wth_num"]:
        pay_info = m.text.strip()
        if u["balance"] < 100.0:
            bot.reply_to(m, "⚠️ Balance kam hai.")
            return

        amount = u["balance"]
        u["balance"] = 0.0
        u["total_withdrawn"] += amount
        save_db(db)

        admin_kb = types.InlineKeyboardMarkup()
        admin_kb.add(
            types.InlineKeyboardButton("✅ APPROVE", callback_data=f"adm_ok_{uid}_{amount}"),
            types.InlineKeyboardButton("❌ REJECT & REFUND", callback_data=f"adm_no_{uid}_{amount}")
        )

        bot.send_message(
            ADMIN_ID,
            f"🚨 *NEW WITHDRAW REQUEST* 🚨\n\n"
            f"👤 User: {m.from_user.first_name} (`{uid}`)\n"
            f"💵 Amount: `₹{amount:.2f}`\n"
            f"📌 Details: `{pay_info}`",
            parse_mode='Markdown',
            reply_markup=admin_kb
        )

        bot.reply_to(
            m,
            f"✅ *Withdrawal Request Submitted!*\n\n"
            f"💵 Amount: `₹{amount:.2f}`\n"
            f"📌 Detail: `{pay_info}`\n\n"
            "Admin verify karke payment dispatch kar denge!",
            parse_mode='Markdown',
            reply_markup=main_keyboard()
        )

    elif st == "redeem_code":
        code = m.text.strip().upper()
        s = str(uid)
        codes = db.get("gift_codes", {})

        if code not in codes:
            bot.reply_to(m, "❌ Invalid ya Expired Code!", reply_markup=main_keyboard())
            return

        gdata = codes[code]
        if s in gdata["users"]:
            bot.reply_to(m, "⚠️ Yeh code pehle claim ho chuka hai!", reply_markup=main_keyboard())
            return

        if len(gdata["users"]) >= gdata["max_claims"]:
            bot.reply_to(m, "⚠️ Code limit full ho gayi!", reply_markup=main_keyboard())
            return

        amt = float(gdata["amount"])
        u["balance"] += amt
        gdata["users"].append(s)
        save_db(db)

        bot.reply_to(
            m,
            f"🎉 *Code Redeemed!* +₹{amt:.2f} Cash added!\n"
            f"💰 New Balance: `₹{u['balance']:.2f}`",
            parse_mode='Markdown',
            reply_markup=main_keyboard()
        )

# 7. Admin Commands & Approval
@bot.callback_query_handler(func=lambda c: c.data.startswith("adm_"))
def admin_approval_callback(c):
    if c.from_user.id != ADMIN_ID:
        return
    
    parts = c.data.split("_")
    action = parts[1]
    target_uid = int(parts[2])
    amt = float(parts[3])

    if action == "ok":
        bot.answer_callback_query(c.id, "Payment Approved!")
        try:
            bot.edit_message_caption(c.message.caption + "\n\n✅ *STATUS: PAID & APPROVED*", chat_id=c.message.chat.id, message_id=c.message.message_id, parse_mode='Markdown')
        except:
            bot.edit_message_text(c.message.text + "\n\n✅ *STATUS: PAID & APPROVED*", chat_id=c.message.chat.id, message_id=c.message.message_id, parse_mode='Markdown')
        try:
            bot.send_message(target_uid, f"🎉 *WITHDRAWAL SUCCESSFUL!*\n\nAapki `₹{amt:.2f}` ki payment dispatch ho chuki hai!", parse_mode='Markdown')
        except:
            pass

    elif action == "no":
        target_s = str(target_uid)
        if target_s in db["users"]:
            db["users"][target_s]["balance"] += amt
            db["users"][target_s]["total_withdrawn"] -= amt
            save_db(db)
        bot.answer_callback_query(c.id, "Payment Rejected & Refunded!")
        try:
            bot.edit_message_caption(c.message.caption + "\n\n❌ *STATUS: REJECTED & REFUNDED*", chat_id=c.message.chat.id, message_id=c.message.message_id, parse_mode='Markdown')
        except:
            bot.edit_message_text(c.message.text + "\n\n❌ *STATUS: REJECTED & REFUNDED*", chat_id=c.message.chat.id, message_id=c.message.message_id, parse_mode='Markdown')
        try:
            bot.send_message(target_uid, f"⚠️ *WITHDRAWAL REJECTED*\n\nAapki request reject ho gayi hai aur paise wallet me refund kar diye gaye hain.", parse_mode='Markdown')
        except:
            pass

@bot.message_handler(commands=['gen'])
def admin_generate_code(m):
    if m.from_user.id != ADMIN_ID:
        return
    parts = m.text.split()
    if len(parts) != 4:
        bot.reply_to(m, "Format: `/gen <CODE> <AMOUNT> <MAX_USERS>`\nExample: `/gen CASH20 20 50`", parse_mode='Markdown')
        return

    code = parts[1].upper()
    amount = float(parts[2])
    max_c = int(parts[3])

    if "gift_codes" not in db:
        db["gift_codes"] = {}

    db["gift_codes"][code] = {
        "amount": amount,
        "max_claims": max_c,
        "users": []
    }
    save_db(db)

    bot.reply_to(
        m,
        f"✅ *Gift Code Created!*\n\n"
        f"🎁 Code: `{code}`\n"
        f"💵 Amount: `₹{amount:.2f}`\n"
        f"👥 Max Users: `{max_c}`",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['all'])
def admin_broadcast(m):
    if m.from_user.id != ADMIN_ID:
        return
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(m, "Format: `/all <Aapka Message>`", parse_mode='Markdown')
        return

    msg = parts[1]
    all_users = list(db.get("users", {}).keys())
    bot.reply_to(m, f"📢 Broadcast shuru: {len(all_users)} users ko ja raha hai...")

    success, failed = 0, 0
    for u in all_users:
        try:
            bot.send_message(int(u), f"📢 *OFFICIAL BROADCAST*\n\n{msg}", parse_mode='Markdown')
            success += 1
            time.sleep(0.04)
        except:
            failed += 1

    bot.send_message(m.chat.id, f"✅ Broadcast Done!\nSent: `{success}`\nFailed: `{failed}`", parse_mode='Markdown')

if __name__ == '__main__':
    threading.Thread(target=run_web).start()
    bot.infinity_polling()
