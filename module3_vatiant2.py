from tkinter import *
import pyodbc
from pyodbc import Error
from tkinter import ttk, messagebox
import module4_variant2

class PartnersApp(Tk):
    def __init__(self):
        super().__init__()
        self.title('Список партнеров')
        self.geometry('900x600')
        self.protocol('WM_DELETE_WINDOW', self.on_close)
        self.current_frame = None
        self.show_main_page()

    def show_main_page(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame=MainPage(self)
        self.current_frame.configure(bg='#CCCCCC')
        self.current_frame.pack(fill='both', expand=True)

    def show_edit_page(self, partner=None):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame=PartnerPage(self, partner)
        self.current_frame.configure(bg='#CCCCFF')
        self.current_frame.pack(fill='both', expand=True)

    def on_close(self):
        if messagebox.askokcancel("Выход", "Вы действительно хотите выйти?"):
            self.destroy()

class MainPage(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()
        self.load_partner()

    def create_widgets(self):
        self.canvas = Canvas(self, bg='#FFFFCC')
        self.scrollbar = Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.scrol_label_frame = Frame(self.canvas, bg='#BBBBBB')

        self.scrol_label_frame.bind("<Configure>",
                                    lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                                    )
        self.canvas.create_window((0, 0), window=self.scrol_label_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.canvas.yview)
        self.label = Label(self.scrol_label_frame, text='Данные о партнерах', font=('Segoe UI', 18))
        self.label.pack(pady=10)

        self.add_button = ttk.Button(self.scrol_label_frame, text='Добавить',
                                     command=lambda: self.parent.show_edit_page())
        self.add_button.pack(side='bottom')

        self.refresh_button = ttk.Button(self.scrol_label_frame, text='Обновление', command=self.parent.show_main_page)
        self.refresh_button.pack(side='bottom')

        self.mat_button = ttk.Button(self.scrol_label_frame, text='Расчет материалов', command=self.open_calculate)
        self.mat_button.pack(side='bottom')
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')
    def load_partner(self):
        connection = (
            r'DRIVER={SQL Server};'
            r'SERVER=HOME-PC\SQLEXPRESS1;'
            r'DATABASE=IS_43;'
            r'TRUSTED_CONNECION=yes'
        )
        conn = pyodbc.connect(connection)
        cursor = conn.cursor()
        try:

            cursor.execute('''select PPI.НаименованиеПартнера,
            SUM(PPI.КоличествоПродукции) as total_sale
            from Partner_products_import PPI
            group by PPI.НаименованиеПартнера''')#запрос на вывод данных

            result = cursor.fetchall()
            discount_list = []
            for НаименованиеПартнера, КоличествоПродукции in result:
                if КоличествоПродукции < 10000:
                    discount = 0
                elif 10000<=КоличествоПродукции<50000:
                    discount = 5
                elif 50000<=КоличествоПродукции<300000:
                    discount = 10
                else:
                    discount = 15
                discount_list.append((НаименованиеПартнера, discount))#подсчет и вывод данных в список
            cursor.execute('''select * from Partners_import''')
            data = cursor.fetchall()
            for row in data:
                self.frame_data = Frame(self.scrol_label_frame)
                self.frame_data.pack(expand=True, fill='x', pady=10, padx=5)
                self.edit_data_button = ttk.Button(self.frame_data, text='Изменить данные', command=lambda  r=row: self.edit_partners(r))
                self.edit_data_button.pack(side='right')
                self.label_data = ttk.Label(self.frame_data, text=f'{row[0]} | {row[1]}\n{row[2]}\n{row[5]}\nРейтинг: {row[7]}', font=('Seroe UI', 18))
                self.label_data.pack(side='left')
                for dis in discount_list: #вывод данных на экран в текстовое поле
                    if row[1] == dis[0]:
                        self.label_sale = ttk.Label(self.frame_data, text=f'{dis[1]}%', font=('Seroe UI', 18))
                        self.label_sale.pack(side='right')
                self.history_button = ttk.Button(self.frame_data, text='История', command=lambda r=row: self.show_history(r[1]))
                self.history_button.pack(side='right')

        except Error as e:
            messagebox.showerror('Ошибка', f'Ошибка подключения к базе данных: {e}')
        finally:
            conn.close()

    def open_calculate(self):
        mat_window = module4_variant2.MaterialCalculate(self.parent)
        mat_window.grab_set()

    def show_history(self, partner):
        sale_window = module4_variant2.SalesHistory(self.parent, partner)
        sale_window.grab_set()

    def edit_partners(self, partnet_data):
        self.parent.show_edit_page(partnet_data)

class PartnerPage(Frame):
    def __init__(self, parent, partner=None):
        super().__init__(parent)
        self.parent = parent
        self.partner = partner
        self.create_widgets()

    def create_widgets(self):
        print('1')
        self.label = Label(self, text='Добавить/редактировать', font=('Seroe UI', 20))
        self.label.pack()

        self.type_label = Label(self, text='Тип партнера', font=('Seroe UI', 18))
        self.type_label.pack()
        self.type_combobox = ttk.Combobox(self, values=["ЗАО", "ПАО", "ООО", "ОАО", "ИП"])
        self.type_combobox.pack()

        self.name_label = Label(self, text='Наименование партнера', font=('Seroe UI', 18))
        self.name_label.pack()
        self.name_entry = Entry(self)
        self.name_entry.pack()

        self.director_label = Label(self, text='Директор', font=('Seroe UI', 18))
        self.director_label.pack()
        self.director_entry = Entry(self)
        self.director_entry.pack()

        self.email_label = Label(self, text='E-mail', font=('Seroe UI', 18))
        self.email_label.pack()
        self.email_entry = Entry(self)
        self.email_entry.pack()

        self.number_label = Label(self, text='Номер телефона', font=('Seroe UI', 18))
        self.number_label.pack()
        self.number_entry = Entry(self)
        self.number_entry.pack()

        self.address_label = Label(self, text='Адрес', font=('Seroe UI', 18))
        self.address_label.pack()
        self.address_entry = Entry(self)
        self.address_entry.pack()

        self.inn_label = Label(self, text='ИНН', font=('Seroe UI', 18))
        self.inn_label.pack()
        self.inn_entry = Entry(self)
        self.inn_entry.pack()

        self.index_label = Label(self, text='Рейтинг партнера', font=('Seroe UI', 18))
        self.index_label.pack()
        self.index_entry =Entry(self)
        self.index_entry.pack()

        self.save_button = Button(self, text='Сохранить', command=self.save_partner)
        self.save_button.pack()

        self.back_button = Button(self, text='Назад', command=self.parent.show_main_page)
        self.back_button.pack()

        if self.partner:
            self.fill_form()

    def fill_form(self):
        self.type_combobox.set(self.partner[0])
        self.name_entry.insert(0, self.partner[1])
        self.director_entry.insert(0, self.partner[2])
        self.email_entry.insert(0, self.partner[3])
        self.number_entry.insert(0, self.partner[4])
        self.address_entry.insert(0, self.partner[5])
        self.inn_entry.insert(0, self.partner[6])
        self.index_entry.insert(0, self.partner[7])

    def save_partner(self):
        print('2')
        try:
            type = self.type_combobox.get()
            name = self.name_entry.get()
            director = self.director_entry.get()
            number = self.number_entry.get()
            address = self.address_entry.get()
            email = self.email_entry.get()
            inn = self.inn_entry.get()
            index = int(self.index_entry.get())

            if not type or not name or not director or not number or not address or not email or not inn or not index:
                raise ValueError('Заполните все поля')

            if index < 0:
                raise ValueError('Рейтинг не может быть отрицательным')

            connection = (
                r'DRIVER={SQL Server};'
                r'SERVER=HOME-PC\SQLEXPRESS1;'
                r'DATABASE=IS_43;'
                r'TRYSTED_CONNECTION=yes;'
            )
            conn = pyodbc.connect(connection)
            cursor = conn.cursor()

            if self.partner:
                print(inn)
                cursor.execute('''
                update Partners_import set
                ТипПартнера = ?, 
                НаименованиеПартнера = ?, 
                Директор = ?, 
                ЭлектроннаяПочтаПартнера = ?, 
                ТелефонПартнера = ?, 
                ЮридическийАдресПартнера = ?,
                Рейтинг = ?
                where ИНН = ?''', (type, name, director, email, number, address, index, inn))
            else:
                cursor.execute('''
                insert into Partners_import (
                ТипПартнера, НаименованиеПартнера, Директор, ЭлектроннаяПочтаПартнера, ТелефонПартнера, ЮридическийАдресПартнера, ИНН, Рейтинг)
                values (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (type, name, director, email, number, address, inn, index))
            conn.commit()
            messagebox.showinfo('Информация', 'Данные сохранены')
            self.parent.show_main_page()

        except ValueError as ve:
            messagebox.showerror('Ошибка данных', ve)
        finally:
            conn.close()

if __name__=='__main__':
    app = PartnersApp()
    app.mainloop()