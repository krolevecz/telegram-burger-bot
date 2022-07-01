import sqlite3
import os
from time import sleep
from telebot import TeleBot, types
from dbhelper import DBHelper
from filter import bind_filters
from filter import catalogs_factory, add_products_factory, delete_products_factory, remove_products_factory
from keyboards import general_markup, catalog_markup, product_in_basket_markup, add_product_markup, \
    confirm_basket_markup, last_order_markup, phone_markup
from flask import Flask, request, abort
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = TeleBot(BOT_TOKEN, threaded=False)

URL = os.getenv("URL")
SECRET = os.getenv("SECRET")
url = URL + SECRET

# Remove webhook, it fails sometimes the set if there is a previous webhook.
bot.remove_webhook()
sleep(0.1)
bot.set_webhook(url=url)

app = Flask(__name__)

bind_filters(bot)

try:
    # Создаём объект для работы с БД.
    # db = DBHelper('sqlite_python.db')
    db = DBHelper(':memory:')

except sqlite3.Error as error:
    print("Ошибка при подключении к Базе Данных", error)


@app.route('/{}'.format(SECRET), methods=["POST"])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        # json_string = request.get_data().decode('utf-8')
        json_string = request.stream.read().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'ok', 200
    else:
        abort(403)


# Empty webserver index, return nothing, just http 200.
@app.route('/')
def index():
    return '<h1>Telegram: @ChatBurgerBot</h1>'


# Обработчик колбэков кнопок каталога.
@bot.callback_query_handler(func=None, catalogs_config=catalogs_factory.filter())
def catalogs_callback(call: types.CallbackQuery):
    if bot.answer_callback_query(callback_query_id=call.id):
        callback_data: dict = catalogs_factory.parse(callback_data=call.data)
        catalog_id = int(callback_data['catalog_id'])
        result = db.get_products(catalog_id=catalog_id)
        for product in result:
            bot.send_photo(chat_id=call.message.chat.id,
                           photo=open('bot/static/' + product[5], 'rb'),
                           caption=f'*{product[2]}*\n_{product[3]}_\nЦена: {product[4]} руб',
                           parse_mode='Markdown',
                           reply_markup=add_product_markup(product[0]))
            sleep(0.2)  # Исключительно для красоты.


# Обработчик колбэков кнопок добавления (+1) продуктов в корзину.
@bot.callback_query_handler(func=None, products_config=add_products_factory.filter())
def products_callback(call: types.CallbackQuery):
    if bot.answer_callback_query(callback_query_id=call.id):
        callback_data: dict = add_products_factory.parse(callback_data=call.data)
        product_id = int(callback_data['product_id'])
        product = db.get_product(product_id=product_id)
        db.add_basket_line(user_id=call.from_user.id,
                           product_id=product_id)

        bot.send_message(chat_id=call.message.chat.id,
                         text=f'*{product[2]}* добавлен в корзину',
                         parse_mode='Markdown')


# Обработчик колбэков кнопок уменьшения (-1) количества продукта в корзине.
@bot.callback_query_handler(func=None, products_config=delete_products_factory.filter())
def products_callback(call: types.CallbackQuery):
    if bot.answer_callback_query(callback_query_id=call.id):
        callback_data: dict = delete_products_factory.parse(callback_data=call.data)
        product_id = int(callback_data['product_id'])
        product = db.get_product(product_id=product_id)
        if db.user_has_product_in_basket(user_id=call.from_user.id, product_id=product_id):
            db.delete_basket_line(user_id=call.from_user.id,
                                  product_id=product_id)

            bot.send_message(chat_id=call.message.chat.id,
                             text=f'Количество *{product[2]}* уменьшено.',
                             parse_mode='Markdown')


# Обработчик колбэков кнопок удаления (X) продуктов из корзины.
@bot.callback_query_handler(func=None, products_config=remove_products_factory.filter())
def products_callback(call: types.CallbackQuery):
    if bot.answer_callback_query(callback_query_id=call.id):
        callback_data: dict = remove_products_factory.parse(callback_data=call.data)
        product_id = int(callback_data['product_id'])
        product = db.get_product(product_id=product_id)
        if db.user_has_product_in_basket(user_id=call.from_user.id, product_id=product_id):
            db.remove_basket_line(user_id=call.from_user.id,
                                  product_id=product_id)

            bot.send_message(chat_id=call.message.chat.id,
                             text=f'*{product[2]}* удалён из коризны',
                             parse_mode='Markdown')


