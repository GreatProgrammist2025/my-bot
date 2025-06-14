import telebot
import random
from datetime import datetime

bot = telebot.TeleBot("7871511906:AAH8hz3f0X2WeihbXz7VDx_yBSM3Sl_BRDQ")

user_data = {} 

def get_user(message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {
            "coins": 100,
            "donations": [],
            "level": 1,
            "exp": 0,
            "last_daily": None,
            "last_wheel": None,
            "echo_mode": False  
        }
    return user_data[user_id]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, " Привет! Я бот. Введи /help, чтобы посмотреть список того что я умею .")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
🌟 Добро пожаловать в бота!

🟢 Базовые команды:
/start — начать чат
/help — показать список команд

🔁 Режим повторялки:
/echo on — включить режим "повторялки"
/echo off — выключить режим "повторялки"

🔧 Edit Bots (управление через @BotFather):
/setname — изменить имя бота
/setdescription — изменить описание бота
/setabouttext — изменить текст "About"
/setuserpic — изменить фото профиля
/setcommands — изменить список команд
/deletebot — удалить бота

⚙️ Bot Settings (тоже через @BotFather):
/token — получить новый токен
/revoke — отозвать текущий токен
/setinline — включить/выключить inline-режим
/setinlinegeo — запросы геолокации в inline-режиме
/setinlinefeedback — настройки обратной связи в inline-режиме
/setjoingroups — можно ли добавлять бота в группы?
/setprivacy — включить/выключить приватность в группах

🎮 Игровые команды:
/donate — как поддержать бота через Telegram Stars
/test_donate — тестовый донат
/mydonations — посмотреть историю донатов
/balance — мой баланс
/top — рейтинг игроков
/bet [сумма] — сделать ставку
/jackpot [сумма] — попробуй удачу в джекпóте
/wheel — колесо фортуны
/daily — ежедневная игра
"""
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['echo'])
def toggle_echo(message):
    data = get_user(message)
    args = message.text.split()

    if len(args) < 2:
        bot.reply_to(message, "❌ Укажите on или off. Например: /echo on")
        return

    mode = args[1].lower()
    if mode == "on":
        data["echo_mode"] = True
        bot.reply_to(message, "🔁 Режим повторялки включён. Пиши что угодно — я буду повторять!")
    elif mode == "off":
        data["echo_mode"] = False
        bot.reply_to(message, "🛑 Режим повторялки выключен.")
    else:
        bot.reply_to(message, "❌ Неизвестный режим. Используй on или off.")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    data = get_user(message)
    if data.get("echo_mode", False):
        bot.reply_to(message, message.text)

@bot.message_handler(commands=['donate'])
def donate(message):
    bot.reply_to(message, """
🌟 Вы можете поддержать меня через Telegram Stars!
Каждый донат помогает развивать бота и получать вам новые возможности.

Примеры вознаграждений:
- +100 монет
- Редкие предметы
- Ежедневные бонусы

Пока что эта функция в разработке. Ожидайте обновения!

