import sqlite3


class DBHelper:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(database=db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()
        print("База данных подключена к SQLite.")

        self.cursor.execute(
            'PRAGMA foreign_keys = ON;')
        self.connection.commit()  # Сохраняем изменения.
        print("Внешние ключи включены.")

    # users - Таблица пользователей.
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS  users (
            user_id INTEGER PRIMARY KEY, 
            user_name TEXT, 
            phone TEXT,
            delivery_address TEXT);''')
        self.connection.commit()
        print("Таблица (users) создана.")

    # catalogs - Таблица каталогов продуктов.
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS  catalogs (
            catalog_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            catalog_name TEXT UNIQUE );''')
        self.cursor.execute(
            '''INSERT INTO catalogs 
            (catalog_name) 
            VALUES 
            ("🍔 Бургеры"), 
            ("🍟 Закуски"), 
            ("🥤 Напитки"), 
            ("🍱 Наборы");''')
        self.connection.commit()
        print("Таблица (catalogs) создана и инициализирована.")

    # products - Таблица продуктов.
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS  products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            catalog_id INTEGER NOT NULL, 
            product_name TEXT NOT NULL UNIQUE, 
            description TEXT,
            price REAL NOT NULL,
            photo_url TEXT,
            FOREIGN KEY (catalog_id) REFERENCES catalogs (catalog_id) ON DELETE CASCADE );''')
        self.cursor.execute(
            '''INSERT INTO products 
            (catalog_id, product_name, description, price, photo_url) 
            VALUES 
            (1, "Бургер «ГРУШЕВКА»", "Говядина, сыр «Фета», сыр «Чеддер», груша, брусничный соус, базилик.", 17.00, "grushevka.png"), 
            (1, "Бургер «ДАБЛ БИФ»", "Говядина, сыр «Чеддер», бекон, соус «1000 островов».", 14.00, "dabl_bif.png"), 
            (1, "Бургер «АМЕРИКАНСКИЙ»", "Говядина, сыр «Чеддер», соус «1000 островов», томат, лук красный, бекон, салат айсберг, корнишоны.", 17.00, "americanskiy.png"), 
            (1, "Бургер «ЧИПОЛЛИНО»", "Фермерская говядина, сыр «Чеддер», ароматный бекон, лук карамелизированный, лук красный маринованный, соус «Барбекю».", 15.00, "chipollino.png"), 
            (1, "Бургер «РВАНЫЙ»", "Реберное томленое мясо (свинина), сыр «Сулугуни», соус «Чипотле», салат.", 20.00, "rvaniy.png"), 
            (2, "Куриные наггетсы", "Куриные наггетсы, картофель фри, соус.", 14.00, "nagetsy.jpeg"), 
            (2, "Картофель фри соломкой", "Картофель фри и ничего больше.", 5.00, "fri.png"), 
            (2, "Картофель фри с соусом и беконом", "Хрустящий картофель фри, ароматный бекон, сырный соус.", 10.00, "fri_s_sousom_i_bekonom.png"), 
            (3, "Coca-Cola", "Напиток газированный Coca-Cola 250 мл.", 2.50, "cola.png"),
            (3, "Sprite", "Напиток газированный Sprite 250 мл.", 2.50, "sprite.png"),
            (3, "Fanta", "Напиток газированный Fanta «Апельсин» 250 мл.", 2.50, "fanta.png"),
            (4, "Набор №1", "Сыр фри, луковые кольца, наггетсы, картофельные чипсы, сырные палки, крылья в соусе «Терияки», лук фри, кетчуп, соус «Тартар».", 21.00, "nabor_1.jpeg"),
            (4, "Набор №2", "Крылья в соусе «Барбекю», ребра запеченные, пряный картофель, сыр фри, кольца кальмара в темпуре, колбаски на гриле, лук маринованный, чипсы картофельные, лук фри, огурец маринованный, соус «1000 островов», соус «Ранч».", 38.00, "nabor_2.jpeg");''')
        self.connection.commit()
        print("Таблица (products) создана и инициализирована.")

    # basket_lines - Таблица записей в корзине.
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS  basket_lines (
            basket_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_id INTEGER, 
            product_id INTEGER, 
            product_count INTEGER, 
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE );''')
        self.connection.commit()
        print("Таблица (basket_lines) создана.")

    # orders - Таблица заказов.
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS  orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_id INTEGER, 
            date_time TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE );''')
        self.connection.commit()
        print("Таблица (orders) создана.")

    # order_lines - Таблица записей продуктов для каждого заказа.
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS  order_lines (
            order_line_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            order_id INTEGER, 
            product_id INTEGER, 
            product_count INTEGER, 
            FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE, 
            FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE );''')
        self.connection.commit()
        print("Таблица (order_lines) создана.")

    # news = Таблица новостей.
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS news (
            news_id INTEGER PRIMARY KEY AUTOINCREMENT,
            news_text TEXT NOT NULL,
            news_date TEXT NOT NULL)'''
        )
        self.connection.commit()
        print("Таблица (news) создана.")

        self.cursor.execute(
            '''INSERT INTO news 
            (news_text, news_date) 
            VALUES 
            ("Мы открылись", datetime("now")), 
            ("Свежая новость", datetime("now", "3 hours"));''')
        self.connection.commit()

    def user_has_phone(self, user_id):
        """Проверяем, отправил ли пользователь свой контактный номер"""
        result = self.cursor.execute(
            'SELECT phone FROM users WHERE user_id = ?;',
            (user_id,))
        return result.fetchone()[0] is not None

    def user_has_delivery_address(self, user_id):
        """Проверяем, указал ли пользователь адрес доставки"""
        result = self.cursor.execute(
            'SELECT delivery_address FROM users WHERE user_id = ?;',
            (user_id,))
        return result.fetchone()[0] is not None

    def get_user_delivery_address(self, user_id):
        """Получаем адрес доставки пользователя"""
        result = self.cursor.execute(
            'SELECT delivery_address FROM users WHERE user_id = ?;',
            (user_id,))
        return result.fetchone()[0]

    def save_user_phone(self, user_id, phone):
        """Сохраняем контакт пользователя"""
        self.cursor.execute(
            'UPDATE users SET phone =  ? WHERE user_id = ?;',
            (phone, user_id,))
        return self.connection.commit()

    def save_user_delivery_address(self, user_id, delivery_address):
        """Сохраняем адрес доставки пользователя"""
        self.cursor.execute(
            'UPDATE users SET delivery_address =  ? WHERE user_id = ?;',
            (delivery_address, user_id,))
        return self.connection.commit()

    def get_news(self):
        """Получаем новости"""
        result = self.cursor.execute(
            'SELECT news_text, news_date FROM news;')
        return result.fetchall()

    def add_order(self, user_id):
        """Добавляем новый заказ в таблицу заказов и заполняем таблицу записей продуктов заказа"""
        self.cursor.execute(
            'INSERT INTO orders (user_id, date_time) VALUES (?, datetime("now", "3 hours"));',
            (user_id,))
        result = self.cursor.execute(
            'SELECT order_id FROM orders WHERE user_id = ? ORDER BY order_id DESC LIMIT 1;',
            (user_id,)).fetchone()
        # Получаем order_id только что созданного заказа.
        order_id = result[0]

        basket = self.get_products_in_basket(user_id=user_id)
        for item in basket:
            self.cursor.execute(
                'INSERT INTO order_lines (order_id, product_id, product_count) VALUES (?, ?, ?);',
                (order_id, item[2], item[3],))

        print(f'Пользователь {user_id} сделал новый заказ.')
        return self.connection.commit()

    def add_user(self, user_id, user_name, phone, delivery_address):
        """Добавляем пользователя в базу"""
        self.cursor.execute(
            'INSERT INTO users (user_id, user_name, phone, delivery_address) VALUES (?, ?, ?, ?);',
            (user_id, user_name, phone, delivery_address))
        print(f'Добавлен новый пользователь ({user_name})')
        return self.connection.commit()

    def add_basket_line(self, user_id, product_id):
        """Добавляем продукт в коризну (если нету -> новая запись, если есть -> увеличиваем count)"""
        # Проверяем есть ли такой товар в корзине у такого пользователя.
        result = self.cursor.execute(
            'SELECT * FROM basket_lines WHERE user_id = ? AND product_id = ?;',
            (user_id, product_id,))
        # Если подобных записей в базе нет, создаём и ставим count = 1.
        if result.fetchone() is None:
            self.cursor.execute(
                'INSERT INTO basket_lines (user_id, product_id, product_count) VALUES (?, ?, ?);',
                (user_id, product_id, 1))
            return self.connection.commit()
        # Если такая запись есть, увеличиваем количество count на 1.
        else:
            self.cursor.execute(
                'UPDATE basket_lines SET product_count = product_count + 1 WHERE user_id = ? AND product_id = ?;',
                (user_id, product_id,))
            return self.connection.commit()

    def remove_basket_line(self, user_id, product_id):
        """Удаляет продукт из корзины"""
        self.cursor.execute(
            'DELETE FROM basket_lines WHERE user_id = ? AND product_id = ?;',
            (user_id, product_id,))
        return self.connection.commit()

    def delete_basket_line(self, user_id, product_id):
        """Уменьшает количество продукта в коризне"""
        result = self.cursor.execute(
            'SELECT * FROM basket_lines WHERE user_id = ? AND product_id = ?;',
            (user_id, product_id,)).fetchone()
        # Удаляем если продукт в корзине в количестве 1 ед.
        if result[3] == 1:
            self.remove_basket_line(user_id=user_id, product_id=product_id)
        else:
            self.cursor.execute(
                'UPDATE basket_lines SET product_count = product_count - 1 WHERE user_id = ? AND product_id = ?;',
                (user_id, product_id,))
            return self.connection.commit()

    def get_products_in_basket(self, user_id):
        """Получаем список продуктов в корзине пользователя."""
        result = self.cursor.execute(
            'SELECT * FROM basket_lines WHERE user_id = ?;',
            (user_id,))
        return result.fetchall()

    def user_has_product_in_basket(self, user_id, product_id):
        """Проверяем есть ли продукт в корзине у пользователя"""
        result = self.cursor.execute(
            'SELECT * FROM basket_lines WHERE user_id = ? AND product_id = ?;',
            (user_id, product_id,))
        return bool(len(result.fetchall()))

    def clear_basket(self, user_id):
        """Очищает корзину пользователя"""
        self.cursor.execute(
            'DELETE FROM basket_lines WHERE user_id = ?;',
            (user_id,))
        return self.connection.commit()

    def get_users(self):
        """Получаем всех пользователей из таблицы (users)"""
        return self.cursor.execute('SELECT * FROM users;').fetchall()

    def get_catalogs(self):
        """Получаем все каталоги продуктов из таблицы (catalogs)"""
        return self.cursor.execute('SELECT * FROM catalogs;').fetchall()

    def get_products(self, catalog_id):
        """Получаем все продукты выбранного каталога из таблицы (products)"""
        return self.cursor.execute('SELECT * FROM products WHERE catalog_id = ?;', (catalog_id,)).fetchall()

    def get_product(self, product_id):
        """Получаем продукт по его id"""
        return self.cursor.execute('SELECT * FROM products WHERE product_id = ?;', (product_id,)).fetchone()

    def get_last_order_info(self, user_id):
        """Получаем информацию о последнем заказе пользователя"""
        result = self.cursor.execute(
            'SELECT * FROM orders WHERE user_id = ? ORDER BY order_id DESC LIMIT 1;',
            (user_id,)).fetchone()
        if result is not None:
            last_order_id = result[0]  # order_id последнего заказа.
            result = self.cursor.execute(
                'SELECT product_id, product_count FROM order_lines WHERE order_id = ?;',
                (last_order_id,)).fetchall()
            text = '📎 Последний заказ:\n'
            for item in result:
                text = f'{text}{self.get_product(item[0])[2]}, {item[1]} шт\n'
            return text
        else:
            return False

    def put_last_order_to_basket(self, user_id):
        """Добавляем в корзину продукты из последнего заказа"""
        result = self.cursor.execute(
            'SELECT * FROM orders WHERE user_id = ? ORDER BY order_id DESC LIMIT 1;',
            (user_id,)).fetchone()
        last_order_id = result[0]   # order_id последнего заказа.
        result = self.cursor.execute(
            'SELECT product_id, product_count FROM order_lines WHERE order_id = ?;',
            (last_order_id,)).fetchall()
        for item in result:
            count = item[1]
            while count > 0:
                self.add_basket_line(user_id=user_id, product_id=item[0])
                count = count - 1
        return self.connection.commit()

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()
        print('Соединение с Базой Данных закрыто.')
