import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import requests
import json
import datetime
import os

time = datetime.date.today()
full_date = datetime.datetime.now()

currencies = ["USD" , "EUR" , "GBP" , "PLN"]
convertion_rates = {}

def gen_config():
    with open("config.json" , "w") as file:
        default_config = {"user_currency": "USD" ,
                          "button_style": {
                              "bg": "#5b5b5b",
                              "fg": "#ffffff",
                              "activebg": "#727272",
                              "activefg": "black",
                              "corner_radius": 35
                          },
                          "window_style": {
                              "bg": "#3b3d3c"
                              }
        }
        json.dump(default_config , file)

def load_config():
    global config
    try:
        with open("config.json" , "r") as file:
            config = json.load(file)
    except FileNotFoundError:
        gen_config()
        load_config()
    except json.JSONDecodeError:
        gen_config()
        load_config()

load_config()

class Button:
    button_style = config["button_style"]
    def __init__(self, text: str , color=(button_style["bg"] , button_style["activebg"]) , corner_radius=button_style["corner_radius"] , size=(50 , 50) , pos=(0 , 0) , command=lambda: None , font=("arial" , 15 , "bold") , root=None):
        self.button = ctk.CTkButton(root , text=text , fg_color=color[0] , hover_color=color[1] , font=font , corner_radius=corner_radius, width=size[0] , height=size[1] , command=lambda: command())
        self.button.place(x=pos[0] , y=pos[1])

class Entry:
    button_style = config["button_style"]
    def __init__(self , textvariable , size=(30 , 10) , pos=(0 , 0) , width=10 , root=None):
        self.entry = ctk.CTkEntry(root , textvariable=textvariable , width=size[0] , height=size[1])
        self.entry.place(x=pos[0] , y=pos[1])

def get_convertion_rates():
    global convertion_rates
    for currency in currencies:
        response = requests.get(f"https://open.er-api.com/v6/latest/{currency}")
        convertion_rates[currency] = {
                            "USD": response.json()["rates"]["USD"],                                                                "EUR": response.json()["rates"]["EUR"],
                            "GBP": response.json()["rates"]["GBP"],
                            "PLN": response.json()["rates"]["PLN"] 
                        }
    convertion_rates["date"] = str(time)
    with open("convertion_rates.json" , "w") as file:
        json.dump(convertion_rates , file)
    print("done fetching!")

def fix_ConvRates_json():
    with open("convertion_rates.json" , "w") as file:
        pass
    get_convertion_rates()

def get_convertion_rates_from_json():
    global convertion_rates
    try:
        with open("convertion_rates.json" , "r") as file:
            test = json.load(file)
            if test["date"] == str(time):
                convertion_rates = test
            else:
                get_convertion_rates()
    except FileNotFoundError:
        fix_ConvRates_json()
    except json.JSONDecodeError:
        fix_ConvRates_json()

def fetch_usrinput(skip_input_validation: bool):
    global prompt_window , reason , currency , amount , date
    if skip_input_validation != True:
        reason = user_input_reason.get()
        currency = user_input_currency.get()
        try:
            amount = user_input_amount.get()
            if amount == 0:
                messagebox.showerror("Amount is not set." , "Amount of money spent must be bigger than 0!")
                return 0
        except tk.TclError:
            messagebox.showerror("Invalid Amount" , "Amount of money needs to be a number.")
            return 0
        if len(reason) > 100:
            messagebox.showerror("Reason too long." , "Reason over 100 letters long! Please make it shorter.")
            return 0
        if len(reason) == 0:
            messagebox.showerror("No reason specified." , "You must specify a reason!")
            return 0
        if currency == "Select A Currency":
            messagebox.showerror("Currency not set!" , "Please select a currency!")
            return 0
        try:
            with open("expenses.txt" , "a") as file:
                file.write(f"{amount} , {currency} , {reason} , {full_date}\n")
            prompt_window.destroy()
        except FileNotFoundError:
            fetch_usrinput(True)

