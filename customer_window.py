from tkinter import messagebox
import tkinter as tk
from tkinter.messagebox import showinfo, askyesno
from tkinter.ttk import Treeview

import db_manager as db
import login_window
import my_config


CUSTOMER_WINDOW_SIZE = "650x600"

PRODUCT_COLUMNS = ('Id', 'Название книги', 'Стоимость', 'На складе')
PRODUCT_COLUMNS_SIZE = (25, 250, 70, 70)

MY_ORDERS_COLUMNS = ('Id', 'Название книги', 'Колличество', 'Итоговая стоимость')
MY_ORDERS_COLUMNS_SIZE = (25, 250, 80, 120)



class CustomerApp:


    def __init__(self, master):

        self.master = master
        self.master.geometry(CUSTOMER_WINDOW_SIZE)
        self.master.configure(bg=my_config.BACKGROUND)
        self.master.title(my_config.APP_NAME)

        # main frames
        self.frame = tk.Frame(self.master, bg=my_config.BACKGROUND)
        self.function_frame = tk.Frame(self.master, bg=my_config.BACKGROUND)
        self.function_frame2 = tk.Frame(self.master, bg=my_config.BACKGROUND)
        self.function_frame3 = tk.Frame(self.master, bg=my_config.BACKGROUND)

        # it contains error messages, for example not all entry are filled.
        self.error_label = tk.Label()

        self.product_tree = None
        self.my_orders_tree = None
        self.location_entry = None
        self.quantity_entry = None
        self.id_product_entry = None

    def initialize_main_buttons(self):

        if self.frame:
            self.frame.destroy()
        if self.function_frame:
            self.function_frame.destroy()
        if self.function_frame2:
            self.function_frame2.destroy()
        if self.function_frame3:
            self.function_frame3.destroy()

        self.frame = tk.Frame(self.master, bg=my_config.BACKGROUND)
        search_button = tk.Button(self.frame, text='Книги',
                                  bg=my_config.FOREGROUND, command=self.list_products, width=16)
        search_button.grid(row=0, column=0, pady=(0, 3), padx=(10, 0))
        edit_button = tk.Button(self.frame, text='Редактировать аккаунт', bg=my_config.FOREGROUND,
                                command=self.account_edit, width=20)
        edit_button.grid(row=0, column=1, pady=(0, 3), padx=(10, 0))
        orders_button = tk.Button(self.frame, text='Мои покупки', bg=my_config.FOREGROUND,
                                  command=self.my_orders, width=16)
        orders_button.grid(row=0, column=2, pady=(0, 3), padx=(10, 0))
        logoff_button = tk.Button(self.frame, text='Выйти', bg=my_config.LOGOUT,
                                  command=self.log_off, width=16)
        logoff_button.grid(row=0, column=3, pady=(0, 3), padx=(10, 0))
        self.frame.pack()

    def list_products(self):

        self.initialize_main_buttons()

        # frame for listbox
        self.function_frame = tk.Frame(self.master, bg=my_config.BACKGROUND)
        self.function_frame.pack()
        self.function_frame2 = tk.Frame(self.master, bg=my_config.BACKGROUND)
        self.function_frame2.pack()

        list_label = tk.Label(self.function_frame, text='Покупка книг',
                              width=100, bg=my_config.BACKGROUND)
        list_label.grid(row=0, column=0, pady=(10, 0))


        self.product_tree = Treeview(self.function_frame, columns=PRODUCT_COLUMNS,
                                     show='headings', height=10)
        self.product_tree.grid(row=1, column=0, padx=8)

        for column_name, width in zip(PRODUCT_COLUMNS, PRODUCT_COLUMNS_SIZE):
            self.product_tree.column(column_name, width=width, anchor=tk.CENTER)
            self.product_tree.heading(column_name, text=column_name)

        scrollbar = tk.Scrollbar(self.function_frame, orient=tk.VERTICAL)
        scrollbar.configure(command=self.product_tree.set)
        self.product_tree.configure(yscrollcommand=scrollbar)
        self.product_tree.bind('<ButtonRelease-1>', self.product_selection)


        records = db.return_products()
        for record in records:
            self.product_tree.insert('', tk.END, values=[record[0], record[1], record[2], record[3]])


        id_product_label = tk.Label(self.function_frame2, text='ID продукта:', bg=my_config.BACKGROUND)
        id_product_label.grid(row=0, column=0, sticky=tk.E)
        quantity_label = tk.Label(self.function_frame2, text='Количество:', bg=my_config.BACKGROUND)
        quantity_label.grid(row=1, column=0, sticky=tk.E)
        location_label = tk.Label(self.function_frame2, text='Местоположение:', bg=my_config.BACKGROUND)
        location_label.grid(row=2, column=0, sticky=tk.E)


        self.id_product_entry = tk.Entry(self.function_frame2, width=30, bg=my_config.FOREGROUND)
        self.id_product_entry.grid(row=0, column=1)
        self.quantity_entry = tk.Entry(self.function_frame2, width=30, bg=my_config.FOREGROUND)
        self.quantity_entry.grid(row=1, column=1)
        self.location_entry = tk.Entry(self.function_frame2, width=30, bg=my_config.FOREGROUND)
        self.location_entry.grid(row=2, column=1)


        place_order_button = tk.Button(self.function_frame2, text='Купить',
                                       bg=my_config.FOREGROUND, command=self.place_order, width=16)
        place_order_button.grid(row=4, column=0)
        details_button = tk.Button(self.function_frame2, text='подробности',
                                   bg=my_config.FOREGROUND, command=self.product_details, width=16)
        details_button.grid(row=4, column=1, )

    def place_order(self):

        if self.error_label:
            self.error_label.destroy()


        if not self.id_product_entry.get():
            self.error_message("'id product' отсутствует")
        elif not my_config.is_integer(self.quantity_entry.get()) or int(self.quantity_entry.get()) < 1:
            self.error_message("'количество' Должно быть положительным целым числом")
        elif not self.location_entry.get():
            self.error_message("'местоположение' отсутствует")

        elif not db.is_customer_id_exist(my_config.MY_ID) or not db.is_product_id_exists(
                self.id_product_entry.get()):
            self.error_message("идентификатор продукта или клиента не существует")

        elif db.add_order(my_config.MY_ID, self.id_product_entry.get(), self.quantity_entry.get(),
                          self.location_entry.get()):
            result = askyesno(title="Подтвержение операции", message="Подтвердить операцию?")
            if result:
                messagebox.showinfo("Уведомление", 'Вы успешно купили.')
                self.list_products()
            else:
                showinfo("Результат", "Операция отменена")

        else:
            self.error_message("недостаточно товаров на складе.")

    def product_details(self):

        if self.error_label:
            self.error_label.destroy()
        if self.function_frame3:
            self.function_frame3.destroy()

        if not self.id_product_entry.get():
            self.error_message("выберите продукт.")

        elif db.is_product_id_exists(self.id_product_entry.get()):

            self.function_frame3 = tk.Frame(self.master, bg=my_config.BACKGROUND)
            self.function_frame3.pack(side=tk.TOP)

            description = db.return_product(self.id_product_entry.get())[4]
            self.error_label = tk.Message(self.function_frame3, text="Описание: {}".format(description),
                                          bg=my_config.BACKGROUND, width=300)
            self.error_label.grid(row=5, column=0)
        else:
            self.error_message("Товара не существует.")

    def product_selection(self, event):

        try:
            if self.product_tree.selection():
                record = self.product_tree.set(self.product_tree.selection())
                self.id_product_entry.delete(0, tk.END)
                self.id_product_entry.insert(tk.END, record[PRODUCT_COLUMNS[0]])

        except KeyError:
            pass

    def order_selection(self, event):

        if self.my_orders_tree.selection():
            record = self.my_orders_tree.set(self.my_orders_tree.selection())
            record = db.return_order(record[PRODUCT_COLUMNS[0]])

            if self.function_frame2:
                self.function_frame2.destroy()

            self.function_frame2 = tk.Frame(self.master, bg=my_config.BACKGROUND)
            self.function_frame2.pack(side=tk.TOP)


            order_info = ("количество: \t{}\nИтоговая цена: \t{}\nстатус платежа: \t{}\n"
                          "Статус отправки: \t{}\nдата заказа: \t{}\nМестоположение: \t{}\n"
                          ).format(record[3], record[4], record[5], record[6], record[7], record[8])

            self.error_label = tk.Message(self.function_frame2, text=order_info,
                                          bg=my_config.BACKGROUND, width=300)
            self.error_label.grid(row=0, column=0)

    def account_edit(self):

        if self.frame:
            self.frame.destroy()
        if self.function_frame:
            self.function_frame.destroy()
        if self.function_frame2:
            self.function_frame2.destroy()
        if self.function_frame3:
            self.function_frame3.destroy()
        AccountEdit(self.master)

    def my_orders(self):
        self.initialize_main_buttons()

        self.function_frame = tk.Frame(self.master, bg=my_config.BACKGROUND)
        self.function_frame.pack()

        list_label = tk.Label(self.function_frame, text='мои покупки:', width=100, bg=my_config.BACKGROUND)
        list_label.grid(row=0, column=0, pady=(10, 0))

        self.my_orders_tree = Treeview(self.function_frame, columns=MY_ORDERS_COLUMNS,
                                       show='headings', height=10)
        self.my_orders_tree.grid(row=1, column=0)

        for column_name, width in zip(MY_ORDERS_COLUMNS, MY_ORDERS_COLUMNS_SIZE):
            self.my_orders_tree.column(column_name, width=width, anchor=tk.CENTER)
            self.my_orders_tree.heading(column_name, text=column_name)

        scrollbar = tk.Scrollbar(self.function_frame, orient=tk.VERTICAL)
        scrollbar.configure(command=self.my_orders_tree.set)
        self.my_orders_tree.configure(yscrollcommand=scrollbar)
        self.my_orders_tree.bind('<ButtonRelease-1>', self.order_selection)

        records = db.orders_product_info(my_config.MY_ID)
        for record in records:
            self.my_orders_tree.insert('', tk.END, values=[record[0], record[1], record[2], record[3]])

    def error_message(self, name):

        if self.error_label:
            self.error_label.destroy()

        self.error_label = tk.Label(self.function_frame2, text=name, bg=my_config.BACKGROUND,
                                    fg=my_config.ERROR_FOREGROUND)
        self.error_label.grid(row=3, column=1)

    def log_off(self):

        if self.frame:
            self.frame.destroy()
        if self.function_frame:
            self.function_frame.destroy()
        if self.function_frame2:
            self.function_frame2.destroy()
        if self.function_frame3:
            self.function_frame3.destroy()
        application = login_window.LoginWindow(self.master)
        application.initialize_login_window()


