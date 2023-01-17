import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class RestaurantConfiguration:
    def __init__(self, tables, seats):
        """Arguments: tables is the number of tables, seats is the number of seats per table"""
        self.tables = tables
        self.seats = seats
        self.data = {}

    def dic(self):
        """This method combines the tables with their corresponding number of seats"""
        for i in range(1, self.tables + 1):
            self.data[i] = self.data.get(i, self.seats[i - 1])


class MenuConfiguration:
    def __init__(self):
        self.menu = {}

    def menu_config(self):
        """This method take an item and price
        :return dictionary has items with prices"""
        price = 0
        while True:
            try:
                name = input("Please input item name: ")
                if name == "":
                    break
                price = input("Please input the price item: ")
                if price == "":
                    break
                price = float(price)
                self.menu[name] = self.menu.get(name, price)
            except ValueError:
                print(F"{price} is not a price")
        return self.menu


class Waiters:
    def __init__(self, number):
        """"""
        self.number = number
        self.waiters = {}

    def creating_waiters(self):
        for i in range(1, self.number + 1):
            self.waiters[i] = self.waiters.get(i, F"waiter {i}")
        return self.waiters


def input_data():
    """Input from the user"""
    table = int(input("Insert the number of tables: "))
    seats = [0] * table
    for i in range(table):
        seats[i] = int(input(F"Insert the number of seats in table {i + 1}: "))
    res = RestaurantConfiguration(table, seats)
    res.dic()
    # print(F"Number of tables is {res.tables}. Number of seats are as follows {res.seats}")
    print(res.data)
    menu = MenuConfiguration().menu_config()
    print(F"List of menu items: {menu}")
    waiter = Waiters(5)
    waiters = waiter.creating_waiters()
    print(F"The list of waiters is: {waiters}")
    return res, menu, waiters


def initialization(cur, inptdata):
    """Initialize tables in database"""
    cur.execute('create table if not exists seat (seatID integer, tableID integer, itemID integer, state text)')
    cur.execute("create table if not exists restaurant_tables (tableID integer, orderID integer)")

    for i, k in inptdata[0].data.items():
        for m in range(1, k + 1):
            cur.execute("insert into seat values (?, ?, ?, ?)", (m, i, None, None))
        cur.execute("insert into restaurant_tables values (?, ?)", (i, None))

    for row in cur.execute("select * from seat"):
        print(row)
    print("************* RESTAURANT TABLES ***************")
    for row in cur.execute("select * from restaurant_tables"):
        print(row)

    cur.execute('create table if not exists menu (itemID integer, itemPrice integer)')

    for i, k in inptdata[1].items():
        cur.execute("insert into menu values (?, ?)", (i.lower(), k))
    print("****************************")
    for row in cur.execute("select * from menu"):
        print(row)

    cur.execute('create table if not exists waiter (waiterID integer, waiterName text, waiterStatus text)')

    for i, k in inptdata[2].items():
        cur.execute("insert into waiter values (?, ?, ?)", (i, k, "Free"))
    print("****************************")
    for row in cur.execute("select * from waiter"):
        print(row)


def order_mode(cur, waiter):
    """Place order and updating tables accordingly"""
    print("**************PLACE ORDER**************")

    item = "water"
    table3 = 3
    itemstate = "pending"

    # specifying seats
    cur.execute("select * from seat where tableID=:c", {"c": table3})
    selected_seat = cur.fetchall()
    # print(selected_seat)

    # specifying menu items
    cur.execute("select * from menu where itemID=:c", {"c": item.lower()})
    selected_item = cur.fetchall()
    # print(selected_item)

    # insert values
    for i in range(len(selected_seat)):
        # print(F"selected seats are {selected_seat[i][0]}")
        cur.execute(F"update seat set itemID=? , state=? where tableID=?", (selected_item[0][0], itemstate, table3))
    print("**************NEW SEAT TABLE**************")

    # printing an updated table - SEAT
    cur.execute("select * from seat where tableID=:c", {"c": table3})
    selected_seat = cur.fetchall()
    print(selected_seat)

    # specifying the order number and the waiter
    cur.execute('create table if not exists orders (orderID integer, tableID integer, waiterID integer, state text)')
    orderno = 1
    order_state = "in_progress"

    cur.execute("select * from waiter where waiterStatus=? and waiterID=?", ("Free", waiter))
    selected_waiter = cur.fetchall()
    print(selected_waiter)

    # creating the order table
    cur.execute("insert into orders values (?, ?, ?, ?)", (orderno, table3, waiter, order_state))

    # printing an updated table - ORDER
    cur.execute("select * from orders where tableID=:c", {"c": table3})
    selected_order = cur.fetchall()
    print(selected_order)

    # updating restaurant_tables table
    cur.execute(F"update restaurant_tables set orderID=? where tableID=?", (orderno, table3))

    cur.execute("select * from restaurant_tables")
    selected_restaurant_tables = cur.fetchall()
    print(selected_restaurant_tables)

    # updating waiter state
    cur.execute("update waiter set waiterStatus=? where waiterID=?", ("Busy", waiter))
    cur.execute("select * from waiter")
    selected_waiter_table = cur.fetchall()
    print(selected_waiter_table)