def add_new():
    global user_input_amount , user_input_reason , user_input_currency , prompt_window , currencies , config
    prompt_window = tk.Toplevel()
    prompt_window.geometry("300x140")
    prompt_window.resizable(width=False , height=False)
    prompt_window.config(bg=config["window_style"]["bg"])
    
    user_input_amount = tk.DoubleVar()
    user_input_reason = tk.StringVar()
    user_input_currency = tk.StringVar()

    user_input_currency.set("Select A Currency")

    amount_of_money_spent = Entry(root=prompt_window , textvariable=user_input_amount , size=(40 , 5) , pos=(65 , 10))

    aoms_label = tk.Label(prompt_window , text="Amount" , bg="#3b3d3c" , fg="white")
    aoms_label.place(x=5 , y=10)

    currency = tk.OptionMenu(prompt_window , user_input_currency , *currencies)
    currency.config(bg="#ffffff" , bd=0 , highlightthickness=0)
    currency["menu"].config(bg="#ffffff" , fg="black" , activebackground="gray")
    currency.place(x=125 , y=10) 

    reason = Entry(root=prompt_window , size=(160 , 5) , pos=(65 , 50) , textvariable=user_input_reason)
    reason_label = tk.Label(prompt_window , text="Reason" , bg="#3b3d3c" , fg="white")
    reason_label.place(x=5 , y=50)

    submit_button = Button("Submit" , size=(100 , 50) , pos=(90 , 85) , root=prompt_window , command=lambda: fetch_usrinput(False))

def load_expenses(tree):
    try:
        for line in tree.get_children():
            tree.delete(line)
        with open("expenses.txt" , "r") as file:
            for line in file.readlines(): 
                line_contents = line.split(',')
                tree.insert("" , "end" , values=(line_contents[0], line_contents[1] , line_contents[2]))
    except FileNotFoundError:
        with open("expenses.txt" , "w") as file:
            pass

def add_all_amounts(label):
    global currency_rates , currencies , value , config
    user_currency = config["user_currency"]
    sum_of_amounts = 0
    with open("expenses.txt" , "r") as file:
        for line in file.readlines():
            line_contents = line.split(",")
            amount = float(line_contents[0])
            value = convertion_rates[line_contents[1].strip()][user_currency] * amount
            sum_of_amounts += value
    label.configure(text=f"Sum: {round(sum_of_amounts , 2)} {user_currency}")

def del_selected_expense():
    global expenses , selection , full_date
    expense_selected = selection.get().strip("()").split("," , 4)
    try:
        expenses.pop(int(expense_selected[0]) - 1)
    except ValueError:
        messagebox.showerror("No expense selected." , "Please select an expense before clicking proceed button!")
    with open("expenses.txt", "w") as file:
        for expense in expenses:
            file.write(f"{expense[1]} , {expense[2]} , {expense[3]} , {full_date}\n")
        del_prompt.destroy()
            

def del_expense():
    global config , expenses , selection , del_prompt
    del_prompt = tk.Toplevel()
    del_prompt.geometry("300x140")
    del_prompt.resizable(width=False , height=False)
    del_prompt.config(bg=config["window_style"]["bg"])
    
    expenses = []
    count = 1

    with open("expenses.txt" , "r") as file:
        for line in file.readlines():
            line_contents = line.strip().split("," , 3)
            expenses.append((count , line_contents[0].strip() , line_contents[1].strip() , line_contents[2].strip()))
            count += 1
    if len(expenses) < 1:
        del_prompt.destroy()
        messagebox.showerror("No expenses." , "Cant initialize deletion, reason: No expenses!")
        return 0
    
    selection = tk.StringVar()
    selection.set("Select")

    expense_selector = tk.OptionMenu(del_prompt , selection , *expenses)
    expense_selector.config(bd=0 , bg=config["button_style"]["bg"] , fg=config["button_style"]["fg"] , highlightthickness=0 , activebackground=config["button_style"]["activebg"] , activeforeground=config["button_style"]["activefg"])
    expense_selector["menu"].config(bg=config["button_style"]["bg"] , activebackground=config["button_style"]["activebg"] , fg=config["button_style"]["fg"] , activeforeground=config["button_style"]["activefg"])
    expense_selector.place(x=25 , y=25)

    delete_button = Button("Proceed" , size=(130 , 80) , pos=(150 , 40) , root=del_prompt , command=del_selected_expense)

