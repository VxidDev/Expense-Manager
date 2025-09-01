import tkinter as tk
from tkinter import ttk
import functions
import os

window = tk.Tk()
window.geometry("700x450")
window.resizable(width=False , height=False)

window.config(bg="#3b3d3c")

currencies = ["USD" , "EUR" , "GBP", "PLN"]

# GUI
new_button = functions.tk_Button("Add New" , 10 , 3 , 50 , 300 , functions.add_new)

del_button = functions.tk_Button("Delete" , 10 , 3 , 175 , 300 , functions.del_expense)

edit_button = functions.tk_Button("Edit" , 10 , 3 , 300 , 300 , lambda: functions.edit_expense(False , 1))

clear_button = functions.tk_Button("Clear" , 10 , 3 , 425 , 300 , lambda: os.remove("expenses.txt"))

expenses = ttk.Treeview(columns=("Amount" , "Currency" , "Reason") , show="headings")
expenses.heading("Amount" , text="Amount")
expenses.heading("Currency" , text="Currency")
expenses.heading("Reason" , text="Reason")
expenses.place(x=50 , y=50)

sum_label = tk.Label(bg="white")
sum_label.place(x=51 , y=270)

def update():
    global currencies
    functions.load_expenses(expenses)
    functions.add_all_amounts(sum_label)

    window.after(1000 , update)

functions.get_convertion_rates_from_json()

update()

window.mainloop()