def cooking(cur, tableID):
    """This method turns the seat state from pending to ready.
    The waiter can pick up the order when it is ready"""
    cur.execute("update seat set state=? where tableID=?", ("Ready", tableID))


def served_customer(cur, tableID, waiter):
    cur.execute("update seat set state=? where tableID=?", ("Served", tableID))
    cur.execute("select * from seat where tableID=:c", {"c": tableID})
    served_seats = cur.fetchall()
    print(F"served seats are: {served_seats}")
    for i in range(len(served_seats)):
        if served_seats[i][3] != 'Served':
            return None
    cur.execute("update waiter set waiterStatus=? where waiterID=?", ("Free", waiter))
    cur.execute("update orders set state=? where tableID=?", ("Completed", tableID))


def total(cur, tableID):
    totall = 0
    cur.execute("select * from seat where tableID=:c", {"c": tableID})
    served_seats = cur.fetchall()

    for i in range(len(served_seats)):
        cur.execute("select * from menu where itemID=:c", {"c": served_seats[i][2]})
        selected_menu = cur.fetchall()
        totall += selected_menu[0][1]
    return totall

    # if served_seats[i][3] != '':
    #     cur.execute("update seat set ")
    # if served_seats[i][3] != 'Served':
    #     cur.execute("update seat set state=? where waiterID=?", ("Free", waiter))
    #     return None

    # cur.execute("select * from orders where tableID=:c", {"c": tableID})
    # completedOrder = cur.fetchall()
    # if completedOrder[3] != "Completed":
    #     return "Can't generate the bill now"
    #
    # cur.execute("select * from seat where tableID=:c", {"c": tableID})
    # served_seats = cur.fetchall()
    # for i in range(len(served_seats)):
    #     if served_seats[i][3] != 'Served':
    #         return None


def completed_orders(cur):
    cur.execute("select * from orders where state=:c", {"c": "Completed"})
    orders = cur.fetchall()
    print(orders)


def in_progress_orders(cur):
    cur.execute("select * from orders where state=?", "in_progress")
    orders = cur.fetchall()


def delete_tables(cur):
    """Delete tables and start again"""
    cur.execute("drop table seat")

    cur.execute("drop table menu")

    cur.execute("drop table restaurant_tables")

    cur.execute("drop table waiter")

    cur.execute("drop table orders")


class Constants:
    background_color = "#3A7FF6"
    btn_color = "#294D8B"
    font = 'Calibri'