def edit_selected(count , amount , currency , reason):
    own_count = 1
    expenses = []
    with open("expenses.txt" , "r") as file:
        for line in file.readlines():
            line_content = line.split("," , 4)
            if own_count == count:
                expenses.append(f"{amount} , {currency} , {reason}")
            else:
                expenses.append(f"{line_content[0].strip()} , {line_content[1].strip()} , {line_content[2].strip()}")
            own_count += 1
    os.remove("expenses.txt")
    with open("expenses.txt" , "a") as file:
        for expense in expenses:
            file.write(f"{expense}\n")


def reload_edit(count):
    try:
        count = int(count)
        edit_prompt.destroy()
        edit_expense(True , count)
    except ValueError:
         messagebox.showerror("Expense not selected." , "Please select an expense before clicking submit!")

def edit_expense(selection_set: bool , count: int):
    global edit_prompt , selection
    edit_prompt = tk.Toplevel()
    if selection_set == True:
        edit_prompt.geometry("300x140")
    if selection_set == False:
        edit_prompt.geometry("150x150")
    edit_prompt.resizable(width=False , height=False)
    edit_prompt.config(bg=config["window_style"]["bg"])
    
    button_style = config["button_style"]
    
    expenses = []

    with open("expenses.txt" , "r") as file:
        for line in file.readlines():
            line_contents = line.strip().split("," , 3)
            expenses.append((count , line_contents[0].strip() , line_contents[1].strip() , line_contents[2].strip()))
            count += 1
        if len(expenses) < 1:
            edit_prompt.destroy()
            messagebox.showerror("No expenses." , "Cant initialize editing mode, reason: No expenses!")
            return 0

    if selection_set != True:
        expenses = []

        selection_set = False
    
        selection = tk.StringVar()
        selection.set("Select Expense.")

        count = 1
        
        if count == 1:
            with open("expenses.txt" , "r") as file:
                for line in file.readlines():
                    line_contents = line.strip().split("," , 3)
                    expenses.append((count , line_contents[0].strip() , line_contents[1].strip() , line_contents[2].strip()))
                    count += 1
                if len(expenses) < 1:
                    edit_prompt.destroy()
                    messagebox.showerror("No expenses." , "Cant initialize editing mode, reason: No expenses!")
                    return 0 

        selector = tk.OptionMenu(edit_prompt , selection , *expenses)
        selector.config(bg=button_style["bg"] ,activebackground=button_style["activebg"], fg=button_style["fg"] , activeforeground=button_style["activefg"] , highlightthickness=0 , bd=0)
        selector["menu"].config(bg=button_style["bg"] ,activebackground=button_style["activebg"], fg=button_style["fg"] , activeforeground=button_style["activefg"] , bd=0)
        selector.place(x=7 , y=15)

        submit = Button("Submit" , size=(100 , 70) , pos=(13 , 60) , root=edit_prompt , command=lambda: reload_edit(selection.get()[1:-1].strip().split("," , 4)[0].strip().strip("'")))

    else:
        selection = selection.get()[1:-1].strip().split("," , 4)

        user_input_amount = tk.DoubleVar()
        user_input_reason = tk.StringVar()
        user_input_currency = tk.StringVar()

        user_input_amount.set(selection[1].strip().strip("'"))
        user_input_reason.set(selection[3].strip().strip("'"))
        user_input_currency.set(selection[2].strip().strip("'"))

        amount_of_money_spent = tk.Entry(edit_prompt , width=5 , textvariable=user_input_amount)
        amount_of_money_spent.place(x=65 , y=10)
        aoms_label = tk.Label(edit_prompt , text="Amount" , bg="#3b3d3c" , fg="white")
        aoms_label.place(x=5 , y=10)

        currency = tk.OptionMenu(edit_prompt , user_input_currency , *currencies)
        currency.config(bg="#ffffff" , bd=0 , highlightthickness=0)
        currency["menu"].config(bg="#ffffff" , fg="black" , activebackground="gray")
        currency.place(x=125 , y=10) 

        reason = tk.Entry(edit_prompt , width=20 , textvariable=user_input_reason)
        reason.place(x=65 , y=50)
        reason_label = tk.Label(edit_prompt , text="Reason" , bg="#3b3d3c" , fg="white")
        reason_label.place(x=5 , y=50)


        submit_button = Button(text="Submit" , size=(100 , 50) , pos=(90 , 85) ,root=edit_prompt, command=lambda: edit_selected(int(selection[0]) , user_input_amount.get() , user_input_currency.get() , user_input_reason.get()))

    
    
    

