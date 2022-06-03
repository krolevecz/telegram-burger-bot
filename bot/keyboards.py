from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from filter import catalogs_factory, add_products_factory, delete_products_factory, remove_products_factory


# Клавиатура ОБЩАЯ.
def general_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = KeyboardButton(text='🍴 Меню')
    btn2 = KeyboardButton(text='🛒 Корзина')
    btn3 = KeyboardButton(text='📩 Новости')
    btn4 = KeyboardButton(text='📋 Заказы')
    btn5 = KeyboardButton(text='⚙️ Настройки')
    btn6 = KeyboardButton(text='❔Помощь')
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return markup


# Клавиатура МЕНЮ.
def catalog_markup(catalogs):
    markup = InlineKeyboardMarkup()
    for catalog in catalogs:
        markup.add(InlineKeyboardButton(
            text=catalog[1],
            callback_data=catalogs_factory.new(catalog_id=catalog[0])))
    return markup


# Клавиатура управления продуктами в корзине.
def product_in_basket_markup(product_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(InlineKeyboardButton(text='➕',
                                    callback_data=add_products_factory.new(product_id=product_id)),
               InlineKeyboardButton(text='➖',
                                    callback_data=delete_products_factory.new(product_id=product_id)),
               InlineKeyboardButton(text='❌',
                                    callback_data=remove_products_factory.new(product_id=product_id)))
    return markup


# Кнопка 'Добавить в корзину' под каждым продуктом.
def add_product_markup(product_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(text='☑️ Добавить в корзину',
                                    callback_data=add_products_factory.new(product_id=product_id)))
    return markup


# Кнопка подтверждения заказа.
def confirm_basket_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(
        text='📬 Оформить заказ',
        callback_data='confirm_basket'))
    return markup


# Кнопка добавления последнего заказа в корзину.
def last_order_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(
        text='☑️ Добавить в корзину',
        callback_data='put_last_order'))
    return markup


# Кнопка для отправления контактных данных пользователя.
def phone_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = KeyboardButton(text='☎️ Отправить контактный номер', request_contact=True)
    markup.add(btn1)
    return markup
