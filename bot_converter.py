import telebot
import requests
import json
import logging


# бот здесь https://t.me/converter_easybite_bot

bot = telebot.TeleBot('6942884627:AAGWAE7iDCAsXe7MAiQmFNUuK4sk8u_dLLs')
logging.basicConfig(filename='bot_log.txt', level=logging.INFO)
def log_user_action(user_id, action):
    logging.info(f"Пользователь {user_id} выполнил действие: {action}")

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id,
                     "Привет! Я бот для конвертации валют. Используй /help, чтобы узнать доступные команды.")
    log_user_action(message.chat.id, "/start")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, "Доступные команды:\n"
                                      "/start - приветствие и описание функционала\n"
                                      "/help - справка по командам\n"
                                      "/convert [сумма] [из валюты] to [в валюту] - конвертация валюты")
    log_user_action(message.chat.id, "/help")

@bot.message_handler(commands=['convert'])
def handle_convert(message):
    try:
        _, amount, from_currency, _, to_currency = message.text.split()
        amount = float(amount)
        conversion_result = convert_currency(amount, from_currency.upper(), to_currency.upper())
        if conversion_result == 'Error':
            bot.send_message(message.chat.id, 'Ошибка при получении курсов валют. Проверьте правильность ввода.')
        else:
            bot.send_message(message.chat.id, f"{amount} {from_currency} равно {conversion_result} {to_currency}")
    except ValueError:
        bot.send_message(message.chat.id,
                         "Некорректный формат ввода. Используйте /convert [сумма] [из валюты] to [в валюту]")


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if "привет" in message.text.lower():
        bot.send_message(message.chat.id, "Привет! Как я могу помочь? Напиши /help чтобы узнать, что я умею")
    elif "пока" in message.text.lower():
        bot.send_message(message.chat.id, "До свидания! Если у вас возникнут вопросы, используйте /help.")
    else:
        bot.send_message(message.chat.id, "Не понимаю ваш запрос. Используйте /help для получения списка команд.")
    log_user_action(message.chat.id, "Неопределенный запрос")


def convert_currency(amount, from_currency, to_currency):
    api_url = f'https://open.er-api.com/v6/latest/{from_currency}'
    response = requests.get(api_url)
    data = json.loads(response.text)

    if response.status_code == 200 and 'rates' in data:
        if to_currency in data['rates']:
            rate = data['rates'][to_currency]
            result = round(amount * rate, 2)
            logging.info(f"Конвертация: {amount} {from_currency} в {result} {to_currency}")
            return result
        else:
            logging.error(f"Курс для валюты {to_currency} не найден.")
            return f"Курс для валюты {to_currency} не найден."
    else:
        logging.error(f"Ошибка при получении курсов валют. Код ошибки: {response.status_code}")
        return "Error"

bot.polling(none_stop=True)