class HomeScreen(tk.Frame):

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        width = kwargs['width']
        height = kwargs['height']

        self.root = root

        title = tk.Label(self, text="Welcome to \n Restaurant Management System", font=(Constants.font, 25, 'bold'),
                         bg=Constants.background_color, fg="White", anchor=tk.W)
        title.place(anchor='center', x=str(width * 0.5), y=str(0.1 * height))

        tk.Label(self, text="This desktop app intends to help managers to monitor the restaurants properly",
                 font=(Constants.font, 12), bg=Constants.background_color, fg="White").place(anchor='center',
                 x=str(width / 2), y=str(0.25 * height))

        # Restaurant Configuration Button
        btn_1 = tk.Button(self, text="Restaurant Configuration", height=2, width=25,
            command=self.load_restaurant_configuration_page, font=(Constants.font, 12, 'bold'), bg=Constants.btn_color,
            fg="White", cursor="hand2")
        btn_1.place(anchor='center', x=str(width / 2), y=str(0.35 * height))

        # Menu Configuration Button
        btn_2 = tk.Button(self, text="Menu Configuration", height=2, width=25, command=configure_menu,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_2.place(anchor='center', x=str(width / 2), y=str(0.45 * height))

        # Waiter Configuration Button
        btn_3 = tk.Button(self, text="Waiters Configuration", height=2, width=25, command=lambda: configure_waiters(),
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_3.place(anchor='center', x=str(width / 2), y=str(0.55 * height))

        # Past Orders Button
        btn_4 = tk.Button(self, text="Past\nOrders", height=2, width=10, command=self.past_orders,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_4.place(anchor='center', x=str(width * 0.95), y=str(0.85 * height))

        # In-Progress Orders Button
        btn_5 = tk.Button(self, text="In-Progress\nOrders", height=2, width=10, command=lambda: in_progress_orders2(),
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_5.place(anchor='center', x=str(width * 0.88), y=str(0.85 * height))

        # New Orders Button
        btn_6 = tk.Button(self, text="+ New Order", height=2, width=10, command=lambda: in_progress_orders2(),
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_6.place(anchor='center', x=str(width * 0.05), y=str(0.85 * height))

    def load_restaurant_configuration_page(self):
        print('load_restaurant_configuration_page')
        self.root.frame3.tkraise()

    def past_orders(self):
        cur = self.root.db.cursor()
        completed_orders(cur)
        self.root.frame4.tkraise()


class RestaurantConfigScreen(tk.Frame):

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.root = root

        width = kwargs['width']
        height = kwargs['height']

        tk.Label(self, text="Restaurant Configuration", fg="black", font=(Constants.font, 20)).pack(pady=25, padx=25)

        tk.Label(self, text="Number of Tables", font=(Constants.font, 12, 'bold'), fg="Black")\
            .place(anchor='center', x=str(width * 0.1), y=str(0.15 * height))

        self.tables = tk.StringVar()

        self.table_entry = tk.Entry(self, font=(Constants.font, 16, 'bold'), bd=2, insertwidth=2, justify='left',
                                    textvariable=self.tables, state="normal")
        self.table_entry.place(anchor='e', x=str(width * 0.22), y=str(0.20 * height))

        # Submit Button
        btn_11 = tk.Button(self, text="Add", height=2, width=10, command=self.add_table,
                           font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_11.place(anchor='e', x=str(width * 0.22), y=str(0.30 * height))

        # Back Button
        btn_10 = tk.Button(self, text="Back", height=2, width=10, command=self.back_to_home,
                           font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_10.place(anchor='center', x=str(width * 0.95), y=str(0.85 * height))

    def back_to_home(self):
        self.root.frame1.tkraise()

    def add_table(self):
        print(F"Table: {self.tables.get()}")
        test(self.tables)
        self.table_entry["state"] = "disabled"


def test(x):
    try:
        x = x.get()
        if not x:
            messagebox.showinfo("Warning", "Please insert the missing data !")
            return
        x = int(x)
    except ValueError:
        messagebox.showinfo("Warning", "Please provide an integer number !")


class PastOrdersScreen(tk.Frame):

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.root = root

        width = kwargs['width']
        height = kwargs['height']

        tk.Label(
            self,
            text="Past Orders",
            # bg=background_color,
            fg="black",
            font=("Ubuntu", 20)
        ).pack(pady=25, padx=25)

        # recipe ingredients widgets
        if True:
            for i in range(1, 15):
                tk.Label(
                    self,
                    text=i,
                    bg="#28393a",
                    fg="white",
                    font=(Constants.font, 12),
                ).pack(fill="both", padx=25)
                # ).place(anchor='center', x=str(width * 0.3), y=str(0.03*i * height))

        style = ttk.Style()
        style.configure("Treeview",
                        foreground="black",
                        rowheight=40,
                        fieldbackground="white"
                        )
        style.map('Treeview',
                  background=[('selected', 'lightblue')])
        # rightframe

        CENTER = 'center'

        past_orders_table = tk.Frame(self, width=400, height=700)
        past_orders_table.place(anchor='center', x=str(width * 0.15), y=str(0.3 * height))

        ###########  Creating table #############
        my_tree = ttk.Treeview(past_orders_table)
        my_tree['columns'] = ("ordno", "table", "waiter", "total")

        ############ creating  for table ################
        horizontal_bar = ttk.Scrollbar(past_orders_table, orient="horizontal")
        horizontal_bar.configure(command=my_tree.xview)
        my_tree.configure(xscrollcommand=horizontal_bar.set)
        # horizontal_bar.place(anchor='center',  x=str(width * 0.5), y=str(0.5 * height))

        vertical_bar = ttk.Scrollbar(past_orders_table, orient="vertical")
        vertical_bar.configure(command=my_tree.yview)
        my_tree.configure(yscrollcommand=vertical_bar.set)
        # vertical_bar.place(anchor='center',  x=str(width * 0.5), y=str(0.5 * height))

        # defining columns for table
        my_tree.column("#0", width=0, minwidth=0)
        my_tree.column("ordno", anchor=CENTER, width=80, minwidth=25)
        my_tree.column("table", anchor=CENTER, width=60, minwidth=25)
        my_tree.column("waiter", anchor=CENTER, width=60, minwidth=25)
        my_tree.column("total", anchor=CENTER, width=50, minwidth=25)

        # defining  headings for table
        my_tree.heading("ordno", text="Order No", anchor=CENTER)
        my_tree.heading("table", text="Table", anchor=CENTER)
        my_tree.heading("waiter", text="Waiter", anchor=CENTER)
        my_tree.heading("total", text="Total", anchor=CENTER)

        my_tree.place(anchor='center', x=str(width * 0.15), y=str(0.5 * height))

        # Order Details Button
        btn_7_label = tk.StringVar(value="Order\nDetails")
        btn_7 = tk.Button(self, textvariable=btn_7_label, height=2, width=10, command=lambda: in_progress_orders2(),
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_7.place(anchor='center', x=str(width * 0.10), y=str(0.85 * height))

        # Delete Order Button
        btn_8_label = tk.StringVar(value="Delete\nOrder")
        btn_8 = tk.Button(self, textvariable=btn_8_label, height=2, width=10, command=lambda: in_progress_orders2(),
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_8.place(anchor='center', x=str(width * 0.18), y=str(0.85 * height))

        # Back Button
        btn_9_label = tk.StringVar(value="Back")
        btn_9 = tk.Button(self, textvariable=btn_9_label, height=2, width=10, command=self.back_to_home,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_9.place(anchor='center', x=str(width * 0.95), y=str(0.85 * height))

    def back_to_home(self):
        self.root.frame1.tkraise()

    def add_table(self):
        print(F"Table: {self.tables.get()}")
        # test(self.tables)
        # self.table_entry["state"] = "disabled"


class RootWindow(tk.Tk):

    def __init__(self, db):
        super().__init__()
        self.db = db

        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry(F"{width}x{height}")
        self.title("Restaurant Management System")

        # create a frame widgets
        self.frame1 = HomeScreen(self, width=width, height=height, bg=Constants.background_color)
        self.frame2 = tk.Frame(self)
        self.frame3 = RestaurantConfigScreen(self, width=width, height=height, bg=Constants.background_color)
        self.frame4 = PastOrdersScreen(self, width=width, height=height, bg=Constants.background_color)

        # place frame widgets in window
        for frame in (self.frame1, self.frame2, self.frame3, self.frame4):
            frame.grid(row=0, column=0, sticky="nesw")

        self.frame1.tkraise()
#        load_home_page()

        # load_past_orders()


def system():
    background_color = "#3A7FF6"
    btn_color = "#294D8B"
    font = 'Calibri'
    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry(F"{width}x{height}")
    root.title("Restaurant Management System")

    # create a frame widgets
    frame1 = HomeScreen(root, width=width, height=height, bg=background_color)
    frame2 = tk.Frame(root)
    frame3 = RestaurantConfigScreen(root, width=width, height=height, bg=background_color)

    def clear_widgets(framee):
        # select all frame widgets and delete them
        for widget in framee.winfo_children():
            widget.destroy()

    def load_home_page():

        # stack frame 2 above frame 1
        frame1.tkraise()

        return

        title = tk.Label(root, text="Welcome to \n Restaurant Management System", font=(font, 25, 'bold'),
                         bg=background_color, fg="White", anchor=tk.W)
        title.place(anchor='center', x=str(width * 0.5), y=str(0.1 * height))

        tk.Label(frame1, text="This desktop app intends to help managers to monitor the restaurants properly",
                 font=(font, 12), bg=background_color, fg="White").place(anchor='center', x=str(width / 2),
                                                                         y=str(0.25 * height))

        # Restaurant Configuration Button
        btn_1_label = tk.StringVar(value="Restaurant Configuration")
        btn_1 = tk.Button(frame1, textvariable=btn_1_label, height=2, width=25,
                          command=load_restaurant_configuration_page,
                          font=(font, 12, 'bold'), bg=btn_color, fg="White", cursor="hand2")
        btn_1.place(anchor='center', x=str(width / 2), y=str(0.35 * height))

        # Menu Configuration Button
        btn_2_label = tk.StringVar(value="Menu Configuration")
        btn_2 = tk.Button(frame1, textvariable=btn_2_label, height=2, width=25, command=configure_menu,
                          font=(font, 12, 'bold'), bg=btn_color, fg="White")
        btn_2.place(anchor='center', x=str(width / 2), y=str(0.45 * height))

        # Waiter Configuration Button
        btn_3_label = tk.StringVar(value="Waiters Configuration")
        btn_3 = tk.Button(frame1, textvariable=btn_3_label, height=2, width=25, command=lambda: configure_waiters(),
                          font=(font, 12, 'bold'), bg=btn_color, fg="White")
        btn_3.place(anchor='center', x=str(width / 2), y=str(0.55 * height))

        # Past Orders Button
        btn_4_label = tk.StringVar(value="Past\nOrders")
        btn_4 = tk.Button(frame1, textvariable=btn_4_label, height=2, width=10, command=lambda: load_past_orders(),
                          font=(font, 12, 'bold'), bg=btn_color, fg="White")
        btn_4.place(anchor='center', x=str(width * 0.95), y=str(0.85 * height))

        # In-Progress Orders Button
        btn_5_label = tk.StringVar(value="In-Progress\nOrders")
        btn_5 = tk.Button(frame1, textvariable=btn_5_label, height=2, width=10, command=lambda: in_progress_orders2(),
                          font=(font, 12, 'bold'), bg=btn_color, fg="White")
        btn_5.place(anchor='center', x=str(width * 0.88), y=str(0.85 * height))

        # New Orders Button
        btn_6_label = tk.StringVar(value="+ New Order")
        btn_6 = tk.Button(frame1, textvariable=btn_6_label, height=2, width=10, command=lambda: in_progress_orders2(),
                          font=(font, 12, 'bold'), bg=btn_color, fg="White")
        btn_6.place(anchor='center', x=str(width * 0.05), y=str(0.85 * height))

    def load_past_orders():
        clear_widgets(frame1)

        # stack frame 2 above frame 1
        frame2.tkraise()

        # recipe title widget
        tk.Label(
            frame2,
            text="Past Orders",
            # bg=background_color,
            fg="black",
            font=("Ubuntu", 20)
        ).pack(pady=25, padx=25)

        # recipe ingredients widgets
        if True:
            for i in range(1, 15):
                tk.Label(
                    frame2,
                    text=i,
                    bg="#28393a",
                    fg="white",
                    font=(font, 12),
                ).pack(fill="both", padx=25)
                # ).place(anchor='center', x=str(width * 0.3), y=str(0.03*i * height))


        style = ttk.Style()
        style.configure("Treeview",
                        foreground="black",
                        rowheight=40,
                        fieldbackground="white"
                        )
        style.map('Treeview',
                  background=[('selected', 'lightblue')])
        # rightframe

        CENTER = 'center'

        past_orders_table = tk.Frame(frame2, width=400, height=700)
        past_orders_table.place(anchor='center', x=str(width * 0.15), y=str(0.3 * height))

        ###########  Creating table #############
        my_tree = ttk.Treeview(past_orders_table)
        my_tree['columns'] = ("ordno", "table", "waiter", "total")

        ############ creating  for table ################
        horizontal_bar = ttk.Scrollbar(past_orders_table, orient="horizontal")
        horizontal_bar.configure(command=my_tree.xview)
        my_tree.configure(xscrollcommand=horizontal_bar.set)
        # horizontal_bar.place(anchor='center',  x=str(width * 0.5), y=str(0.5 * height))

        vertical_bar = ttk.Scrollbar(past_orders_table, orient="vertical")
        vertical_bar.configure(command=my_tree.yview)
        my_tree.configure(yscrollcommand=vertical_bar.set)
        # vertical_bar.place(anchor='center',  x=str(width * 0.5), y=str(0.5 * height))

        # defining columns for table
        my_tree.column("#0", width=0, minwidth=0)
        my_tree.column("ordno", anchor=CENTER, width=80, minwidth=25)
        my_tree.column("table", anchor=CENTER, width=60, minwidth=25)
        my_tree.column("waiter", anchor=CENTER, width=60, minwidth=25)
        my_tree.column("total", anchor=CENTER, width=50, minwidth=25)

        # defining  headings for table
        my_tree.heading("ordno", text="Order No", anchor=CENTER)
        my_tree.heading("table", text="Table", anchor=CENTER)
        my_tree.heading("waiter", text="Waiter", anchor=CENTER)
        my_tree.heading("total", text="Total", anchor=CENTER)

        my_tree.place(anchor='center', x=str(width * 0.15), y=str(0.5 * height))

        # Order Details Button
        btn_7_label = tk.StringVar(value="Order\nDetails")
        btn_7 = tk.Button(frame2, textvariable=btn_7_label, height=2, width=10, command=lambda: in_progress_orders2(),
                          font=(font, 12, 'bold'), bg=btn_color, fg="White")
        btn_7.place(anchor='center', x=str(width * 0.10), y=str(0.85 * height))

        # Delete Order Button
        btn_8_label = tk.StringVar(value="Delete\nOrder")
        btn_8 = tk.Button(frame2, textvariable=btn_8_label, height=2, width=10, command=lambda: in_progress_orders2(),
                          font=(font, 12, 'bold'), bg=btn_color, fg="White")
        btn_8.place(anchor='center', x=str(width * 0.18), y=str(0.85 * height))

        # Back Button
        btn_9_label = tk.StringVar(value="Back")
        btn_9 = tk.Button(frame2, textvariable=btn_9_label, height=2, width=10, command=lambda: load_home_page(),
                          font=(font, 12, 'bold'), bg=btn_color, fg="White")
        btn_9.place(anchor='center', x=str(width * 0.95), y=str(0.85 * height))

    def load_restaurant_configuration_page():
#        clear_widgets(frame1)

        # stack frame 3 above frame 1
        frame3.tkraise()

        return

        tk.Label(frame3, text="Restaurant Configuration", fg="black", font=(font, 20)).pack(pady=25, padx=25)

        tk.Label(frame3, text="Number of Tables", font=(font, 12, 'bold'), fg="Black")\
            .place(anchor='center', x=str(width * 0.1), y=str(0.15 * height))

        tables = tk.StringVar()

        global entry_state
        entry_state = "normal"

        tk.Entry(frame3, font=(font, 16, 'bold'), bd=2, insertwidth=2, justify='left', textvariable=tables,
                 state=entry_state).place(anchor='e', x=str(width * 0.22), y=str(0.20 * height))

        # Submit Button
        btn_11_label = tk.StringVar(value="Add")
        btn_11 = tk.Button(frame3, textvariable=btn_11_label, height=2, width=10, command=lambda: test(tables),
                           font=(font, 12, 'bold'), bg=btn_color, fg="White")
        btn_11.place(anchor='e', x=str(width * 0.22), y=str(0.30 * height))

        # Back Button
        btn_10_label = tk.StringVar(value="Back")
        btn_10 = tk.Button(frame3, textvariable=btn_10_label, height=2, width=10, command=lambda: load_home_page(),
                          font=(font, 12, 'bold'), bg=btn_color, fg="White")
        btn_10.place(anchor='center', x=str(width * 0.95), y=str(0.85 * height))

        def test(x):
            try:
                x = x.get()
                if not x:
                    messagebox.showinfo("Warning", "Please insert the missing data !")
                    return
                x = int(x)
            except ValueError:
                messagebox.showinfo("Warning", "Please provide an integer number !")

    # place frame widgets in window
    for frame in (frame1, frame2, frame3):
        frame.grid(row=0, column=0, sticky="nesw")

    load_home_page()

    # load_past_orders()

    root.mainloop()


def configure_restaurant():
    print("restaurant")


def configure_menu():
    print("menu")


def configure_waiters():
    print("waiter")
    messagebox.showinfo("Warning", "CRASH!!!")


def past_orders():
    print("past orders")


def in_progress_orders2():
    print("In-progress orders")

def test_data(db):
    cur = db.cursor()

    inptdata = input_data()
    waiter = 2
    table = 3

    initialization(cur, inptdata)

    order_mode(cur, waiter)

    cooking(cur, table)

    served_customer(cur, table, waiter)

    db.commit()

    # delete_tables(cur)

def main():
    db = sqlite3.connect('restaurant.db')
    # test_data(db)
    root = RootWindow(db)
    root.mainloop()

    db.close()


#    system()

    # inptdata = input_data()
    #
    #
    # cur = db.cursor()
    #
    # waiter = 2
    # table = 3
    #
    # initialization(cur, inptdata)
    #
    # order_mode(cur, waiter)
    #
    # cooking(cur, table)
    #
    # served_customer(cur, table, waiter)
    #
    # completed_orders(cur)
    #
    # total1 = total(cur, table)
    #
    # print(F"The total bill for table {table} is {total1}")
    #
    # delete_tables(cur)
    #
    # db.commit()
    #
    # db.close()


if __name__ == '__main__':
    main()