💡 Для тестирования используйте команду `/test_donate`
""")

@bot.message_handler(commands=['test_donate'])
def test_donate(message):
    amount = 50  # звёздочек
    give_rewards(message, amount)
    bot.reply_to(message, f"🌟 Тестовый донат на {amount} звёздочек выполнен!")

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(query):
    bot.answer_pre_checkout_query(query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    amount = message.successful_payment.total_amount // 100  # Переводим из копеек в звёздочки
    bot.send_message(message.chat.id, f"🌟 Благодарю за поддержку! Получено {amount} звёздочек.")
    give_rewards(message, amount)

def give_rewards(message, amount: int):
    data = get_user(message)
    coins = amount * 10  
    data["coins"] += coins
    data["donations"].append({
        "stars": amount,
        "coins_received": coins,
        "date": str(datetime.now())
    })
    bot.reply_to(message, f"🎁 За {amount} звёздочек ты получил(а) {coins} монет!")

@bot.message_handler(commands=['mydonations'])
def my_donations(message):
    data = get_user(message)
    donations = data.get("donations", [])
    if not donations:
        bot.reply_to(message, "😢 У тебя ещё не было донатов.")
        return

    reply = "🧾 История твоих донатов:\n\n"
    for d in donations:
        reply += f"⭐ {d['stars']} звёзд → 💰 +{d['coins_received']} монет\n"
        reply += f"📅 {d['date']}\n\n"

    bot.reply_to(message, reply)

@bot.message_handler(commands=['balance'])
def balance(message):
    data = get_user(message)
    bot.reply_to(message, f"💰 У тебя {data['coins']} монет.")

@bot.message_handler(commands=['top'])
def top_players(message):
    sorted_users = sorted(
        [(uid, d["coins"], d["level"]) for uid, d in user_data.items()],
        key=lambda x: (-x[1], -x[2])
    )[:10]
    reply = "🏆 ТОП ИГРОКОВ:\n"
    for i, (uid, coins, level) in enumerate(sorted_users, start=1):
        name = user_data.get(uid, {}).get("name", "Игрок")
        reply += f"{i}. {name} — {coins} монет (Уровень {level})\n"
    bot.reply_to(message, reply)

@bot.message_handler(commands=['daily'])
def daily_game(message):
    data = get_user(message)
    today = datetime.now().date()

    last = data.get("last_daily")
    if last and (datetime.fromisoformat(last).date() == today):
        bot.reply_to(message, "❌ Сегодня ты уже играл. Приходи завтра!")
        return

    result = random.choice(["win", "lose"])
    reward = 50
    if result == "win":
        data["coins"] += reward
        data["last_daily"] = str(today)
        bot.reply_to(message, f"🎉 Тебе повезло! +{reward} монет.")
    else:
        bot.reply_to(message, "😢 Фортуна не на твоей стороне.")

@bot.message_handler(commands=['casino'])
def casino(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "❌ Укажите цвет: красное или чёрное")
        return

    color = args[1].lower()
    if color not in ["красное", "чёрное"]:
        bot.reply_to(message, "❌ Неверный цвет. Используй: красное или чёрное")
        return

    bot.reply_to(message, "🎰 Кручу рулетку...")
    winning_color = random.choice(["красное", "чёрное"])

    @bot.send_chat_action(message.chat.id, 'typing')
    def play_casino():
        if color == winning_color:
            get_user(message)["coins"] += 100
            bot.reply_to(message, f"🎉 Выпало **{winning_color}**! Ты выиграл(а) 100 монет!")
        else:
            bot.reply_to(message, f"😢 Выпало **{winning_color}**. Ты проиграл(а).")

    play_casino()

@bot.message_handler(commands=['jackpot'])
def jackpot(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "❌ Укажите сумму для ставки.")
        return

    try:
        amount = int(args[1])
    except:
        bot.reply_to(message, "❌ Это не число.")
        return

    data = get_user(message)
    if amount > data["coins"]:
        bot.reply_to(message, "❌ Недостаточно монет.")
        return

    bot.reply_to(message, "🎰 Делаем ставку...")

    win_chance = 0.1  
    if random.random() < win_chance:
        prize = amount * 3  
        data["coins"] += prize
        bot.reply_to(message, f"🔥 Джекпот! Ты выиграл(а) {prize} монет!")
    else:
        data["coins"] -= amount
        bot.reply_to(message, f"😢 Промах... Ты потерял(а) {amount} монет.")

@bot.message_handler(commands=['wheel'])
def wheel_of_fortune(message):
    data = get_user(message)
    now = datetime.now()

    last_spin = data.get("last_wheel")
    if last_spin:
        last_time = datetime.fromisoformat(last_spin)
        if (now - last_time).days < 1:
            bot.reply_to(message, "⏳ Колесо можно крутить раз в день.")
            return

    rewards = [
        {"text": "золотой слиток", "coins": 100},
        {"text": "монетный мешок", "coins": 50},
        {"text": "ничего", "coins": 0},
        {"text": "удача", "coins": 30},
        {"text": "богатство", "coins": 75}
    ]

    reward = random.choice(rewards)
    data["coins"] += reward["coins"]
    data["last_wheel"] = str(now)

    bot.reply_to(message, f"🎡 Ты крутишь колесо...\n🎁 Выпало: **{reward['text']}** (+{reward['coins']} монет)")

@bot.message_handler(commands=['bet'])
def bet(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "❌ Укажите сумму для ставки.")
        return

    try:
        amount = int(args[1])
    except:
        bot.reply_to(message, "❌ Это не число.")
        return

    data = get_user(message)
    if amount > data["coins"]:
        bot.reply_to(message, "❌ Недостаточно монет.")
        return

    win = random.random() < 0.4  
    if win:
        data["coins"] += amount
        bot.reply_to(message, f"🎉 Ты выиграл(а)! +{amount} монет. Теперь у тебя {data['coins']}")
    else:
        data["coins"] -= amount
        bot.reply_to(message, f"😢 Ты проиграл(а)... -{amount} монет. Осталось {data['coins']}")

print("Бот запущен!")
bot.polling(non_stop=False)