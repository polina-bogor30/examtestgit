from tkinter import *
import pyodbc
from pyodbc import Error
from tkinter import ttk, messagebox

class SalesHistory(Toplevel):
    def __init__(self, parent, partner_name):
        super().__init__(parent)
        self.title(f'История продаж для {partner_name}')
        self.geometry('600x400')
        self.data_frame =Frame(self, bg='#FFFCFF')
        self.data_frame.pack()
        self.load_history(partner_name)

    def load_history(self, partner_name):
        connection = (
            r'DRIVER={SQL Server};'
            r'SERVER=HOME-PC\SQLEXPRESS1;'
            r'DATABASE=IS_43;'
            r'TRUSTED_CONNECTION=yes'
        )
        conn = pyodbc.connect(connection)
        cursor = conn.cursor()

        try:
            cursor.execute('''select Продукция, КоличествоПродукции, ДатаПродажи 
            from Partner_products_import
            where НаименованиеПартнера=?''', (partner_name,))
            history_data = cursor.fetchall()

            for row in history_data:
                self.frame_data = Frame(self.data_frame)
                self.frame_data.pack(expand=True, fill='x')
                self.label_data = ttk.Label(self.frame_data, text=f'Продукция: {row[0]}\nКоличество продукции: {row[1]}\nДата продажи: {row[2]}', font=('Seroe UI', 15))
                self.label_data.pack(side='left')



        except Error as e:
            messagebox.showerror('Ошибка', f'Ошибка подключения к бд: {e}')

        finally:
            conn.close()

class MaterialCalculate(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Расчет материалов')
        self.geometry('350x150')

        self.label_matID = Label(self, text='Введите тип материала')
        self.label_matID.grid(row=0, column=0)
        self.entry_matID = Entry(self)
        self.entry_matID.grid(row=0, column=1)

        self.label_typeID = Label(self, text='Введите тип продукции')
        self.label_typeID.grid(row=1, column=0)
        self.entry_typeID = Entry(self)
        self.entry_typeID.grid(row=1, column=1)

        self.label_quant = Label(self, text='Введите количество продукции')
        self.label_quant.grid(row=2, column=0)
        self.entry_quant = Entry(self)
        self.entry_quant.grid(row=2, column=1)

        self.label_param1 = Label(self, text='Введите длинну')#длинна
        self.label_param1.grid(row=3, column=0)
        self.entry_param1 = Entry(self)
        self.entry_param1.grid(row=3, column=1)

        self.label_param2 = Label(self, text='Введите ширину')#ширина
        self.label_param2.grid(row=4, column=0)
        self.entry_param2 = Entry(self)
        self.entry_param2.grid(row=4, column=1)

        Button(self, text='Рассчитать', command=self.on_calculate).grid(row=5, column=0, columnspan=2)

    def on_calculate(self):
        type_id = int(self.entry_typeID.get())
        mat_id = int(self.entry_matID.get())
        quant = int(self.entry_quant.get())
        param1 = float(self.entry_param1.get())
        param2 = float(self.entry_param2.get())

        if param1<=0 or param2<=0 or quant<=0:
            return

        resalt = self.calculate_material(type_id, mat_id, quant, param1, param2)

        if resalt == -1:
            messagebox.showerror('Ошибка ввода', 'Введите требуемое количество данных')
        else:
            messagebox.showinfo('Результат: ', f'Требуемое количество материала {resalt}')

    def calculate_material(self, type_id, mat_id, quant, param1, param2):
        connection = (
            r'DRIVER={SQL Server};'
            r'SERVER=HOME-PC\SQLEXPRESS1;'
            r'DATABASE=IS_43;'
            r'TRUSTED_CONNECTION=yes'
        )
        conn = pyodbc.connect(connection)

        if conn is None:
            return -1

        cursor = conn.cursor()

        try:
            cursor.execute('''select КоэффициентТипаПродукции
            from Product_type_import
            where ID=?''', (type_id,))

            type_cof = cursor.fetchone()

            if type_cof is None:
                return -1

            cursor.execute('''select ПроцентБракаМатериала
            from Material_type_import
            where ID=?''', (mat_id, ))

            mat_cof = cursor.fetchone()

            if mat_cof is None:
                return -1

            mat_quand = param1*param2*type_cof[0]
            total_mat = mat_quand*quant*(1+mat_cof[0]/100)
            return round(total_mat)

        except Error as e:
            messagebox.showerror('Ошибка', f'Ошибка подключения к бд: {e}')
        finally:
            conn.close()

if __name__=="__main__":
    root = Tk()
    app = SalesHistory(root, "partner")
    root.mainloop()