# Обработчик колбэков подтверждения заказа -> новый заказ.
@bot.callback_query_handler(func=lambda c: c.data == 'confirm_basket')
def confirm_basket_callback(call: types.CallbackQuery):
    if bot.answer_callback_query(callback_query_id=call.id):
        basket = db.get_products_in_basket(call.from_user.id)
        if len(basket) != 0:
            if db.user_has_phone(user_id=call.from_user.id):  # Проверяем указал ли пользователь телефон.
                if db.user_has_delivery_address(user_id=call.from_user.id):  # Проверяем указал ли пользователь адрес.
                    db.add_order(call.from_user.id)  # Новый заказ (данные идут в orders и order_lines)
                    db.clear_basket(call.from_user.id)  # Очищаем корзину пользователя.

                    bot.send_message(chat_id=call.message.chat.id,
                                     text='✅ *Заказ подтвержден*',
                                     parse_mode='Markdown')
                else:
                    bot.send_message(chat_id=call.message.chat.id,
                                     text='🚚 Укажите адрес доставки. Для этого вначале напишите `/address` \n'
                                          'Пример: `/address Лобанка19 кв41`',
                                     parse_mode='Markdown')
            else:
                bot.send_message(chat_id=call.message.chat.id,
                                 text='Чтобы сделать заказ, пожалуйста, укажите ваш контактный номер',
                                 parse_mode='Markdown',
                                 reply_markup=phone_markup())

        else:
            bot.send_message(chat_id=call.message.chat.id,
                             text='❕Ваша корзина пуста')


# Обработчик колбэка добавления продуктов из последнего заказа в корзину.
@bot.callback_query_handler(func=lambda c: c.data == 'put_last_order')
def confirm_basket_callback(call: types.CallbackQuery):
    if bot.answer_callback_query(callback_query_id=call.id):
        db.put_last_order_to_basket(call.from_user.id)
        bot.send_message(chat_id=call.message.chat.id,
                         text='Продукты добавлены в корзину')


# Обработчик стартового сообщения.
@bot.message_handler(commands=['start'])
def start_message(message):
    # Добавляем пользователя в БД
    try:
        db.add_user(user_id=message.from_user.id,
                    user_name=message.from_user.first_name,
                    phone=None,
                    delivery_address=None)

    except sqlite3.Error as err:
        print("Пользователь уже существует.", err)

    bot.send_message(chat_id=message.chat.id,
                     text='🤖 Добро пожаловать!\n\n_Чтобы получить дополнительную информацию, '
                          'пожалуйста, перейдите в соответствующий раздел главного меню или '
                          'воспользуйтесь командой_ /help\b',
                     parse_mode='Markdown',
                     reply_markup=general_markup()
                     )


# Сохраняем контакт пользователя.
@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    db.save_user_phone(user_id=message.from_user.id, phone=message.contact.phone_number)

    bot.send_message(chat_id=message.from_user.id,
                     text='Теперь вы можете оформить заказ',
                     reply_markup=general_markup())


# Обработчик команды изменения адреса доставки.
@bot.message_handler(commands=['address'])
def address_handler(message):
    delivery_address = ' '.join(message.text.split()[1:])
    db.save_user_delivery_address(user_id=message.from_user.id, delivery_address=delivery_address)
    bot.send_message(chat_id=message.from_user.id,
                     text=f'🚚 Ваш адрес доставки: *{delivery_address}*\n'
                          f'📍_Вы всегда можете его изменить_\n\nТеперь вы можете оформить заказ',
                     parse_mode='Markdown',
                     reply_markup=general_markup())


def get_help_text(user_name):
    return f'🤖 Приветствую, *{user_name}!*\n' \
           f'Я - чат-бот лучшей бургерной вашего города! ' \
           f'С моей помощью вы всегда можете посмотреть актуальное меню нашего заведения, ' \
           f'заказать доставку, а также быть в курсе последний новостей, связанных с нашей деятельностью.\n\n' \
           f'_В нижней части экрана нашего диалога располагается главное меню, с помощью которого вы можете ' \
           f'перейти в следующие разделы:_\n' \
           f'*🍴 Меню* - посмотреть актуальное меню и добавить что-нибудь в корзину\n' \
           f'*🛒 Корзина* - ознакомиться с перечнем добавленного, изменить содержимое и ознакомиться с ' \
           f' итоговой суммой заказа\n' \
           f'*📩 Новости* - почитать последние новости/акции нашего заведения\n' \
           f'*📋 Заказы* - получить информацию о последнем заказе и добавить его содержимое в корзину\n' \
           f'*⚙️ Настройки* - изменить некоторые настройки в нашем сервисе\n\n' \
           f'_Если у вас возникнут вопросы, вы всегда можете связаться с нашим оператором ' \
           f'по телефону:_\n☎️`+666(66)666-66-66`'


