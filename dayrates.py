from connector import Connector
import tkinter as tk
from tkinter import ttk
import datetime

class App():
    c = Connector('dayrates.db')
    root = tk.Tk()
    root.title('Main')
    # Create a style
    style = ttk.Style(root)

    # Import the tcl file
    root.tk.call("source", "forest-dark.tcl")

    # Set the theme with the theme_use method
    style.theme_use("forest-dark")

    # Create Frame for Reports
    reports = ttk.LabelFrame(root,text='Reports',height=400, width=300, borderwidth=1,relief=tk.SUNKEN,padding=5)
    # Create Frame for Veiwing Data
    dataview = ttk.LabelFrame(root,text='Data', height=400, width=300, borderwidth=1,relief=tk.SUNKEN,padding=5)
    # Create Frame for End of Day 
    endofday = ttk.LabelFrame(root,text='End of Day',height=200, width=700, borderwidth=1,relief=tk.SUNKEN,padding=5)
    
    # reports Frame
    r_book = ttk.Notebook(reports, height=400, width=300)
    # daily_page reports page
    daily_page = ttk.Frame(r_book)
    r_book.add(daily_page, text="Daily")

    # planter reports page
    pr_page = ttk.Frame(r_book)
    r_book.add(pr_page, text="Planter")

    #stats report page
    stats_page = ttk.Frame(r_book)
    r_book.add(stats_page, text="Stats")
    #foreman report page
    f_page = ttk.Frame(r_book)
    r_book.add(f_page, text="Foreman")

    r_book.pack(expand=True, fill="both", padx=5, pady=5)
    
    # data viewing Frame
    dv_book = ttk.Notebook(dataview, height=400, width=300)
    
    
    # planter view page
    pv_page = ttk.Frame(dv_book)
    dv_book.add(pv_page, text="Planters")
    planter_data = c.get('planters')
    print(planter_data)
    planter_label = ttk.Label(pv_page, text=planter_data)
    planter_label.pack()
    
    
    
    # seedlot view page
    sv_page = ttk.Frame(dv_book)
    dv_book.add(sv_page, text="Seedlots")
    # blocks view page
    blocks_page = ttk.Frame(dv_book)
    dv_book.add(blocks_page, text="Blocks")
    
    dv_book.pack(expand=True, fill='both', padx=5, pady=5)
    
    # grid the frames to root
    reports.grid(row=0, column=0,padx=5,pady=5)
    dataview.grid(row=0, column=1,padx=5,pady=5)
    endofday.grid(row=1, column=0, columnspan=2,padx=5,pady=(0,5))
if __name__ == '__main__':
    App()
