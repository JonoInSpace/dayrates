# spinboxes.py

import tkinter as tk 
from tkinter import ttk 

root = tk.Tk()
j = 0

rows = ['test', 'test2']
columns = ['1','2']
global functions
functions = {}


for row in rows:
    label = tk.Label(root, text=row)
    label.grid(row=j, column=0)
    i=1
    running_total = tk.Entry(root)
    running_total.insert(0,0)

    for col in columns: 
        label = tk.Label(root, text=col)
        label.grid(row=j, column=i)
        
        def update(inc, label	):
        	total = label
        	current = int(total.get())
        	total.delete(0, tk.END) 
        	total.insert(0, current + inc)


        spinbox_1 = tk.Spinbox(root, from_=0, to=50,command= lambda x=1,y=running_total : update(x,y)) # multiples of 1

        spinbox_2 = tk.Spinbox(root, from_=0, to=50,command= lambda x=5,y=running_total: update(x,y)) # multiples of 5
        spinbox_1.grid(row=j, column=i+1)
        spinbox_2.grid(row=j, column=i+2)
        i+=3

    running_total.grid(row=j,column=i)
    j+=1

print(functions)
root.mainloop()