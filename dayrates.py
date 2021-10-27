from connector import Connector
import tkinter as tk
from tkinter import ttk
import datetime

class App():
    global c
    c = Connector('dayrates.db')
    root = tk.Tk()
    root.title('Main')
    # Create a style
    style = ttk.Style(root)


    # Import the tcl file
    root.tk.call("source", "forest-dark.tcl")

    # Set the theme with the theme_use method
    style.theme_use("forest-dark")
    style.map('Treeview', background=[('selected','#217346')])
    style.configure('Treeview', font=('consolas',10))
    style.configure('Treeview.Heading', font=('consolas',10))
    style.configure('TButton', font=('consolas',10))
    style.configure('TLabel', font=('consolas',10))
    style.configure('TEntry', font=('consolas',10))
    style.configure('TLabelframe.Label', font=('consolas',10))
    style.configure('TNotebook.Tab', font=('consolas',10))
    root.option_add( "*font", "consolas 10")

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
    
    
    # # planter view page # #
    ps_page = ttk.Frame(dv_book)
    dv_book.add(ps_page, text="Planters")
    planter_data = c.get('planters')
    
    # tree frame
    ps_tree_frame = ttk.Frame(ps_page,height=100)
    ps_tree_frame.pack()
    # create scrollbar
    p_scroll = ttk.Scrollbar(ps_tree_frame)
    p_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    # create treeview
    global p_tree
    p_tree = ttk.Treeview(ps_tree_frame, yscrollcommand=p_scroll.set,selectmode='browse')
    p_tree.pack(pady=5)
    
    # scrollbar config
    p_scroll.config(command=p_tree.yview)
    
    # define columns
    p_tree['columns'] = ("fname", "lname", "ID")
    # format columns
    p_tree.column("#0", width=0, stretch=tk.NO)
    p_tree.column("fname", anchor=tk.W, width=100)
    p_tree.column("lname",anchor=tk.W, width=100)
    p_tree.column("ID", anchor=tk.CENTER, width=50)
    
    # create headings
    p_tree.heading("#0", text="", anchor=tk.W)
    p_tree.heading("fname", text="First Name", anchor=tk.W)
    p_tree.heading("lname", text="Last Name", anchor=tk.W)
    p_tree.heading("ID", text="ID", anchor=tk.CENTER)
    # striped row tags and colors 
    p_tree.tag_configure('even', background='#313131')
    p_tree.tag_configure('odd', background='#424242')

    global p_count
    p_count = 0    
    for record in planter_data:
        if p_count % 2:
            TAG = 'even'
        else:
            TAG = 'odd'
        p_tree.insert(parent='', index='end', iid=p_count, text='', values=(record[1],record[2],record[0]),tags=(TAG,))
        p_count += 1
    
    # Planter Data Entry and Labels
    p_data_frame = ttk.Frame(ps_page, width=300)
    p_data_frame.pack()
    
    p_fname_label = ttk.Label(p_data_frame, text='First Name',anchor=tk.W)
    p_fname_label.grid(row=0, column=0)
    p_lname_label = ttk.Label(p_data_frame, text='Last Name')
    p_lname_label.grid(row=1,column=0)
    p_id_label = ttk.Label(p_data_frame, text='ID')
    p_id_label.grid(row=2,column=0)
    
    global p_fname
    global p_lname
    global p_id
    p_fname = ttk.Entry(p_data_frame)
    p_lname = ttk.Entry(p_data_frame)
    p_id = ttk.Entry(p_data_frame, text=p_count+1)
    p_fname.grid(row=0,column=1,columnspan=3)
    p_lname.grid(row=1,column=1,columnspan=3)
    p_id.grid(row=2,column=1,columnspan=3,pady=(0,5))
    
    # edit and add buttons
    
    def edit_planter():
        oid = p_id.get()
        values = {'fname':p_fname.get(),
              'lname':p_lname.get()}
        c.update_on('planters',oid,values)
        selected = p_tree.focus()
        p_tree.item(selected, text='', values=(values['fname'],values['lname'],oid))

        
    def add_planter():
        global p_count
        fname = p_fname.get()
        lname = p_lname.get()
        c.add('planters', [fname, lname])
        if p_count % 2:
            TAG = 'even'
        else:
            TAG = 'odd'
        p_tree.insert(parent='', index='end', iid=p_count, text='', values=(fname,lname,p_count+1),tags=(TAG,))
        p_count += 1
    
    def remove_planter():
        oid = p_id.get()
        if (c.in_daily('pid', oid)): 
            return 
            # error message here 
            # 
            # 

        c.delete_on('planters', oid)
        p_tree.delete(p_tree.focus())

    p_edit_btn = ttk.Button(p_data_frame, text='Edit', command=edit_planter)
    p_add_btn = ttk.Button(p_data_frame, text='Add', command=add_planter)
    p_del_btn = ttk.Button(p_data_frame,text='Remove',command=remove_planter,style='Accent.TButton')

    p_edit_btn.grid(row=3, column=0,padx=5)
    p_add_btn.grid(row=3, column=1,padx=5)
    p_del_btn.grid(row=3,column=2,padx=5)

    # select planter button
    def select_planter(x):
        p_id.config(state='enabled')
        p_fname.delete(0,tk.END)
        p_lname.delete(0,tk.END)
        p_id.delete(0,tk.END)
        
        selected = p_tree.focus()
        values = p_tree.item(selected, 'values')  
        p_fname.insert(0,values[0])
        p_lname.insert(0,values[1])
        p_id.insert(0,values[2])
        p_id.config(state='disabled')
    
    p_tree.bind('<ButtonRelease-1>',select_planter)
    


    # seedlot view page
    sv_page = ttk.Frame(dv_book)
    dv_book.add(sv_page, text="Seedlots")
    # get seed data
    seed_data = c.get('seedlots')
    # tree frame
    sv_tree_frame = ttk.Frame(sv_page)
    sv_tree_frame.pack()
    # create scrollbar
    s_scroll = ttk.Scrollbar(sv_tree_frame)
    s_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    # create treeview
    global s_tree
    s_tree = ttk.Treeview(sv_tree_frame, yscrollcommand=s_scroll.set,selectmode='browse')
    s_tree.pack()
    
    # scrollbar config
    s_scroll.config(command=s_tree.yview)
    
    # define columns
    s_tree['columns'] = ("code", "spec", "price","box","bndl")
    # format columns
    s_tree.column("#0", width=0, stretch=tk.NO)
    s_tree.column("code", anchor=tk.W, width=50)
    s_tree.column("spec",anchor=tk.W, width=50)
    s_tree.column("price", anchor=tk.CENTER, width=50)
    s_tree.column("box", anchor=tk.CENTER, width=50)
    s_tree.column("bndl", anchor=tk.CENTER, width=50)
    # create headings
    s_tree.heading("#0", text="", anchor=tk.W)
    s_tree.heading("code", text="Code", anchor=tk.W)
    s_tree.heading("spec", text="Species", anchor=tk.W)
    s_tree.heading("price", text="Price", anchor=tk.CENTER)
    s_tree.heading("box", text="Box", anchor=tk.CENTER)
    s_tree.heading("bndl", text="Bndl", anchor=tk.CENTER)
    # striped row tags and colors 
    s_tree.tag_configure('even', background='#313131')
    s_tree.tag_configure('odd', background='#424242')
    
    global s_count
    s_count = 0    
    for record in seed_data:
        if s_count % 2:
            TAG = 'even'
        else:
            TAG = 'odd'
        s_tree.insert(parent='', index='end', iid=s_count, text='', values=(record[1],record[2],'$'+str(record[3]),record[4],record[5]),tags=(TAG,))
        s_count += 1

    # frame for labels/entries/buttons 
    s_data_frame = ttk.Frame(sv_page, width=300)
    s_data_frame.pack()
    # labels and entries for seedlot info 
    s_code_label = ttk.Label(s_data_frame, text='Code')
    s_spec_label = ttk.Label(s_data_frame, text='Species')
    s_price_label = ttk.Label(s_data_frame, text='Price')
    s_box_label = ttk.Label(s_data_frame, text='Box Size')
    s_bndl_label = ttk.Label(s_data_frame, text='Bndl Size')
    
    global s_code
    global s_spec
    global s_price
    global s_box
    global s_bndl

    s_code = ttk.Entry(s_data_frame,width=10)
    s_spec = ttk.Entry(s_data_frame,width=10)
    s_price = ttk.Entry(s_data_frame,width=10)
    s_box = ttk.Entry(s_data_frame,width=10)
    s_bndl = ttk.Entry(s_data_frame,width=10)

    s_code_label.grid(row=0,column=0)
    s_spec_label.grid(row=0,column=2)
    s_price_label.grid(row=2,column=0)
    s_box_label.grid(row=1,column=0)
    s_bndl_label.grid(row=1,column=2)

    s_code.grid(row=0,column=1,pady=5)
    s_spec.grid(row=0,column=3)
    s_price.grid(row=2,column=1,pady=5)
    s_box.grid(row=1,column=1)
    s_bndl.grid(row=1,column=3)

    def select_seedlot(x):
        s_code.delete(0,tk.END)
        s_spec.delete(0,tk.END)
        s_price.delete(0,tk.END)
        s_box.delete(0,tk.END)
        s_bndl.delete(0, tk.END)

        selected = s_tree.focus()
        values = s_tree.item(selected, 'values')

        s_code.insert(0,values[0])
        s_spec.insert(0,values[1])
        s_price.insert(0,values[2][1:])
        s_box.insert(0,values[3])
        s_bndl.insert(0,values[4])


    s_tree.bind('<ButtonRelease-1>',select_seedlot)
    

    # add, edit, remove seed buttons 
    def edit_seed(): 
        values = { 
        'code':s_code.get(),
        'species':s_spec.get(),
        'price':s_price.get(),
        'box_size':s_box.get(),
        'bndl_size':s_bndl.get()
        }

        if (values['box_size'] % values['bndl_size']): 
           return 
           # maybe make an error message here!!!
           # 
           # 
           # 

        oid = c.get_seed_oid(values['code'])
        c.update_on('seedlots', oid, values)
        selected = s_tree.focus()
        s_tree.item(selected, text='', values=(values['code'],values['species'],'$' + str(values['price']),values['box_size'],values['bndl_size']))

    def add_seed():
        global s_count 

        code = s_code.get()
        spec = s_spec.get() 
        price = s_price.get() 
        box = s_box.get() 
        bndl = s_bndl.get()
        if (c.seed_code_exists(code) or (box%bndl)):
            return
            # make an error message here!!! 
            # 
            # 
            # 

        c.add('seedlots', [code, spec, price, box, bndl])
        if s_count % 2:
            TAG = 'even'
        else:
            TAG = 'odd'
        s_tree.insert(parent='', index='end', iid=s_count, text='', values=(code, spec, '$' + price, box, bndl),tags=(TAG,))
        s_count += 1


    def remove_seed(): 
        code = s_code.get() 
        if c.in_daily('sid', code):
            return
            # error message
            # 
            #

        c.delete_on('seedlots', c.get_seed_oid(code))
        s_tree.delete(s_tree.focus())


    # seed button frame 
    s_btn_frame = ttk.Frame(sv_page)
    s_btn_frame.pack()

    s_edit_btn = ttk.Button(s_btn_frame, text='Edit', command=edit_seed)
    s_add_btn = ttk.Button(s_btn_frame, text='Add', command=add_seed)
    s_del_btn = ttk.Button(s_btn_frame,text='Remove',command=remove_seed,style='Accent.TButton')

    s_edit_btn.grid(row=0, column=0, padx=5)
    s_add_btn.grid(row=0, column=1, padx=5)
    s_del_btn.grid(row=0,column=2, padx=5) 

    # blocks view page
    blocks_page = ttk.Frame(dv_book)
    dv_book.add(blocks_page, text="Blocks")
    # get block data
    block_data = c.get('blocks')
    print(block_data)
    
    dv_book.pack(expand=True, fill='both', padx=5, pady=5)
    
    # grid the frames to root
    reports.grid(row=0, column=0,padx=5,pady=5)
    dataview.grid(row=0, column=1,padx=5,pady=5)
    endofday.grid(row=1, column=0, columnspan=2,padx=5,pady=(0,5))

    root.mainloop()
if __name__ == '__main__':
    App()
