
import telebot
from threading import Thread
import time
from datetime import datetime

BOT_TOKEN = 'YOUR_BOT_TOKEN'
OWNER_ID = 123456789

bot = telebot.TeleBot(BOT_TOKEN)
users = {}
referrals = {}
scrolling_messages = []
MINING_RATE = 0.000002  # TON per second
CLAIM_THRESHOLD = 0.015

# Helper to ensure user exists
def ensure_user(user_id, username):
    if user_id not in users:
        users[user_id] = {
            'username': username,
            'joined': str(datetime.now()),
            'vip': False,
            'ton_balance': 0.0,
            'mining_balance': 0.0,
            'tonix_balance': 0,
            'referrals': [],
            'speed': 1.0
        }

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.chat.id
    uname = message.from_user.username or f"user{uid}"
    ensure_user(uid, uname)
    parts = message.text.split()
    if len(parts) > 1:
        referrer_id = int(parts[1])
        if referrer_id != uid and uid not in referrals:
            referrals[uid] = referrer_id
            users[referrer_id]['referrals'].append(uid)
            users[referrer_id]['tonix_balance'] += 100  # Level 1
    bot.send_message(uid, f"""👋 Welcome to TON Mining Bot, @{uname}!
Use /wallet to check your balance or /claim to withdraw mined TON.
""")

@bot.message_handler(commands=['wallet'])
def wallet(message):
    uid = message.chat.id
    user = users[uid]
    bot.send_message(uid, f"💎 TON Balance: {user['ton_balance']:.6f}\n🔄 Mined: {user['mining_balance']:.10f}\n🌀 TONIX: {user['tonix_balance']}\nVIP: {'✅' if user['vip'] else '❌'}")


@bot.message_handler(commands=['claim'])
def claim(message):
    uid = message.chat.id
    user = users[uid]
    if user['mining_balance'] >= CLAIM_THRESHOLD:
        user['ton_balance'] += user['mining_balance']
        scrolling_messages.append(f"🎉 @{user['username']} just claimed {user['mining_balance']:.6f} TON!")
        user['mining_balance'] = 0.0
        bot.send_message(uid, "✅ Claimed and transferred to wallet.")
    else:
        bot.send_message(uid, "⚠️ Claim amount too small (min 0.015 TON).")


@bot.message_handler(commands=['boost'])
def boost(message):
    uid = message.chat.id
    msg = """⚡ Mining Power Boost

Rent power for 30 days to increase speed.
Profitability: 8.493%/day (approx 0.849 TON/day).
Send TON to activate, admin will approve manually.
"""
    bot.send_message(uid, msg)

@bot.message_handler(commands=['status'])
def status(message):
    uid = message.chat.id
    vip = users[uid]['vip']
    bot.send_message(uid, f"VIP Status: {'✅' if vip else '❌'}")

@bot.message_handler(commands=['approvevip'])
def approvevip(message):
    if message.chat.id != OWNER_ID:
        return
    try:
        parts = message.text.split()
        target_id = int(parts[1])
        users[target_id]['vip'] = True
        users[target_id]['speed'] = 3.0  # Triple speed for VIP
        bot.send_message(target_id, "✅ VIP access granted! Mining speed tripled.")
        bot.send_message(message.chat.id, "Approved.")
    except:
        bot.send_message(message.chat.id, "❌ Failed to approve.")

# Mining thread
def mine_loop():
    while True:
        time.sleep(1)
        for user in users.values():
            user['mining_balance'] += MINING_RATE * user['speed']

Thread(target=mine_loop, daemon=True).start()
bot.polling()