class AccountEdit:

    def __init__(self, master):

        self.master = master
        self.master.configure(bg=my_config.BACKGROUND)
        self.master.title(my_config.APP_NAME)
        self.master.geometry(CUSTOMER_WINDOW_SIZE)


        self.error_label = tk.Label()

        self.frame = tk.Frame(self.master, bg=my_config.BACKGROUND)
        self.frame.pack()

        new_password_label = tk.Label(self.frame, text='Новый пароль:', bg=my_config.BACKGROUND)
        new_password_label.grid(row=1, column=0, pady=(10, 0), sticky=tk.E)
        password_label = tk.Label(self.frame, text='Пароль:', bg=my_config.BACKGROUND)
        password_label.grid(row=2, column=0, sticky=tk.E)
        name_label = tk.Label(self.frame, text='Имя:', bg=my_config.BACKGROUND)
        name_label.grid(row=3, column=0, pady=(4, 0), sticky=tk.E)
        phone_label = tk.Label(self.frame, text='Телефон:', bg=my_config.BACKGROUND)
        phone_label.grid(row=4, column=0, pady=(4, 0), sticky=tk.E)
        email_label = tk.Label(self.frame, text='Почта:', bg=my_config.BACKGROUND)
        email_label.grid(row=5, column=0, pady=(4, 0), sticky=tk.E)

        self.new_password_entry = tk.Entry(self.frame, width=22, show='*', bg=my_config.FOREGROUND)
        self.new_password_entry.grid(row=1, column=1, pady=(10, 0))
        self.password_entry = tk.Entry(self.frame, width=22, show='*', bg=my_config.FOREGROUND)
        self.password_entry.grid(row=2, column=1)
        self.name_entry = tk.Entry(self.frame, width=22, bg=my_config.FOREGROUND)
        self.name_entry.grid(row=3, column=1)
        self.phone_entry = tk.Entry(self.frame, width=22, bg=my_config.FOREGROUND)
        self.phone_entry.grid(row=4, column=1)
        self.email_entry = tk.Entry(self.frame, width=22, bg=my_config.FOREGROUND)
        self.email_entry.grid(row=5, column=1)


        self.change_button = tk.Button(self.frame, text='изменить', bg=my_config.FOREGROUND,
                                       command=self.set_change, width=16)
        self.change_button.grid(row=1, column=2, padx=(10, 0), pady=(10, 0))
        self.cancel_button = tk.Button(self.frame, text='Отмена', bg=my_config.FOREGROUND,
                                       command=self.exit, width=16)
        self.cancel_button.grid(row=2, column=2, padx=(10, 0))

        customer_info = db.return_customer(my_config.MY_ID)
        if customer_info:
            self.name_entry.insert(tk.END, customer_info[3])
            self.phone_entry.insert(tk.END, customer_info[4])
            self.email_entry.insert(tk.END, customer_info[5])
        else:
            messagebox.showinfo("Уведомление", 'ERROR: WRONG ID!!!')
            self.exit()

    def set_change(self):
        if self.error_label:
            self.error_label.destroy()

        if 0 < len(self.new_password_entry.get()) < 6:
            self.error_message('Минимальная длина пароля — 6')

        elif self.password_entry.get() != db.return_customer(my_config.MY_ID)[2]:
            self.error_message('Пароль не подходит.')
        elif not self.name_entry.get():
            self.error_message('Нельзя оставить пустое имя.')
        elif self.phone_entry.get() and not my_config.is_integer(self.phone_entry.get()):
            self.error_message("неправильный номер телефона.")
        elif not self.email_entry.get():
            self.error_message('Нельзя оставить пустую почту.')

        else:

            if self.new_password_entry:
                db.edit_customer(my_config.MY_ID, self.new_password_entry.get(), self.name_entry.get(),
                                 self.email_entry.get(),
                                 self.phone_entry.get())
            else:

                db.edit_customer(my_config.MY_ID,
                                 db.return_customer(my_config.MY_ID)[2], self.name_entry.get(),
                                 self.email_entry.get(), self.phone_entry.get())

            self.error_message("Аккаунт обновлен.")

    def error_message(self, name):

        if self.error_label:
            self.error_label.destroy()

        self.error_label = tk.Label(self.frame, fg=my_config.ERROR_FOREGROUND,
                                    text=name, bg=my_config.BACKGROUND)
        self.error_label.grid(row=6, column=1)

    def exit(self):

        self.frame.destroy()
        application = CustomerApp(self.master)
        application.initialize_main_buttons()