# Обработчик команды получения помощи.
@bot.message_handler(commands=['help'])
def help_handler(message):
    bot.send_message(chat_id=message.from_user.id,
                     text=get_help_text(message.from_user.first_name),
                     parse_mode='Markdown')


# Обработчик текстовых сообщений кнопок главного меню.
@bot.message_handler(content_types=['text'])
def general_markup_handler(message):
    if message.text == '🍴 Меню':
        bot.send_message(chat_id=message.chat.id,
                         text='🍴 Меню нашего заведения',
                         reply_markup=catalog_markup(db.get_catalogs()))

    elif message.text == '🛒 Корзина':
        basket = db.get_products_in_basket(message.from_user.id)
        if len(basket) != 0:
            total_price = 0.00  # Сумма заказа.
            for item in basket:
                product = db.get_product(item[2])
                total_price = total_price + product[4] * item[3]

                bot.send_message(chat_id=message.chat.id,
                                 text=f'*{product[2]}*, {item[3]} шт',
                                 reply_markup=product_in_basket_markup(item[2]),
                                 parse_mode='Markdown')
                sleep(0.2)

            address = db.get_user_delivery_address(message.from_user.id)
            if address is None:
                address = 'нет данных'

            bot.send_message(chat_id=message.chat.id,
                             text=f'*Сумма заказа:* {total_price} руб\n'
                                  f'*Адрес доставки:* {address}\n',
                             parse_mode='Markdown',
                             reply_markup=confirm_basket_markup())
        else:
            bot.send_message(chat_id=message.chat.id,
                             text='❕Ваша корзина пуста')

    elif message.text == '📋 Заказы':
        last_order = db.get_last_order_info(message.from_user.id)
        if last_order:
            bot.send_message(chat_id=message.chat.id,
                             text=last_order,
                             reply_markup=last_order_markup())
        else:
            bot.send_message(chat_id=message.chat.id,
                             text='У вас нет ни одного заказа')

    elif message.text == '📩 Новости':
        news_text = '📌_Новости нашего заведения_\n\n'
        for news in db.get_news():
            news_text = f'{news_text}📝{news[1][8:10]}.{news[1][5:7]}.{news[1][:4]}\n{news[0]}\n\n'
        bot.send_message(chat_id=message.chat.id,
                         text=news_text,
                         parse_mode='Markdown')

    elif message.text == '⚙️ Настройки':
        phone_status = '❌'
        address_status = '❌'
        if db.user_has_phone(message.from_user.id):
            phone_status = '✅'
        if db.user_has_delivery_address(message.from_user.id):
            address_status = '✅'

        bot.send_message(chat_id=message.chat.id,
                         text=f'⚙️ *Ваши настройки*\n\n'
                              f'☎️ Контактный номер: {phone_status}\n'
                              f'🚚 Адрес доставки: {address_status}\n\n'
                              f'_Чтобы изменить адрес доставки напишите_ `/address` \n'
                              '_Пример:_ `/address Лобанка19 кв41`',
                         parse_mode='Markdown')

    elif message.text == '❔Помощь':
        bot.send_message(chat_id=message.chat.id,
                         text=get_help_text(message.from_user.first_name),
                         parse_mode='Markdown')
    # Обработчик любого иного текстового сообщения.
    else:
        # reply_to - отвечает на сообщение.
        bot.reply_to(message=message,
                     text='<неверная_команда>')


# if __name__ == '__main__':
#     # После вызова этой функции TeleBot начинает опрашивать серверы Telegram на наличие новых сообщений.
#     # - interval: int (по умолчанию 0) - Интервал между запросами на опрос.
#     # - timeout: integer (по умолчанию 20) - Тайм-аут в секундах для длительного опроса.
#     # - Allowed_updates: список строк (по умолчанию нет) - список типов обновлений для запроса.
#     bot.infinity_polling()
