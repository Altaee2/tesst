import telebot
from telebot import types
import requests
import datetime

bot = telebot.TeleBot("8210571275:AAE-MLpnfT-XesPR_QFGQmJ4bUtwQvpBpkQ", parse_mode="HTML")

headers = {
    'Host': 'restore-access.indream.app',
    'Connection': 'keep-alive',
    'x-api-key': 'e758fb28-79be-4d1c-af6b-066633ded128',
    'Accept': '*/*',
    'Accept-Language': 'ar',
    'Content-Length': '25',
    'User-Agent': 'Nicegram/101 CFNetwork/1404.0.5 Darwin/22.3.0',
    'Content-Type': 'application/x-www-form-urlencoded',
}

# /start handler
@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    info = get_user_info(user.id)

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="📍 ايديي", callback_data="get_id"))
    keyboard.add(types.InlineKeyboardButton(text="🧑‍💻 المطور", url="https://t.me/altaee_z"))
    keyboard.add(types.InlineKeyboardButton(text="📡 قناة التحديثات", url="https://t.me/xx28z"))

    text = f"""
اهلاً <b>{user.first_name}</b> 👋
• هذا البوت يوفر لك معلومات عن الحسابات والمجموعات.

🔹 فقط أرسل أي <b>ID</b> وسنخبرك بتاريخ الإنشاء.

ملاحظة مهمة :
	إذا تريد البوت يدعم المجموعات والقنوات بعد، لازم تستخدم API ثاني (ولحد الآن API تاريخ إنشاء القنوات غير متوفر للعامة).
	
"""
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

    # ترحيب بالمستخدم بمعلوماته
    welcome_text = f"""✨ <b>معلومات دخولك:</b>
👤 الاسم: <b>{user.first_name}</b>
🆔 الايدي: <code>{user.id}</code>
🔗 اليوزر: @{user.username if user.username else 'لا يوجد'}
📅 تاريخ الدخول: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
📱 البايو: <i>{user.bio if hasattr(user, 'bio') else 'لا يوجد'}</i>

ملاحظة مهمة : 
إذا تريد البوت يدعم المجموعات والقنوات بعد، لازم تستخدم API ثاني (ولحد الآن API تاريخ إنشاء القنوات غير متوفر للعامة).
"""
    try:
        bot.send_message(user.id, welcome_text)
    except:
        pass


# /id command
@bot.message_handler(commands=['id'])
def get_id_cmd(message):
    chat = message.chat
    if chat.type == 'private':
        user = message.from_user
        info = get_user_info(user.id)
        bot.reply_to(message, info)
    else:
        info = get_group_info(chat)
        bot.reply_to(message, info)


# قراءة الايدي وتحويله لتاريخ إنشاء
@bot.message_handler(func=lambda m: m.text and m.text.lstrip('-').isdigit())
def fetch_creation_date(message):
    user_input = message.text.strip()

    # آيدي قناة أو مجموعة
    if user_input.startswith("-100"):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="➕ أضفني للمجموعة", url="https://t.me/data990_bot?startgroup=true"))
        bot.reply_to(message,
            "ℹ️ هذا الآيدي يتبع لمجموعة أو قناة.\n⚠️ لا يمكن معرفة تاريخ إنشاء القنوات أو المجموعات من هذا البوت.\n\n"
            "إذا تريد تعرف معلومات مجموعة، أضف البوت بداخلها واكتب /id.",
            reply_markup=keyboard
        )
        return

    # آيدي رقمي لكنه مو صالح
    if not user_input.isdigit():
        bot.reply_to(message, "❌ الايدي يجب أن يكون أرقام فقط.")
        return

    # التأكد أنه مو آيدي قناة لكن بصيغة خاطئة
    if len(user_input) >= 12:
        bot.reply_to(message, "❌ يبدو أن هذا الآيدي طويل جداً، ربما يكون آيدي قناة.\nأرسل فقط آيدي مستخدم مكون من 9 أرقام أو أقل.")
        return

    data = f'{{"telegramId":{user_input}}}'
    try:
        res = requests.post('https://restore-access.indream.app/regdate', headers=headers, data=data).json()
        if res.get("data") and res["data"].get("date"):
            date = res["data"]["date"]
            bot.reply_to(message, f"✅ <b>تاريخ إنشاء الحساب:</b>\n{date}")
        else:
            bot.reply_to(message, "❌ لا يمكن جلب تاريخ الإنشاء. تأكد من صحة الايدي.")
    except Exception as e:
        bot.reply_to(message, "❌ حدث خطأ أثناء جلب البيانات.")


# زر جلب الايدي من الزر
@bot.callback_query_handler(func=lambda call: call.data == "get_id")
def get_id_button(call):
    user = call.from_user
    data = f'{{"telegramId":{user.id}}}'
    res = requests.post('https://restore-access.indream.app/regdate', headers=headers, data=data).json()
    date = res["data"]["date"] if res.get("data") else "❓"

    text = f"""
🆔 ايديك: <code>{user.id}</code>
📅 تاريخ إنشاء حسابك: <b>{date}</b>
"""
    bot.send_message(call.message.chat.id, text)


# إشعار عند إضافة البوت لقناة أو مجموعة
@bot.my_chat_member_handler()
def handle_chat_member_update(message):
    new_status = message.new_chat_member.status
    chat = message.chat

    if new_status == 'member' or new_status == 'administrator':
        info = get_group_info(chat)
        added_by = message.from_user

        text_group = f"✅ تم اضافة البوت هنا.\n\n{info}"
        text_user = f"🔔 تم اضافة البوت في <b>{chat.type}</b> بواسطة <b>{added_by.first_name}</b>\n\n{info}"

        try:
            bot.send_message(chat.id, text_group)
        except:
            pass

        try:
            bot.send_message(added_by.id, text_user)
        except:
            pass

    elif new_status == 'kicked':
        try:
            bot.send_message(message.from_user.id, f"❌ تم حظر البوت من <b>{chat.title}</b>")
        except:
            pass


# دالة معلومات المستخدم
def get_user_info(user_id):
    data = f'{{"telegramId":{user_id}}}'
    res = requests.post('https://restore-access.indream.app/regdate', headers=headers, data=data).json()
    date = res["data"]["date"] if res.get("data") else "❓"
    text = f"""🧍‍♂️ معلومات المستخدم:
🆔 الايدي: <code>{user_id}</code>
📅 تاريخ إنشاء الحساب: <b>{date}</b>
"""
    return text


# دالة معلومات المجموعة أو القناة
def get_group_info(chat):
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    link = f"https://t.me/{chat.username}" if chat.username else "لا يوجد"
    chat_type = "مجموعة" if chat.type in ['group', 'supergroup'] else "قناة"
    text = f"""📣 معلومات {chat_type}:
📛 الاسم: <b>{chat.title}</b>
🆔 الايدي: <code>{chat.id}</code>
🔗 الرابط: {link}
📅 تاريخ الإضافة: {date}
"""
    return text


# تشغيل البوت
bot.infinity_polling()