from connector import Connector
import tkinter as tk
from tkinter import ttk, messagebox
import datetime

class App():
    global c
    c = Connector('dayrates.db')
    if c.new(): 
        # add some dummy stuff to the database 
        # FOR NOW 
        # 
        c.dummy()

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
    style.configure('TMenubutton', font=('consolas',10))
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
    r_book = ttk.Notebook(reports, height=400)
    # daily_page reports page
    daily_page = ttk.Frame(r_book)
    r_book.add(daily_page, text="Daily")

    # OptionMenu to select the day, defaulted to latest entry 
    global day
    day = tk.StringVar()
    global day_list
    day_list = c.day_list()
    if not day_list:
        day_list.append(datetime.datetime.now().strftime('%Y-%m-%d'))

    global day_tree_frame
    day_tree_frame = ttk.Frame(daily_page)
    day_tree_frame.pack(fill=tk.X)
    global day_scroll
    day_scroll = ttk.Scrollbar(day_tree_frame)
    day_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    global day_tree
    day_tree = ttk.Treeview(day_tree_frame,yscrollcommand=day_scroll.set,selectmode='browse')

    def reset_day(): 
        global day_tree
        global day_list
        selected = day.get()
        response = messagebox.askyesno("Confirmation", f"Are you sure you wish to delete all data for {selected}?")
        if response: 
            c.delete_on('daily', selected, keyword='jour')
            day_tree.destroy() 
            day_list = c.day_list()
            print(day_list)
            day_list.remove(day)
        else: 
            return

    def generate_daily():
        global day
        global day_select 
        # grab the data 
        daily_data = c.daily_report(day.get())
        # display in a treeview with scroller
        global day_tree
        day_tree.destroy()
        day_tree_frame.update() 
        
        day_tree = ttk.Treeview(day_tree_frame,yscrollcommand=day_scroll.set,selectmode='browse')
        day_tree.pack(pady=5)

        # scrollbar config
        day_scroll.config(command=day_tree.yview)
        
        # define columns
        day_tree['columns'] = daily_data[0][0]
        # "Planter, Seed1, Seed2, ... TOTAL, gross"

        # format columns
        day_tree.column("#0", width=0, stretch=tk.NO)
        day_tree.column('Planter', width=100, anchor=tk.W)
        for column in daily_data[0][0][1:]:
            day_tree.column(column, width=60, anchor=tk.W)
        
        # create headings
        day_tree.heading("#0", text="", anchor=tk.W)
        day_tree.heading('Planter', text='Planter', anchor=tk.W)
        for heading in daily_data[0][0][1:]:
            day_tree.heading(heading, text=heading, anchor=tk.W)
        # striped row tags and colors 
        day_tree.tag_configure('even', background='#313131')
        day_tree.tag_configure('odd', background='#424242')

        daily_rows = daily_data[0][1:]
        # all the records for the day, minus the header row

        row_count = 0 
        for row in daily_rows:
            row[-1] = f'${row[-1]}'
            if row_count%2: 
                TAG = 'even'
            else: 
                TAG = 'odd'
            day_tree.insert(parent='', index='end', iid=row_count, text='', values=(row),tags=(TAG,))
            row_count+=1
        # add the remaining data, (crew_total, commission) to the button frame beneath the tree
        global day_label_frame
        for widgets in day_label_frame.winfo_children():
            widgets.destroy()
        
        day_crew_label = ttk.Label(day_label_frame, text=f'Crew Total: {daily_data[-1][0]}')
        day_cmsn_label = ttk.Label(day_label_frame, text=f'Commission: ${daily_data[-1][1]}')
        day_crew_label.grid(row=1, column=0, padx=10, pady=10)
        day_cmsn_label.grid(row=1, column=1, padx=10)
        day_label_frame.update()


    # daily report button frame
    global day_btn_frame
    day_btn_frame = ttk.Frame(daily_page)
    day_btn_frame.pack()

    global day_label_frame
    day_label_frame =ttk.Frame(daily_page)
    day_label_frame.pack()
    global day_select
    day_select = ttk.OptionMenu(day_btn_frame, day, day_list[0], *day_list)
    day_select.grid(row=0, column=0,padx=10)
    gen_day_btn = ttk.Button(day_btn_frame, text='Generate Report', command=generate_daily, style='Accent.TButton')
    gen_day_btn.grid(row=0, column=1, padx=10,pady=10)
    del_day_btn = ttk.Button(day_btn_frame, text='Reset Selected Day',command=reset_day, style='Accent.TButton')
    del_day_btn.grid(row=0, column=2, pady=10, padx=10)

    # planter reports page
    pr_page = ttk.Frame(r_book)
    r_book.add(pr_page, text="Planter")
    global pr_tree_frame 
    pr_tree_frame = ttk.Frame(pr_page)
    pr_tree_frame.pack()
    global pr_scroll
    pr_scroll = ttk.Scrollbar(pr_tree_frame)
    pr_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    # build tree
    global pr_tree
    pr_tree = ttk.Treeview(pr_tree_frame,yscrollcommand=pr_scroll.set,selectmode='browse')
    pr_tree.pack()
    # variables for OptionMenu to select the planter
    global planter
    planter = tk.StringVar()
    planter_list = c.planter_list()


    # tree to display the data
    def generate_planter():
        global planter
        global pr_tree
        global pr_tree_frame
        # gather data and assign to variables 
        pid = planter.get().split()[0]
        try:
            planter_data = c.planter_report(pid)
        except: 
            pr_tree.destroy() 
            pr_tree_frame.update()
            response = messagebox.showerror('Error', 'Planter not associated with any data yet!') 
            return
        rows = planter_data[0]
        total, gross = planter_data[1]
        avg,pb,stdev = planter_data[2]

        # reset the tree
        pr_tree.destroy()
        pr_tree_frame.update()
        pr_tree = ttk.Treeview(pr_tree_frame,yscrollcommand=pr_scroll.set,selectmode='browse')
        pr_tree.pack()
        # define columns 
        pr_tree['columns'] = ('Date','Planted','Earned')
        pr_tree.column("#0", width=0, stretch=tk.NO)
        pr_tree.column("Date", anchor=tk.W, width=100)
        pr_tree.column("Planted",anchor=tk.CENTER, width=100)
        pr_tree.column("Earned", anchor=tk.CENTER, width=100)
        # define headings 
        pr_tree.heading("#0", text="", anchor=tk.W)
        pr_tree.heading("Date", text="Date", anchor=tk.W)
        pr_tree.heading("Planted", text="Planted", anchor=tk.CENTER)
        pr_tree.heading("Earned", text="Earned", anchor=tk.CENTER)
        pr_tree.tag_configure('even', background='#313131')
        pr_tree.tag_configure('odd', background='#424242')
        # insert each row 
        x = 0
        for row in rows:
            if x%2: 
                TAG = 'even'
            else: 
                TAG = 'odd'
            pr_tree.insert(parent='', index='end', iid=row, text='', values=(row),tags=(TAG,) )
            x+=1
        pr_tree_frame.update()
        
        # reset the label frame
        global pr_label_frame 
        for widgets in pr_label_frame.winfo_children():
            widgets.destroy()
        # display total gross, avg, pb, stdev in pr_btn_frame
        total_label = ttk.Label(pr_label_frame, text = f'Total Planted: {total}')
        gross_label = ttk.Label(pr_label_frame, text=f'Total Grossed: ${gross}')
        avg_label = ttk.Label(pr_label_frame, text=f'Average Planted: {avg}')
        pb_label = ttk.Label(pr_label_frame, text=f'Personal Best: {pb}')
        stdev_label = ttk.Label(pr_label_frame, text=f'STDEV: {stdev}')
        total_label.grid(row=1,column=0,padx=10)
        gross_label.grid(row=1,column=1,pady=10)
        avg_label.grid(row=2,column=0,padx=10)
        pb_label.grid(row=2,column=1)
        stdev_label.grid(row=3,column=0,pady=10)

        pr_label_frame.update()


    # button to generate report, labels to display misc data
    global pr_btn_frame 
    pr_btn_frame = ttk.Frame(pr_page)
    pr_btn_frame.pack()

    global pr_label_frame
    pr_label_frame=ttk.Frame(pr_page)
    pr_label_frame.pack()


    planter_select = ttk.OptionMenu(pr_btn_frame, planter, planter_list[0], *planter_list)
    gen_planter_btn = ttk.Button(pr_btn_frame, text='Generate Report', command=generate_planter, style='Accent.TButton')
    planter_select.grid(row=0, column=0, padx=10, pady=10)
    gen_planter_btn.grid(row=0, column=1, padx=10)


    #stats report page
    stats_page = ttk.Frame(r_book)
    r_book.add(stats_page, text="Stats")
    global stats_tree
    global stats_tree_frame
    stats_tree_frame = ttk.Frame(stats_page)
    stats_tree_frame.pack()
    global stats_scroll
    stats_scroll = ttk.Scrollbar(stats_tree_frame)
    stats_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    # build tree
    global stats_tree
    stats_tree = ttk.Treeview(stats_tree_frame,yscrollcommand=stats_scroll.set,selectmode='browse')
    stats_tree.pack()
    
    def generate_stats():
        global stats_tree
        global stats_tree_frame
        global stats_btn_frame
        # gather data  
        
        stats_data = c.stats_report()
        rows = stats_data

        # reset the tree
        stats_tree.destroy()
        stats_tree_frame.update()
        stats_tree = ttk.Treeview(stats_tree_frame,yscrollcommand=stats_scroll.set,selectmode='browse')
        stats_tree.pack()
        # define columns 
        stats_tree['columns'] = ('planter', 'total', 'avg', 'pb', 'stdev')
        stats_tree.column("#0", width=0, stretch=tk.NO)
        stats_tree.column("planter", anchor=tk.W, width=100)
        stats_tree.column("total",anchor=tk.CENTER, width=100)
        stats_tree.column("avg", anchor=tk.CENTER, width=100)
        stats_tree.column("pb", anchor=tk.CENTER, width=100)
        stats_tree.column("stdev", anchor=tk.CENTER, width=100)
        # define headings 
        stats_tree.heading("#0", text="", anchor=tk.W)
        stats_tree.heading("planter", text="Planter", anchor=tk.W)
        stats_tree.heading("total", text="Total", anchor=tk.CENTER)
        stats_tree.heading("avg", text="Average", anchor=tk.CENTER)
        stats_tree.heading("pb", text="P. B.", anchor=tk.CENTER)
        stats_tree.heading("stdev", text="STDEV", anchor=tk.CENTER)
        stats_tree.tag_configure('even', background='#313131')
        stats_tree.tag_configure('odd', background='#424242')
        # insert each row 
        x = 0
        for row in rows:
            if x%2: 
                TAG = 'even'
            else: 
                TAG = 'odd'
            stats_tree.insert(parent='', index='end', iid=[x]+row, text='', values=(row),tags=(TAG,) )
            x+=1
        stats_tree_frame.update()
    stats_btn_frame = ttk.Frame(stats_page) 
    stats_btn_frame.pack()

    # buttons and labels 
    stats_report_btn = ttk.Button(stats_btn_frame, text='Generate Report', command=generate_stats, style='Accent.TButton')
    stats_report_btn.pack()


    #foreman report page
    f_page = ttk.Frame(r_book)
    r_book.add(f_page, text="Foreman")

    global f_tree_frame 
    f_tree_frame = ttk.Frame(f_page)
    f_tree_frame.pack()
    global f_scroll
    f_scroll = ttk.Scrollbar(f_tree_frame)
    f_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    # build tree
    global f_tree
    f_tree = ttk.Treeview(f_tree_frame,yscrollcommand=f_scroll.set,selectmode='browse')
    f_tree.pack()
    def generate_foreman():
        global f_tree
        global f_tree_frame
        global f_btn_frame
        # gather data and assign to variables 
        
        foreman_data = c.foreman_report()
        rows = foreman_data[0]
        total, crew_total, cmsn_total, gross_total = foreman_data[1]

        # reset the tree
        f_tree.destroy()
        f_tree_frame.update()
        f_tree = ttk.Treeview(f_tree_frame,yscrollcommand=f_scroll.set,selectmode='browse')
        f_tree.pack()
        # define columns 
        f_tree['columns'] = ('Date', 'Planted', 'Crew', 'Gross') # Date Planted Crew Planted Gross
        f_tree.column("#0", width=0, stretch=tk.NO)
        f_tree.column("Date", anchor=tk.W, width=100)
        f_tree.column("Planted",anchor=tk.CENTER, width=100)
        f_tree.column("Crew", anchor=tk.CENTER, width=100)
        f_tree.column("Gross", anchor=tk.CENTER, width=100)
        # define headings 
        f_tree.heading("#0", text="", anchor=tk.W)
        f_tree.heading("Date", text="Date", anchor=tk.W)
        f_tree.heading("Planted", text="Planted", anchor=tk.CENTER)
        f_tree.heading("Crew", text="Crew Planted", anchor=tk.CENTER)
        f_tree.heading("Gross", text="Gross", anchor=tk.CENTER)

        f_tree.tag_configure('even', background='#313131')
        f_tree.tag_configure('odd', background='#424242')
        # insert each row 
        x = 0
        for row in rows[1:]:
            row[-1] = f'${row[-1]}'
            if x%2: 
                TAG = 'even'
            else: 
                TAG = 'odd'
            f_tree.insert(parent='', index='end', iid=row, text='', values=(row),tags=(TAG,) )
            x+=1
        f_tree_frame.update()
        # labels for misc data 
        total_label = ttk.Label(f_btn_frame, text=f'Total Planted: {total}')
        crew_label = ttk.Label(f_btn_frame, text=f'Crew Total: {crew_total}')
        cmsn_label = ttk.Label(f_btn_frame, text=f'Commission: ${cmsn_total}')
        gross_label = ttk.Label(f_btn_frame, text=f'Gross: ${gross_total}')
        total_label.grid(row=1,column=0,padx=5)
        crew_label.grid(row=1,column=1,padx=5, pady=10)
        cmsn_label.grid(row=2,column=0,padx=5)
        gross_label.grid(row=2,column=1,padx=5)

    # frame to hold button and labels 
    global f_btn_frame
    f_btn_frame = ttk.Frame(f_page)
    f_btn_frame.pack()
    # button to generate reports 
    foreman_report_btn = ttk.Button(f_btn_frame, text="Generate Report", command=generate_foreman, style='Accent.TButton')
    foreman_report_btn.grid(row=0,column=0, columnspan=2, pady=(10,0))

    r_book.pack(expand=True, fill="both", padx=5, pady=5)
    
    dv_book = ttk.Notebook(dataview)

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
    p_data_frame = ttk.Frame(ps_page)
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
    p_id.config(state='disabled')
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
            response = messagebox.showerror("Error", "Cannot remove planter: associated with daily entries")
            return 

        c.delete_on('planters', oid, keyword='oid')
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
    s_box_label = ttk.Label(s_data_frame, text='Box Size')
    s_bndl_label = ttk.Label(s_data_frame, text='Bndl Size')
    s_price_label = ttk.Label(s_data_frame, text='Price')
    
    global s_code
    global s_spec
    global s_price
    global s_box
    global s_bndl
    global seed_code
    seed_code = ''
    s_code = ttk.Entry(s_data_frame,width=10)
    s_spec = ttk.Entry(s_data_frame,width=10)
    s_box = ttk.Entry(s_data_frame,width=10)
    s_bndl = ttk.Entry(s_data_frame,width=10)
    s_price = ttk.Entry(s_data_frame,width=10)

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
        global seed_code
        seed_code = s_code.get()

        s_code.delete(0,tk.END)
        s_spec.delete(0,tk.END)
        s_price.delete(0,tk.END)
        s_box.delete(0,tk.END)
        s_bndl.delete(0, tk.END)

        selected = s_tree.focus()
        values = s_tree.item(selected, 'values')

        s_code.insert(0,values[0])
        seed_code = s_code.get()

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
        'price':float(s_price.get()),
        'box_size':int(s_box.get()),
        'bndl_size':int(s_bndl.get())
        }
        if values['code'] != seed_code: 
            response = messagebox.askyesno("Warning!", "Seed code has been changed! If this code is already being used, data could be corrupted. Do you want to continue?")
            if not response: 
                return

        if (values['box_size'] % values['bndl_size']): 
           return 
           response = messagebox.showerror("Error", "Box size must be a multiple of bundle size!")

        
        c.update_on('seedlots', seed_code, values, keyword='code')
        selected = s_tree.focus()
        s_tree.item(selected, text='', values=(values['code'],values['species'],'$' + str(values['price']),values['box_size'],values['bndl_size']))

    def add_seed():
        global s_count 

        code = s_code.get()
        spec = s_spec.get() 
        price = float(s_price.get()) 
        box = int(s_box.get()) 
        bndl = int(s_bndl.get())

        if (c.seed_code_exists(code)):
            response = messagebox.showerror("Error", "Seed code already exists!")
            return
        if not (box%bndl): 
            response = messagebox.showerror("Error", "Box size must be a multiple of Bundle size!")
             

        c.add('seedlots', [code, spec, price, box, bndl])
        if s_count % 2:
            TAG = 'even'
        else:
            TAG = 'odd'
        s_tree.insert(parent='', index='end', iid=s_count, text='', values=(code, spec, '$' + str(price), box, bndl),tags=(TAG,))
        s_count += 1


    def remove_seed(): 
        code = s_code.get() 
        if c.in_daily('sid', code):
            response = messagebox.showerror("Error", "Cannot remove seed: associated with daily entries!")
            return
            

        c.delete_on('seedlots', code)
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
    block_data = c.get_blocks()

    block_tree_frame = ttk.Frame(blocks_page)
    block_tree_frame.pack()
    # create scrollbar
    block_scroll = ttk.Scrollbar(block_tree_frame)
    block_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    # create treeview
    global block_tree
    block_tree = ttk.Treeview(block_tree_frame, yscrollcommand=block_scroll.set,selectmode='browse')
    block_tree.pack()
    block_tree['columns']= (1)

    block_tree.column("#0", width=10, stretch=tk.NO)
    block_tree.column(1, anchor=tk.W)
   
    
    # scrollbar config
    block_scroll.config(command=s_tree.yview)

    block_tree.tag_configure('even', background='#313131')
    block_tree.tag_configure('odd', background='#424242')
    block_tree.tag_configure('pe', background='#015326')
    block_tree.tag_configure('po', background='#216336')
    global bs_count
    global bb_count
    bb_count = 0
    bs_count = 0

    for block, seeds in block_data.items(): 
        bs_count=0
        if bb_count%2: 
            TAG='pe'
        else:
            TAG='po'
        block_tree.insert(parent='', index='end', iid=block, text='', values=(block,),tags=(TAG,))
        
        for seed in seeds: 
            if bs_count%2: 
                TAG='even'
            else:
                TAG='odd'
            block_tree.insert(parent=block, index='end', iid=str(block) + '.'+ str(seed), text='', values=(seed,),tags=(TAG,))
            bs_count += 1
        bb_count+=1



    
    # Frame for block labels and entries 
    block_label_frame = ttk.Frame(blocks_page)
    block_label_frame.pack()

    block_label = ttk.Label(block_label_frame, text='Block')
    bs_label = ttk.Label(block_label_frame, text='Seedlot')

    global block_entry
    global bs_entry
    block_entry = ttk.Entry(block_label_frame) 
    bs_entry = ttk.Entry(block_label_frame) 

    block_label.grid(row=0, column=0) 
    bs_label.grid(row=1, column=0)
    block_entry.grid(row=0, column=1,pady=5) 
    bs_entry.grid(row=1, column=1)
    
    def select_block(x):
        block_entry.delete(0, tk.END)
        bs_entry.delete(0,tk.END)

        selected = block_tree.focus()
        parent = block_tree.parent(selected)
        values = ['','']
        if parent: # has parent
            values[0] = block_tree.item(selected, 'values')[0]
            values[1] = block_tree.item(parent, 'values')[0]
            bs_entry.insert(0, values[0])
        else: 
            values[1] = block_tree.item(selected, 'values')
        block_entry.insert(0, values[1])
        

    block_tree.bind('<ButtonRelease-1>',select_block)

    # frame for block add, edit, remove buttons
    block_btn_frame = ttk.Frame(blocks_page)
    block_btn_frame.pack() 

    # block add edit remove buttons
    def add_block():
        global bs_count
        global bb_count

        block, seed = (block_entry.get(), bs_entry.get())
        if not block: 
            response = messagebox.showerror("Error", "No block code given, cannot commit to database")
            return
        # add parent BLOCK if not already present
        if not block_tree.exists(block): 
            fix = 'e'*(bb_count%2) + 'o'*(not bb_count%2)
            TAG = f"p{fix}"
            block_tree.insert(parent='', index='end', iid=block, text='', values=(block,),tags=(TAG,))

        if seed: # there is a selected seed
            if not c.seed_code_exists(seed): 
                response = messagebox.showwarning("Warning", "Invalid seed code!")
                return

            if block in c.get_blocks():
                if seed in c.get_blocks()[block]: 
                    response = messagebox.showwarning("Warning", "Selected block already contains selected seed")
                    return

            # add entry to database
            c.add('blocks', [block, seed])
            # add child SEED  
            if bs_count%2: 
                TAG = 'even'
            else: 
                TAG = 'odd'
            block_tree.insert(parent=block, index='end', iid=str(block)+'.'+str(seed), text='', values=(seed,),tags=(TAG,))
            bs_count += 1

    def rem_block(): 
        block, seed = (block_entry.get(), bs_entry.get())
        if not seed: 
            c.delete_on('blocks',block)

            # remove parent BLOCK and all children SEEDS 
            block_tree.delete(block)
        else: 
            c.remove_seed_from_block(block, seed)
            # remove just child SEED 
            block_tree.delete(str(block)+'.'+str(seed))
        

    block_add_btn = ttk.Button(block_btn_frame, text='Add', command=add_block)
    block_rem_btn = ttk.Button(block_btn_frame, text='Remove', command=rem_block,style='Accent.TButton') 

    block_add_btn.grid(row=0,column=0,padx=5, pady=10)
    block_rem_btn.grid(row=0,column=2,padx=5)
    
    # end of day Frame 
    global eod_proper
    eod_proper = ttk.Frame(endofday) 
    eod_proper.pack() 
    def eod(): 
        global eod_proper
        global block_select
        global day_entry
        global block_menu
        for widgets in eod_proper.winfo_children():
            widgets.destroy()
        eod_proper.update()
        # make block_select, day_entry DISABLED
        block_menu.config(state='disabled')
        day_entry.config(state='disabled')
        # ensure valid date entered 
        try: 
            datetime.datetime.strptime(day_entry.get(), '%Y-%m-%d')
        except: 
            day_entry.delete(0,tk.END)
            day_entry.insert(0,'MUST BE YYYY-MM-DD')
            return
        # empty list to fill with (pid, sid, N*<ttk.Entry>)
        entries = []
        # empty list to hold running totals for each planter, to be updated with the update_total() function by the spinboxes
        
        # build planter list                

        planters = c.get('planters') # (oid, fname, lname)
        # build seed list
        seeds = c.get_blocks()[block_select.get()]
        # create HEADER 
        header = ["Planter"]
        for seed in seeds: 
            header += [seed, "Boxes", "Bundles"]
        header += ['Total']
        # build end of day
        j = 0 
        i = 0 
        for heading in header: 
            h = ttk.Label(eod_proper, text=heading) 
            h.grid(row=j, column=i,padx=5,pady=10)
            i+=1
        j += 1

        def update(label, row): 
            t = 0
            total = label
            for entry in entries: 
                if entry[0] == row: 
                    # add to running total
                    seed_data = c.get_on('seedlots', entry[1], 'code')[-2:]
                    t += int(entry[2].get()) * seed_data[0] + int(entry[3].get()) * seed_data[1]
            total.delete(0,tk.END)
            total.insert(0, t)


        for planter in planters:
            p = ttk.Label(eod_proper, text=planter[1])
            p.grid(row=j, column=0,pady=(0,10))
            total = ttk.Entry(eod_proper, justify=tk.RIGHT,width=15) 
            total.insert(0,0)
            i=1
            for seed in seeds:
                s = ttk.Label(eod_proper, text=seed)
                s.grid(row=j, column=i, padx=5,pady=(0,10))
                box_size, bndl_size = c.get_on('seedlots', seed, keyword='code')[-2:]
                box = ttk.Spinbox(eod_proper, width=10, from_=0, to=50, command=lambda x=total, y=planter[0] : update(x,y))
                bndl = ttk.Spinbox(eod_proper, width=10, from_=-50, to=50, command=lambda x=total, y=planter[0] : update(x,y))
                box.set(0)
                bndl.set(0)
                box.grid(row=j, column=i+1,padx=5,pady=(0,10))
                bndl.grid(row=j, column=i+2,padx=5,pady=(0,10))
                # add the "temporary" entries to the list 
                entries.append([planter[0], seed, box, bndl, total])
                i+=3
            total.grid(row=j, column=i,padx=5,pady=(0,10))
            j+=1

        # submit button
        def submit_eod():
            # destroy eod_proper

            global day_list
            global day_select
            global day_btn_frame 
            response = messagebox.askyesno("Confirmation", "Do you want to commit this data?")
            if response == 0:
                return
            else:
                
                global block_menu
                global day_entry
                block_menu.config(state='enabled')
                day_entry.config(state='enabled')

                day_list.append(day_entry.get())
                day_list.sort(reverse=True)
                day_select.destroy()
                day_select = ttk.OptionMenu(day_btn_frame, day, day_list[0], *day_list)
                day_select.grid(row=0, column=0,padx=10)

                for entry in entries: 
                    data = [day_entry.get(), entry[0], entry[1], int(entry[2].get()), int(entry[3].get())]
                    c.add('daily', data)
                for widget in eod_proper.winfo_children():
                    widget.destroy() 
                eod_proper.update() 

        submit_eod_btn = ttk.Button(eod_proper, text='Submit', command=submit_eod, style='Accent.TButton')
        submit_eod_btn.grid(row=j, column=0, columnspan=100)

    # frame = endofday
    eod_btn_frame = ttk.Frame(endofday)
    eod_btn_frame.pack()
    # build list of blocks and create a drop down 
    block_list = [ b for b in c.get_blocks().keys()]
    global block_select
    block_select = tk.StringVar()
    # build day entry widget 
    global day_entry 
    day_entry = ttk.Entry(eod_btn_frame)
    day_entry.insert(0,datetime.datetime.now().strftime('%Y-%m-%d'))
    day_entry.grid(row=0, column=1, padx=10, pady=10)
    global block_menu   
    block_menu = ttk.OptionMenu(eod_btn_frame, block_select, block_list[0], *block_list)
    block_menu.grid(row=0, column=0, padx=10)
    start_eod_btn = ttk.Button(eod_btn_frame, text='Start EOD', command= eod, style='Accent.TButton')
    start_eod_btn.grid(row=0, column=2,padx=10)
    # grid the frames to root 
    reports.grid(row=0, column=0,padx=5,pady=5)
    dataview.grid(row=0, column=1,padx=5,pady=5)
    endofday.grid(row=1, column=0, columnspan=2,padx=5,pady=(0,5))
    

    dv_book.pack(expand=True, fill='both', padx=5, pady=5)
    root.mainloop()
    
if __name__ == '__main__':
    App()