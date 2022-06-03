from telebot import TeleBot, types
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter

catalogs_factory = CallbackData('catalog_id', prefix='catalogs')
add_products_factory = CallbackData('product_id', prefix='add_products')
delete_products_factory = CallbackData('product_id', prefix='delete_products')
remove_products_factory = CallbackData('product_id', prefix='remove_products')


class CatalogsCallbackFilter(AdvancedCustomFilter):
    key = 'catalogs_config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


class ProductsCallbackFilter(AdvancedCustomFilter):
    key = 'products_config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


def bind_filters(bot: TeleBot):
    bot.add_custom_filter(CatalogsCallbackFilter())
    bot.add_custom_filter(ProductsCallbackFilter())
