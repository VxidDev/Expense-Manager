import tkinter as tk
from tkinter import ttk
import functions
import os

window = tk.Tk()
window.geometry("700x450")
window.resizable(width=False , height=False)

window.config(bg="#3b3d3c")

currencies = ["USD" , "EUR" , "GBP", "PLN"]
list_of_expenses = []

# GUI
new_button = functions.Button("Add New" , size=(140 , 100) , pos=(10 , 320), command=functions.add_new)

del_button = functions.Button("Delete" , size=(140 , 100) , pos=(180 , 320) , command=functions.del_expense)

edit_button = functions.Button("Edit" , size=(140 , 100) , pos=(360 , 320) , command=lambda: functions.edit_expense(False , 1))

clear_button = functions.Button("Clear" , size=(140 , 100) , pos=(540 , 320) , command=lambda: os.remove("expenses.txt"))

expenses = ttk.Treeview(columns=("Amount" , "Currency" , "Reason") , show="headings")
expenses.heading("Amount" , text="Amount")
expenses.heading("Currency" , text="Currency")
expenses.heading("Reason" , text="Reason")
expenses.place(x=50 , y=50)

style = ttk.Style(window)
style.configure("Treeview" , font=("arial" , 13 , "bold"))
style.configure("Treeview.Heading" , bd=0 , highlightthickness=0)
expenses.config(style="Treeview")


fake_extension = tk.Label(bg="white" , text=(" " * 199))
fake_extension.place(x=51 , y=270)

sum_label = tk.Label(bg="white")
sum_label.place(x=51 , y=270)

def update(): 
    functions.load_expenses(expenses)
    functions.add_all_amounts(sum_label)

    window.after(500 , update)

functions.get_convertion_rates_from_json()

update()

window.mainloop()
