import operator
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
    cur.execute('create table if not exists seat (seatID integer, tableID integer, itemID text, state text)')
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

    cur.execute('create table if not exists menu (itemID text, itemPrice integer)')

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


def completed_orders(cur):
    try:
        x = cur.execute("select * from orders where state=:c", {"c": "Completed"})
        return x
    except sqlite3.OperationalError:
        messagebox.showinfo("Warning", "There are no past orders table !")
        return None


def in_progress_orders(cur):
    cur.execute("select * from orders where state=?", "in_progress")
    orders = cur.fetchall()


def most_popular_item(cur):
    item_list = {}
    cur.execute("select * from seat where itemID is not null")
    popular_item_fetch = cur.fetchall()
    if not popular_item_fetch:
        messagebox.showinfo("Message", "No items for seats")
        return
    for i in popular_item_fetch:
        item_list[i[2]] = item_list.get(i[2], 0) + 1
    sorted_item_list = sorted(item_list.items(), key=operator.itemgetter(1), reverse=True)
    return sorted_item_list

def delete_tables(cur):
    """Delete tables and start again"""
    cur.execute("drop table seat")

    cur.execute("drop table menu")

    cur.execute("drop table restaurant_tables")

    cur.execute("drop table waiter")

    cur.execute("drop table orders")


def test(x, cond):
    try:
        x = x.get()
        if not x:
            messagebox.showinfo("Warning", "Please insert the missing data !")
            return
        if cond == "int":
            x = int(x)
            return x
        if cond == "float":
            x = float(x)
            return x
        if cond == "str":
            x = x.lower()
            return x
    except ValueError:
        messagebox.showinfo("Warning", "Please provide an integer number !")


def new_order_test(cur):
    table_cursor = cur.execute("select * from restaurant_tables")
    table_fetch = table_cursor.fetchall()
    print(table_fetch)
    if not table_fetch:
        messagebox.showinfo("Warning", "There are no tables !\nPlease define tables first")
        return None

    menu_cursor = cur.execute("select * from menu")
    menu_fetch = menu_cursor.fetchall()
    print(menu_fetch)
    if not menu_fetch:
        messagebox.showinfo("Warning", "There is no menu !\nPlease define the menu first")
        return None

    waiter_cursor = cur.execute("select * from waiter")
    waiter_fetch = waiter_cursor.fetchall()
    print(waiter_fetch)
    if not waiter_fetch:
        messagebox.showinfo("Warning", "There are no waiters !\nPlease define the waiters first")
        return None
    return True


def seat_item_test(cur, seat, item, table):
    seat_cursor = cur.execute("select * from seat where tableID=:c and seatID=:d", {"c": table, "d": seat})
    seat_fetch = seat_cursor.fetchall()
    print(seat_fetch)
    if not seat_fetch:
        messagebox.showinfo(F"Warning", f"There is no seat {seat} in table {table}!\nPlease choose the right seat")
        return None

    menu_cursor = cur.execute(F"select * from menu where itemID=:c", {"c": item})
    menu_fetch = menu_cursor.fetchall()
    print(menu_fetch)
    if not menu_fetch:
        messagebox.showinfo(F"Warning", f"There is no item: {item} !\nPlease choose from the list")
        return None
    return True


def tracked_table_test(cur, table):
    table_cursor = cur.execute("select * from restaurant_tables where tableID=:c", {"c": table})
    table_fetch = table_cursor.fetchall()
    if not table_fetch:
        messagebox.showinfo(F"Warning", f"There is no table {table}!\nPlease choose the correct table")
        return None
    return True

def check_if_table_test(cur):
    table_cursor = cur.execute("select * from restaurant_tables")
    table_fetch = table_cursor.fetchall()
    if not table_fetch:
        messagebox.showinfo(F"Warning", f"There are no tables to delete !")
        return None
    return table_fetch


class Constants:
    background_color = "#3A7FF6"
    fg_color = "white"
    btn_color = "#294D8B"
    font = 'Calibri'


class HomeScreen(tk.Frame):

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        width = kwargs['width']
        height = kwargs['height']
        self.root = root
        self.cur = self.root.db.cursor()

        title = tk.Label(self, text="Welcome to \n Restaurant Management System", font=(Constants.font, 25, 'bold'),
                         bg=Constants.background_color, fg="White", anchor=tk.W)
        title.place(anchor='center', x=str(width * 0.5), y=str(0.1 * height))

        tk.Label(self, text="This desktop app intends to help managers to monitor the restaurants properly",
                 font=(Constants.font, 12), bg=Constants.background_color, fg="White") \
            .place(anchor='center', x=str(width / 2), y=str(0.25 * height))

        # Restaurant Configuration Button
        btn_1 = tk.Button(self, text="Restaurant Configuration", height=2, width=25,
                          command=self.load_restaurant_configuration_page, font=(Constants.font, 12, 'bold'),
                          bg=Constants.btn_color, fg="White")
        btn_1.place(anchor='center', x=str(width / 2), y=str(0.35 * height))

        # Menu Configuration Button
        btn_2 = tk.Button(self, text="Menu Configuration", height=2, width=25, command=self.load_menu_config,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_2.place(anchor='center', x=str(width / 2), y=str(0.45 * height))

        # Waiter Configuration Button
        btn_3 = tk.Button(self, text="Waiters Configuration", height=2, width=25, command=self.load_waiter_config,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_3.place(anchor='center', x=str(width / 2), y=str(0.55 * height))

        # Past Orders Button
        btn_4 = tk.Button(self, text="Past\nOrders", height=2, width=10, command=self.past_orders,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_4.place(anchor='center', x=str(width * 0.95), y=str(0.85 * height))

        # In-Progress Orders Button
        btn_5 = tk.Button(self, text="In-Progress\nOrders", height=2, width=10,
                          command=self.load_in_progress_orders_screen,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_5.place(anchor='center', x=str(width * 0.88), y=str(0.85 * height))

        # New Orders Button
        btn_6 = tk.Button(self, text="+ New Order", height=2, width=10, command=self.load_new_order_screen,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_6.place(anchor='center', x=str(width * 0.05), y=str(0.85 * height))

        # Reset Button
        self.btn_13 = tk.Button(self, text="Restore\nDefault", height=2, width=6, command=self.restore_default,
                                font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        self.btn_13.place(anchor='center', x=str(width * 0.95), y=str(0.10 * height))
    def past_orders(self):
        x = new_order_test(self.cur)
        if not x:
            return
        x = completed_orders(self.cur)
        if not x:
            return
        self.root.frame4.tkraise()

    def load_menu_config(self):
        self.root.frame2.tkraise()

    def load_restaurant_configuration_page(self):
        self.root.frame3.tkraise()

    def load_waiter_config(self):
        self.root.frame5.tkraise()

    def load_new_order_screen(self):
        x = new_order_test(self.cur)
        if not x:
            return
        self.root.frame6.tkraise()

    def load_in_progress_orders_screen(self):
        x = new_order_test(self.cur)
        if not x:
            return
        self.root.frame7.tkraise()

    def restore_default(self):
        self.cur.execute("delete from seat")
        self.cur.execute("delete from menu")
        self.cur.execute("delete from restaurant_tables")
        self.cur.execute("delete from waiter")
        self.cur.execute("delete from orders")
        self.root.db.commit()
        messagebox.showinfo("Message", "All data are deleted permanently !")


class RestaurantConfigScreen(tk.Frame):

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.root = root
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.tested_seats = {}
        self.entry_seats = []
        self.cur = self.root.db.cursor()
        tk.Label(self, text="Restaurant Configuration", fg=Constants.fg_color, bg=Constants.background_color,
                 font=(Constants.font, 20, "bold")).pack(pady=25, padx=25)

        # Table-Seat Tree
        style = ttk.Style()
        style.configure("Treeview", foreground="black", rowheight=35, fieldbackground="white")
        style.map('Treeview', background=[('selected', 'lightblue')])

        CENTER = 'center'

        self.restaurant_table_frame = tk.Frame(self, width=180, height=390, bg=Constants.background_color)
        self.restaurant_table_frame.place(anchor='center', x=str(self.width * 0.15), y=str(0.38 * self.height))
        ###########  Creating table #############
        self.restaurant_table_tree = ttk.Treeview(self.restaurant_table_frame)
        self.restaurant_table_tree['columns'] = ("table", "seat")

        ############ creating  for table ################
        horizontal_bar = ttk.Scrollbar(self.restaurant_table_frame, orient="horizontal")
        horizontal_bar.configure(command=self.restaurant_table_tree.xview)
        self.restaurant_table_tree.configure(xscrollcommand=horizontal_bar.set)

        vertical_bar = ttk.Scrollbar(self.restaurant_table_frame, orient="vertical")
        vertical_bar.configure(command=self.restaurant_table_tree.yview)
        self.restaurant_table_tree.configure(yscrollcommand=vertical_bar.set)

        # defining columns for table
        self.restaurant_table_tree.column("#0", width=0, minwidth=0)
        self.restaurant_table_tree.column("table", anchor=CENTER, width=80, minwidth=25)
        self.restaurant_table_tree.column("seat", anchor=CENTER, width=80, minwidth=25)

        # defining  headings for table
        self.restaurant_table_tree.heading("table", text="Table", anchor=CENTER)
        self.restaurant_table_tree.heading("seat", text="Seat", anchor=CENTER)

        self.restaurant_table_tree.place(anchor='center', x=str(self.width * 0.065), y=str(0.25 * self.height))
        self.display_data()

        tk.Label(self, text="Number of Tables", font=(Constants.font, 12, 'bold'), fg="Black") \
            .place(anchor='e', x=str(self.width * 0.33), y=str(0.15 * self.height))
        self.tables = tk.StringVar()
        self.table_entry = tk.Entry(self, font=(Constants.font, 16, 'bold'), bd=2, insertwidth=2, justify='left',
                                    textvariable=self.tables, state="normal")
        self.table_entry.place(anchor='e', x=str(self.width * 0.4), y=str(0.2 * self.height))

        # Add Tables Button
        self.btn_11 = tk.Button(self, text="Add", height=2, width=10, command=self.add_table,
                                font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        self.btn_11.place(anchor='e', x=str(self.width * 0.39), y=str(0.30 * self.height))

        # Delete Button
        btn_6 = tk.Button(self, text="Delete\nTables", height=2, width=10, command=self.delete_restaurant_tables,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_6.place(anchor='center', x=str(self.width * 0.1), y=str(0.85 * self.height))

        # Back Button
        btn_10 = tk.Button(self, text="Back", height=2, width=10, command=self.back_to_home,
                           font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_10.place(anchor='center', x=str(self.width * 0.95), y=str(0.85 * self.height))

        # Seats
    def display_data(self):
        try:
            restaurant_table_cursor = self.cur.execute("select tableID , seatID from seat order by tableID asc")
            restaurant_table_fetch = restaurant_table_cursor.fetchall()
            for i in restaurant_table_fetch:
                self.restaurant_table_tree.insert('', 'end', values=i)
        except sqlite3.OperationalError:
            pass

    def add_seats(self):
        self.seats = [tk.StringVar()] * self.result
        tk.Label(self, font=(Constants.font, 18, 'bold'), text=F"Seats Per Table", fg="Black",
                 bg=Constants.background_color, anchor="center") \
            .place(anchor='e', x=str(self.width * 0.59), y=str(0.20 * self.height))
        for i in range(1, self.result + 1):
            self.seats[i - 1] = tk.StringVar()
            seatlbl = tk.Label(self, font=(Constants.font, 16, 'bold'), text=F"Table {i}",
                               fg="Black", bg=Constants.background_color, anchor="center")
            seatlbl.place(anchor='center', x=str(self.width * 0.5), y=str(0.2 * self.height + i * 40))

            seatentry = tk.Entry(self, font=(Constants.font, 16, 'bold'), bd=2, insertwidth=2, justify='left',
                                 state="normal", textvariable=self.seats[i - 1])
            seatentry.place(anchor='center', x=str(self.width * 0.62), y=str(0.2 * self.height + i * 40))
            self.entry_seats.append(seatentry)

        # Add Button
        btn_12 = tk.Button(self, text="Add Seats", height=2, width=10, font=(Constants.font, 12, 'bold'),
                           bg=Constants.btn_color, fg="White", command=self.add_table_seats)
        btn_12.place(anchor='center', x=str(self.width * 0.55), y=str(0.85 * self.height))

    def back_to_home(self):
        self.root.frame1.tkraise()

    def add_table(self):
        self.result = test(self.tables, "int")
        if self.result:
            self.add_seats()
            self.table_entry["state"] = "disabled"
            self.btn_11["state"] = "disabled"

    def add_table_seats(self):
        for i in range(1, self.result + 1):
            get_seat = self.seats[i - 1]
            test_seat = test(get_seat, "int")
            if test_seat is None:
                return
            self.tested_seats[i] = self.tested_seats.get(i, test_seat)
        self.cur.execute(
            'create table if not exists seat (seatID integer, tableID integer, itemID text, state text)')
        self.cur.execute("create table if not exists restaurant_tables (tableID integer, orderID integer)")
        for i, k in self.tested_seats.items():
            self.entry_seats[i - 1]["state"] = "disabled"
            for m in range(1, k + 1):
                self.cur.execute("insert into seat values (?, ?, ?, ?)", (m, i, None, None))
            self.cur.execute("insert into restaurant_tables values (?, ?)", (i, None))
        messagebox.showinfo("Message", "Tables have been added successfully !")
        self.display_data()
        self.root.db.commit()

    def delete_restaurant_tables(self):
        check = check_if_table_test(self.cur)
        if check:
            result = messagebox.askquestion('Confirm', 'Are you sure you want to delete the tables?',
                                            icon="warning")
            if result == 'yes':
                """Delete tables and start again"""
                self.cur.execute("delete from restaurant_tables")
                self.cur.execute("delete from seat")
                messagebox.showinfo("Message", "Tables have been deleted successfully !")
                self.restaurant_table_tree.delete(*self.restaurant_table_tree.get_children())
                self.root.db.commit()
                self.table_entry["state"] = "normal"
                self.btn_11["state"] = "normal"
                self.tables.set("")
                for i in range(1, len(check) + 1):
                    self.seats[i - 1].set("")
                    self.entry_seats[i - 1]["state"] = "normal"
                self.root.db.commit()


class PastOrdersScreen(tk.Frame):

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.root = root
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.cur = self.root.db.cursor()
        tk.Label(self, text="Past Orders", bg=Constants.background_color, fg="black", font=("Ubuntu", 20)) \
            .pack(pady=25, padx=25)

        # Tree
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

        past_orders_frame = tk.Frame(self, width=400, height=700, bg=Constants.background_color)
        past_orders_frame.place(anchor='center', x=str(self.width * 0.15), y=str(0.33 * self.height))
        ###########  Creating table #############
        self.past_orders_tree = ttk.Treeview(past_orders_frame)
        self.past_orders_tree['columns'] = ("ordno", "table", "waiter", "total")

        ############ creating  for table ################
        horizontal_bar = ttk.Scrollbar(past_orders_frame, orient="horizontal")
        horizontal_bar.configure(command=self.past_orders_tree.xview)
        self.past_orders_tree.configure(xscrollcommand=horizontal_bar.set)
        # horizontal_bar.place(anchor='center',  x=str(width * 0.5), y=str(0.5 * height))

        vertical_bar = ttk.Scrollbar(past_orders_frame, orient="vertical")
        vertical_bar.configure(command=self.past_orders_tree.yview)
        self.past_orders_tree.configure(yscrollcommand=vertical_bar.set)
        # vertical_bar.place(anchor='center',  x=str(width * 0.5), y=str(0.5 * height))

        # defining columns for table
        self.past_orders_tree.column("#0", width=0, minwidth=0)
        self.past_orders_tree.column("ordno", anchor=CENTER, width=80, minwidth=25)
        self.past_orders_tree.column("table", anchor=CENTER, width=80, minwidth=25)
        self.past_orders_tree.column("waiter", anchor=CENTER, width=80, minwidth=25)
        self.past_orders_tree.column("total", anchor=CENTER, width=80, minwidth=25)

        # defining  headings for table
        self.past_orders_tree.heading("ordno", text="Order No", anchor=CENTER)
        self.past_orders_tree.heading("table", text="Table", anchor=CENTER)
        self.past_orders_tree.heading("waiter", text="Waiter", anchor=CENTER)
        self.past_orders_tree.heading("total", text="Total", anchor=CENTER)

        self.past_orders_tree.place(anchor='center', x=str(self.width * 0.15), y=str(0.5 * self.height))

        # Refresh Button
        btn_7 = tk.Button(self, text="Refresh", height=2, width=10, command=self.display_data,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_7.place(anchor='center', x=str(self.width * 0.07), y=str(0.85 * self.height))

        # Delete Order Button
        btn_8 = tk.Button(self, text="Delete\nOrder", height=2, width=10, command=self.delete_order,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_8.place(anchor='center', x=str(self.width * 0.18), y=str(0.85 * self.height))

        # Order Details Button
        btn_10 = tk.Button(self, text="Order\nDetails", height=2, width=10, command=self.order_details,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_10.place(anchor='center', x=str(self.width * 0.26), y=str(0.85 * self.height))

        # Back Button
        btn_9 = tk.Button(self, text="Back", height=2, width=10, command=self.back_to_home,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_9.place(anchor='center', x=str(self.width * 0.95), y=str(0.85 * self.height))

        # Show Statistics Button
        btn_11 = tk.Button(self, text="Show", height=1, width=5, command=self.show_statistics,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_11.place(anchor='center', x=str(self.width * 0.93), y=str(0.65 * self.height))

        tk.Label(self, text="Statistics", bg=Constants.background_color, fg="black", font=(Constants.font, 14))\
            .place(anchor='center', x=str(self.width * 0.90), y=str(0.10 * self.height))
        self.statisticss_tree()

    def back_to_home(self):
        self.root.frame1.tkraise()

    def statisticss_tree(self):
        # Tree
        style = ttk.Style()
        style.configure("Treeview", foreground="black", rowheight=40, fieldbackground="white")
        style.map('Treeview', background=[('selected', 'lightblue')])

        CENTER = 'center'

        statistics_frame = tk.Frame(self, width=200, height=400, bg=Constants.background_color)
        statistics_frame.place(anchor='center', x=str(self.width * 0.9), y=str(0.38 * self.height))
        ###########  Creating table #############
        self.statistics_tree = ttk.Treeview(statistics_frame)
        self.statistics_tree['columns'] = ("item", "cumulative_number")

        ############ creating  for table ################
        horizontal_bar = ttk.Scrollbar(statistics_frame, orient="horizontal")
        horizontal_bar.configure(command=self.statistics_tree.xview)
        self.statistics_tree.configure(xscrollcommand=horizontal_bar.set)
        # horizontal_bar.place(anchor='center',  x=str(width * 0.5), y=str(0.5 * height))

        vertical_bar = ttk.Scrollbar(statistics_frame, orient="vertical")
        vertical_bar.configure(command=self.statistics_tree.yview)
        self.statistics_tree.configure(yscrollcommand=vertical_bar.set)
        # vertical_bar.place(anchor='center',  x=str(width * 0.5), y=str(0.5 * height))

        # defining columns for table
        self.statistics_tree.column("#0", width=0, minwidth=0)
        self.statistics_tree.column("item", anchor=CENTER, width=80, minwidth=25)
        self.statistics_tree.column("cumulative_number", anchor=CENTER, width=100, minwidth=25)


        # defining  headings for table
        self.statistics_tree.heading("item", text="Item", anchor=CENTER)
        self.statistics_tree.heading("cumulative_number", text="Cumulative No.", anchor=CENTER)

        self.statistics_tree.place(anchor='center', x=str(self.width * 0.07), y=str(0.25 * self.height))

    def show_statistics(self):
        self.statistics_tree.delete(*self.statistics_tree.get_children())
        items = most_popular_item(self.cur)
        if not items:
            return
        # for k, v in items.items():
        #     self.statistics_tree.insert('', 'end', values=(k, v))
        for data in items:
            self.statistics_tree.insert('', 'end', values=data)

    def order_details(self):
        if not self.past_orders_tree.selection():
            messagebox.showwarning("Warning", "Select order to show details")
            return
        curItem = self.past_orders_tree.focus()
        contents = self.past_orders_tree.item(curItem)
        selecteditem = contents['values']
        tableID = selecteditem[1]
        orderID = selecteditem[0]
        total = selecteditem[3]

        order_seats = self.cur.execute("select * from seat where tableID=:c", {"c": tableID})
        fetch1 = order_seats.fetchall()

        tk.Label(self, text="Order No:", bg=Constants.background_color, fg="black", font=(Constants.font, 12, "bold")) \
            .place(anchor='center', x=str(self.width * 0.35), y=str(0.15 * self.height))
        self.order_no_var = tk.Label(self, text=orderID, bg=Constants.background_color, fg="white", font=(Constants.font, 12), ) \
            .place(anchor='center', x=str(self.width * 0.4), y=str(0.15 * self.height))

        tk.Label(self, text="Table:", bg=Constants.background_color, fg="black", font=(Constants.font, 12, "bold")) \
            .place(anchor='center', x=str(self.width * 0.35), y=str(0.18 * self.height))
        tk.Label(self, text=tableID, bg=Constants.background_color, fg="white", font=(Constants.font, 12), ) \
            .place(anchor='center', x=str(self.width * 0.4), y=str(0.18 * self.height))

        tk.Label(self, text="Total:", bg=Constants.background_color, fg="black", font=(Constants.font, 12, "bold")) \
            .place(anchor='center', x=str(self.width * 0.45), y=str(0.15 * self.height))
        tk.Label(self, text=total, bg=Constants.background_color, fg="white", font=(Constants.font, 12), ) \
            .place(anchor='center', x=str(self.width * 0.5), y=str(0.15 * self.height))

        k = 0
        for i in fetch1:
            k += 1
            itemID = i[2]
            menu_items_seat = self.cur.execute("select * from menu where itemID=:c", {"c": itemID})
            fetch2 = menu_items_seat.fetchone()
            tk.Label(self, text=F"Seat {i[0]}:", bg="white", fg="black", font=(Constants.font, 12), ) \
                .place(anchor='center', x=str(self.width * 0.35), y=str(0.2 * self.height + k * 40))

            tk.Label(self, text=itemID, bg=Constants.background_color, fg="black", font=(Constants.font, 12), ) \
                .place(anchor='center', x=str(0.38 * self.width + 45), y=str(0.2 * self.height + k * 40))
            tk.Label(self, text=fetch2[1], bg=Constants.background_color, fg="white", font=(Constants.font, 10), ) \
                .place(anchor='center', x=str(0.38 * self.width + 45), y=str(0.225 * self.height + k * 40))

    def delete_order(self):
        result = "No"
        if not self.past_orders_tree.selection():
            messagebox.showwarning("Warning", "Select data to delete")
        else:
            result = messagebox.askquestion('Confirm', 'Are you sure you want to delete this record?',
                                            icon="warning")
        if result == 'yes':
            curItem = self.past_orders_tree.focus()
            contents = self.past_orders_tree.item(curItem)
            selecteditem = contents['values']
            self.past_orders_tree.delete(curItem)
            self.cur.execute("delete from orders where orderID= %d" % selecteditem[0])
            self.root.db.commit()

    def display_data(self):
        p = []
        self.past_orders_tree.delete(*self.past_orders_tree.get_children())
        pastorders = self.cur.execute("select * from orders where state=:c", {"c": 'Completed'})
        fetch = pastorders.fetchall()
        if not fetch:
            messagebox.showinfo("Message", "No past orders")
            return
        for i in fetch:
            ordno = i[0]
            tableno = i[1]
            waiterno = i[2]
            totall = total(self.cur, tableno)
            p.append([ordno, tableno, waiterno, totall])
        for data in p:
            self.past_orders_tree.insert('', 'end', values=data)


class MenuConfigScreen(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.root = root
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.cur = self.root.db.cursor()

        tk.Label(self, text="Menu Configuration", bg=Constants.background_color, fg="black", font=("Ubuntu", 20)) \
            .pack(pady=25, padx=25)

        # Tree
        style = ttk.Style()
        style.configure("Treeview", foreground="black", rowheight=40, fieldbackground="white")
        style.map('Treeview', background=[('selected', 'lightblue')])

        CENTER = 'center'

        past_orders_table = tk.Frame(self, width=400, height=700, bg=Constants.background_color)
        past_orders_table.place(anchor='center', x=str(self.width * 0.15), y=str(0.33 * self.height))
        ###########  Creating table #############
        my_tree = ttk.Treeview(past_orders_table)
        self.my_tree = my_tree
        my_tree['columns'] = ("menu_item", "item_price")

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
        my_tree.column("menu_item", anchor=CENTER, width=80, minwidth=25)
        my_tree.column("item_price", anchor=CENTER, width=80, minwidth=25)

        # defining  headings for table
        my_tree.heading("menu_item", text="Item", anchor=CENTER)
        my_tree.heading("item_price", text="Price", anchor=CENTER)

        my_tree.place(anchor='center', x=str(self.width * 0.15), y=str(0.5 * self.height))
        self.display_data()

        # Menu Item label & entry
        tk.Label(self, text="Item", font=(Constants.font, 12, 'bold'), fg="Black") \
            .place(anchor='e', x=str(self.width * 0.3), y=str(0.15 * self.height))
        self.item = tk.StringVar()
        self.table_entry = tk.Entry(self, font=(Constants.font, 16, 'bold'), bd=2, insertwidth=2, justify='left',
                                    textvariable=self.item, state="normal")
        self.table_entry.place(anchor='center', x=str(self.width * 0.35), y=str(0.19 * self.height))

        # Item Price label & entry
        tk.Label(self, text="Price", font=(Constants.font, 12, 'bold'), fg="Black") \
            .place(anchor='e', x=str(self.width * 0.5), y=str(0.15 * self.height))
        self.price = tk.StringVar()
        self.table_entry = tk.Entry(self, font=(Constants.font, 16, 'bold'), bd=2, insertwidth=2, justify='left',
                                    textvariable=self.price, state="normal")
        self.table_entry.place(anchor='center', x=str(self.width * 0.55), y=str(0.19 * self.height))

        # Add Tables Button
        self.btn_11 = tk.Button(self, text="Add", height=2, width=10, command=self.add_menu_item,
                                font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        self.btn_11.place(anchor='e', x=str(self.width * 0.35), y=str(0.30 * self.height))

        # Delete an item Button
        btn_2 = tk.Button(self, text="Remove\nItem", height=2, width=10, command=self.delete_item,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_2.place(anchor='center', x=str(self.width * 0.10), y=str(0.85 * self.height))

        # Delete the menu
        btn_3 = tk.Button(self, text="Delete\nMenu", height=2, width=10, command=self.delete_menu,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_3.place(anchor='center', x=str(self.width * 0.18), y=str(0.85 * self.height))

        # Back Button
        btn_1 = tk.Button(self, text="Back", height=2, width=10, command=self.back_to_home,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_1.place(anchor='center', x=str(self.width * 0.95), y=str(0.85 * self.height))

    def back_to_home(self):
        self.root.frame1.tkraise()

    def add_menu_item(self):
        self.item_result = test(self.item, "str")
        self.price_result = test(self.price, "float")
        if self.item_result and self.price_result:
            self.cur.execute('create table if not exists menu (itemID text, itemPrice integer)')
            self.cur.execute("insert into menu values (?, ?)", (self.item_result, self.price_result))
            self.root.db.commit()
            messagebox.showinfo("Message", "Stored successfully")
            self.update_table()
            self.item.set("")
            self.price.set("")

    def update_table(self):
        self.my_tree.delete(*self.my_tree.get_children())
        self.display_data()

    def display_data(self):
        try:
            menu_cursor = self.cur.execute("select * from menu")
            menu_fetch = menu_cursor.fetchall()
            for i in menu_fetch:
                self.my_tree.insert('', 'end', values=i)
        except sqlite3.OperationalError:
            pass

    def delete_item(self):
        if not self.my_tree.selection():
            messagebox.showwarning("Warning", "Select data to delete")
            return
        curItem = self.my_tree.focus()
        contents = self.my_tree.item(curItem)
        selecteditem = contents['values']
        self.my_tree.delete(curItem)
        self.cur.execute("delete from menu where itemID=:c", {"c": selecteditem[0]})
        self.root.db.commit()

    def delete_menu(self):
        result = messagebox.askquestion('Confirm', 'Are you sure you want to delete the menu?',
                                        icon="warning")
        if result == 'yes':
            self.cur.execute(F"delete from menu")
            self.root.db.commit()
            messagebox.showinfo("Message", "Menu has been deleted successfully !")
            self.update_table()


class WaiterConfigScreen(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.root = root
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.cur = self.root.db.cursor()

        tk.Label(self, text="Waiter Configuration", bg=Constants.background_color, fg="black", font=("Ubuntu", 20)) \
            .pack(pady=25, padx=25)

        # Tree
        style = ttk.Style()
        style.configure("Treeview", foreground="black", rowheight=40, fieldbackground="white")
        style.map('Treeview', background=[('selected', 'lightblue')])

        CENTER = 'center'

        past_orders_table = tk.Frame(self, width=400, height=700, bg=Constants.background_color)
        past_orders_table.place(anchor='center', x=str(self.width * 0.15), y=str(0.33 * self.height))
        ###########  Creating table #############
        my_tree = ttk.Treeview(past_orders_table)
        self.my_tree = my_tree
        my_tree['columns'] = ("waiter_id", "waiter_name", "waiter_status")

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
        my_tree.column("waiter_id", anchor=CENTER, width=80, minwidth=25)
        my_tree.column("waiter_name", anchor=CENTER, width=80, minwidth=25)
        my_tree.column("waiter_status", anchor=CENTER, width=80, minwidth=25)

        # defining  headings for table
        my_tree.heading("waiter_id", text="Waiter No", anchor=CENTER)
        my_tree.heading("waiter_name", text="Name", anchor=CENTER)
        my_tree.heading("waiter_status", text="Status", anchor=CENTER)

        my_tree.place(anchor='center', x=str(self.width * 0.15), y=str(0.5 * self.height))
        # self.update_table()

        tk.Label(self, text="Number of Waiters", font=(Constants.font, 12, 'bold'), fg="Black") \
            .place(anchor='e', x=str(self.width * 0.37), y=str(0.15 * self.height))
        self.waiters = tk.StringVar()
        self.waiters_entry = tk.Entry(self, font=(Constants.font, 16, 'bold'), bd=2, insertwidth=2, justify='left',
                                      textvariable=self.waiters, state="normal")
        self.waiters_entry.place(anchor='center', x=str(self.width * 0.35), y=str(0.19 * self.height))
        self.display_waiters()

        # Add Tables Button
        self.btn_11 = tk.Button(self, text="Add", height=2, width=10, command=self.add_waiters,
                                font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        self.btn_11.place(anchor='e', x=str(self.width * 0.35), y=str(0.30 * self.height))

        # Back Button
        btn_1 = tk.Button(self, text="Back", height=2, width=10, command=self.back_to_home,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_1.place(anchor='center', x=str(self.width * 0.95), y=str(0.85 * self.height))

        # Delete a waiter Button
        btn_2 = tk.Button(self, text="Remove\nWaiter", height=2, width=10, command=self.delete_one_waiter,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_2.place(anchor='center', x=str(self.width * 0.10), y=str(0.85 * self.height))

        # Delete all waiters Button
        btn_3 = tk.Button(self, text="Delete\nWaiters", height=2, width=10, command=self.delete_waiters,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_3.place(anchor='center', x=str(self.width * 0.18), y=str(0.85 * self.height))

    def back_to_home(self):
        self.root.frame1.tkraise()

    def add_waiters(self):
        self.result = test(self.waiters, "int")
        if self.result:
            self.waiters_entry["state"] = "disabled"
            self.btn_11["state"] = "disabled"
            self.cur.execute('create table if not exists waiter (waiterID integer, waiterName text, waiterStatus text)')
            for i in range(1, self.result + 1):
                self.cur.execute("insert into waiter values (?, ?, ?)", (i, F"waiter {i}", "Free"))
            self.root.db.commit()
            self.update_table()

    def display_waiters(self):
        try:
            waiters_cursor = self.cur.execute("select * from waiter")
            waiters_fetch = waiters_cursor.fetchall()
            for i in waiters_fetch:
                self.my_tree.insert('', 'end', values=i)
        except sqlite3.OperationalError:
            pass

    def delete_one_waiter(self):
        if not self.my_tree.selection():
            messagebox.showwarning("Warning", "Select data to delete")
            return
        curItem = self.my_tree.focus()
        contents = self.my_tree.item(curItem)
        selecteditem = contents['values']
        self.my_tree.delete(curItem)
        self.cur.execute("delete from waiter where waiterID=:c", {"c": selecteditem[0]})
        self.root.db.commit()

    def delete_waiters(self):
        result = messagebox.askquestion('Confirm', 'Are you sure you want to delete all the waiters?',
                                        icon="warning")
        if result == 'yes':
            self.cur.execute("delete from waiter")
            self.root.db.commit()
            messagebox.showinfo("Message", "All waiters have been deleted successfully !")
            self.waiters_entry["state"] = "normal"
            self.waiters.set("")
            self.btn_11["state"] = "normal"
            self.update_table()

    def update_table(self):
        self.my_tree.delete(*self.my_tree.get_children())
        self.display_waiters()


class TreeWidget(tk.Frame):
    def __init__(self, root, column1, column2, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.root = root
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.column1 = column1
        self.column2 = column2
        self.cur = self.root.db.cursor()
        # Tree
        style = ttk.Style()
        style.configure("Treeview", foreground="black", rowheight=40, fieldbackground="white")
        style.map('Treeview', background=[('selected', 'lightblue')])

        CENTER = 'center'

        past_orders_table = tk.Frame(self, width=400, height=700, bg=Constants.background_color)
        past_orders_table.place(anchor='center', x=str(self.width * 0.15), y=str(0.33 * self.height))
        ###########  Creating table #############
        my_tree = ttk.Treeview(past_orders_table)
        self.my_tree = my_tree
        my_tree['columns'] = (self.column1, self.column2)

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
        my_tree.column(self.column1, anchor=CENTER, width=80, minwidth=25)
        my_tree.column(self.column2, anchor=CENTER, width=80, minwidth=25)

        # defining  headings for table
        my_tree.heading(self.column1, text="Waiter No", anchor=CENTER)
        my_tree.heading(self.column2, text="Name", anchor=CENTER)

        my_tree.place(anchor='center', x=str(self.width * 0.15), y=str(0.5 * self.height))

        tk.Label(self, text="Number of Waiters", font=(Constants.font, 12, 'bold'), fg="Black") \
            .place(anchor='e', x=str(self.width * 0.37), y=str(0.15 * self.height))
        self.waiters = tk.StringVar()
        self.waiters_entry = tk.Entry(self, font=(Constants.font, 16, 'bold'), bd=2, insertwidth=2, justify='left',
                                      textvariable=self.waiters, state="normal")
        self.waiters_entry.place(anchor='center', x=str(self.width * 0.35), y=str(0.19 * self.height))


class NewOrderScreen(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.root = root
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.cur = self.root.db.cursor()
        self.cond = False
        self.cur.execute('create table if not exists orders (orderID integer, tableID integer,'
                         ' waiterID integer, state text)', )
        tk.Label(self, text="New Order", bg=Constants.background_color, fg="black", font=("Ubuntu", 20)) \
            .pack(pady=25, padx=25)

        # Table-Seat Tree
        style = ttk.Style()
        style.configure("Treeview", foreground="black", rowheight=40, fieldbackground="white")
        style.map('Treeview', background=[('selected', 'lightblue')])

        CENTER = 'center'

        self.table_seat_frame = tk.Frame(self, width=400, height=700, bg=Constants.background_color)
        self.table_seat_frame.place(anchor='center', x=str(self.width * 0.15), y=str(0.33 * self.height))
        ###########  Creating table #############
        self.table_seat_tree = ttk.Treeview(self.table_seat_frame)
        self.table_seat_tree['columns'] = ("table", "seat")

        ############ creating  for table ################
        horizontal_bar = ttk.Scrollbar(self.table_seat_frame, orient="horizontal")
        horizontal_bar.configure(command=self.table_seat_tree.xview)
        self.table_seat_tree.configure(xscrollcommand=horizontal_bar.set)
        # horizontal_bar.place(anchor='center',  x=str(width * 0.5), y=str(0.5 * height))

        vertical_bar = ttk.Scrollbar(self.table_seat_frame, orient="vertical")
        vertical_bar.configure(command=self.table_seat_tree.yview)
        self.table_seat_tree.configure(yscrollcommand=vertical_bar.set)
        # vertical_bar.place(anchor='center',  x=str(width * 0.5), y=str(0.5 * height))

        # defining columns for table
        self.table_seat_tree.column("#0", width=0, minwidth=0)
        self.table_seat_tree.column("table", anchor=CENTER, width=80, minwidth=25)
        self.table_seat_tree.column("seat", anchor=CENTER, width=80, minwidth=25)

        # defining  headings for table
        self.table_seat_tree.heading("table", text="Table", anchor=CENTER)
        self.table_seat_tree.heading("seat", text="Seat", anchor=CENTER)

        self.table_seat_tree.place(anchor='center', x=str(self.width * 0.15), y=str(0.5 * self.height))
        self.display_table_seats()

        # Menu Tree
        style = ttk.Style()
        style.configure("Treeview", foreground="black", rowheight=40, fieldbackground="white")
        style.map('Treeview', background=[('selected', 'lightblue')])

        CENTER = 'center'

        self.menu_frame = tk.Frame(self, width=180, height=400, bg=Constants.background_color)
        self.menu_frame.place(anchor='center', x=str(self.width * 0.36), y=str(0.63 * self.height))
        ###########  Creating table #############
        self.menu_tree = ttk.Treeview(self.menu_frame)
        self.menu_tree['columns'] = ("menu_item", "item_price")

        ############ creating  for table ################
        horizontal_bar = ttk.Scrollbar(self.menu_frame, orient="horizontal")
        horizontal_bar.configure(command=self.menu_tree.xview)
        self.menu_tree.configure(xscrollcommand=horizontal_bar.set)

        vertical_bar = ttk.Scrollbar(self.menu_frame, orient="vertical")
        vertical_bar.configure(command=self.menu_tree.yview)
        self.menu_tree.configure(yscrollcommand=vertical_bar.set)

        # defining columns for table
        self.menu_tree.column("#0", width=0, minwidth=0)
        self.menu_tree.column("menu_item", anchor=CENTER, width=80, minwidth=25)
        self.menu_tree.column("item_price", anchor=CENTER, width=80, minwidth=25)

        # defining  headings for table
        self.menu_tree.heading("menu_item", text="Item", anchor=CENTER)
        self.menu_tree.heading("item_price", text="Price", anchor=CENTER)

        self.menu_tree.place(anchor='center', x=str(self.width * 0.065), y=str(0.28 * self.height))

        # Item name label & entry
        tk.Label(self, text="Item", font=(Constants.font, 12, 'bold'), fg="Black") \
            .place(anchor='e', x=str(self.width * 0.3), y=str(0.15 * self.height))
        self.item = tk.StringVar()
        self.item_selection_entry = tk.Entry(self, font=(Constants.font, 16, 'bold'), bd=2, insertwidth=2,
                                             justify='left', textvariable=self.item, state="normal")
        self.item_selection_entry.place(anchor='center', x=str(self.width * 0.35), y=str(0.19 * self.height))

        # Add Item Button
        btn_11 = tk.Button(self, text="Add\nItem", height=2, width=10, command=self.add_seat_item,
                                font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_11.place(anchor='e', x=str(self.width * 0.35), y=str(0.30 * self.height))

        # Show Menu Button
        btn_12 = tk.Button(self, text="Show\nMenu", height=2, width=10, command=self.show_menu,
                                font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_12.place(anchor='e', x=str(self.width * 0.45), y=str(0.30 * self.height))

        # Back Button
        btn_1 = tk.Button(self, text="Back", height=2, width=10, command=self.back_to_home,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_1.place(anchor='center', x=str(self.width * 0.95), y=str(0.85 * self.height))

        # Tracking Table
        tk.Label(self, text="Table", font=(Constants.font, 12, 'bold'), fg="Black") \
            .place(anchor='center', x=str(self.width * 0.60 + 6), y=str(0.15 * self.height))

        self.tracked_table_var = tk.StringVar()
        self.tracked_table_entry = tk.Entry(self, font=(Constants.font, 16, 'bold'), bd=2, insertwidth=2,
                                            justify='left', textvariable=self.tracked_table_var, state="normal",
                                            width=10)
        self.tracked_table_entry.place(anchor='center', x=str(self.width * 0.67), y=str(0.15 * self.height))

        # Tracked Table Button
        self.btn_13 = tk.Button(self, text="Select", height=1, width=5, command=self.display_seat_item_state,
                                font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        self.btn_13.place(anchor='center', x=str(self.width * 0.74), y=str(0.15 * self.height))

        # Table - Order state
        self.show_seats_items()

        # Pending Orders List Box
        tk.Label(self, text="Pending Orders", font=(Constants.font, 12, 'bold'), fg="Black") \
            .place(anchor='center', x=str(self.width * 0.935), y=str(0.15 * self.height))
        self.order_listbox = tk.Listbox(self)
        self.order_listbox.place(anchor='center', x=str(self.width * 0.94), y=str(0.32 * self.height))
        self.display_list_box_data()

        # Waiter List
        self.show_waiters()
        # Assign Waiter Button
        self.btn_15 = tk.Button(self, text="Assign", height=1, width=5, command=self.assign_waiter,
                                font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        self.btn_15.place(anchor='center', x=str(self.width * 0.74), y=str(0.81 * self.height))

        # Refresh Button
        btn_14 = tk.Button(self, text="Refresh", height=2, width=10, command=self.update_list_box,
                           font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_14.place(anchor='center', x=str(self.width * 0.94), y=str(0.48 * self.height))

    def back_to_home(self):
        self.root.frame1.tkraise()

    def display_table_seats(self):
        try:
            table_seat_cursor = self.cur.execute("select distinct tableID , seatID from seat order by tableID asc")
            table_seat_fetch = table_seat_cursor.fetchall()
            for i in table_seat_fetch:
                self.table_seat_tree.insert('', 'end', values=i)
        except sqlite3.OperationalError:
            pass

    def add_seat_item(self):
        if not self.table_seat_tree.selection():
            messagebox.showwarning("Warning", "Select table to proceed")
            return
        curItem = self.table_seat_tree.focus()
        contents = (self.table_seat_tree.item(curItem))
        selecteditem = contents['values']
        table = selecteditem[0]
        seat = selecteditem[1]

        self.item_result = test(self.item, "str")
        if self.item_result:
            test2 = seat_item_test(self.cur, seat, self.item_result, table)
            if test2:
                self.cur.execute("insert into seat values (?, ?, ?, ?)", (seat, table, self.item_result, "pending"))
                self.cur.execute(F"delete from seat where tableID=? and seatID=? and itemID is null", (table, seat))
                self.root.db.commit()
                messagebox.showinfo("Message", "Stored successfully")
                self.item.set("")

    def show_menu(self):
        self.cond = not self.cond
        if self.cond:
            self.display_menu()
        else:
            self.menu_tree.delete(*self.menu_tree.get_children())

    def display_menu(self):
        try:
            menu_cursor = self.cur.execute("select * from menu")
            menu_fetch = menu_cursor.fetchall()
            for i in menu_fetch:
                self.menu_tree.insert('', 'end', values=i)
        except sqlite3.OperationalError:
            pass

    def show_seats_items(self):
        # Tree
        style = ttk.Style()
        style.configure("Treeview", foreground="black", rowheight=40, fieldbackground="white")
        style.map('Treeview', background=[('selected', 'lightblue')])

        CENTER = 'center'
        tracking_frame = tk.Frame(self, width=250, height=200, bg=Constants.background_color)
        tracking_frame.place(anchor='center', x=str(self.width * 0.68), y=str(0.35 * self.height))
        ###########  Creating table #############
        self.tracked_tree = ttk.Treeview(tracking_frame)
        self.tracked_tree['columns'] = ("seat", "item", "state")

        ############ creating  for table ################
        horizontal_bar = ttk.Scrollbar(tracking_frame, orient="horizontal")
        horizontal_bar.configure(command=self.tracked_tree.xview)
        self.tracked_tree.configure(xscrollcommand=horizontal_bar.set)
        # horizontal_bar.place(anchor='center',  x=str(width * 0.5), y=str(0.5 * height))

        vertical_bar = ttk.Scrollbar(tracking_frame, orient="vertical")
        vertical_bar.configure(command=self.tracked_tree.yview)
        self.tracked_tree.configure(yscrollcommand=vertical_bar.set)
        # vertical_bar.place(anchor='center',  x=str(width * 0.5), y=str(0.5 * height))

        # defining columns for table
        self.tracked_tree.column("#0", width=0, minwidth=0)
        self.tracked_tree.column("seat", anchor=CENTER, width=80, minwidth=25)
        self.tracked_tree.column("item", anchor=CENTER, width=80, minwidth=25)
        self.tracked_tree.column("state", anchor=CENTER, width=80, minwidth=25)

        # defining  headings for table
        self.tracked_tree.heading("seat", text="Seat", anchor=CENTER)
        self.tracked_tree.heading("item", text="Item", anchor=CENTER)
        self.tracked_tree.heading("state", text="State", anchor=CENTER)

        self.tracked_tree.place(anchor='center', x=str(self.width * 0.09), y=str(0.25 * self.height))

    def display_seat_item_state(self):
        self.tracked_table_result = test(self.tracked_table_var, "int")
        if self.tracked_table_result:
            test2 = tracked_table_test(self.cur, self.tracked_table_result)
            if test2:
                self.tracked_tree.delete(*self.tracked_tree.get_children())
                tracked_table_cursor = self.cur.execute("select seatID , itemID , state from seat where tableID=:c",
                                                        {"c": self.tracked_table_result})
                tracked_table_fetch = tracked_table_cursor.fetchall()
                for i in tracked_table_fetch:
                    self.tracked_tree.insert('', 'end', values=i)

    def display_list_box_data(self):
        pending_orders_cursor = self.cur.execute("select orderID , tableID from orders where state=:c",
                                                 {"c": "in_progress"})
        pending_orders_fetch = pending_orders_cursor.fetchall()
        for i in pending_orders_fetch:
            self.order_listbox.insert(tk.END, F"Table {i[0]} - Order {i[1]}")

    def update_list_box(self):
        self.order_listbox.delete(0, tk.END)
        self.display_list_box_data()
        self.waiters_tree.delete(*self.waiters_tree.get_children())
        self.display_waiters()
        self.table_seat_tree.delete(*self.table_seat_tree.get_children())
        self.display_table_seats()

    def show_waiters(self):
        # Tree
        style = ttk.Style()
        style.configure("Treeview", foreground="black", rowheight=40, fieldbackground="white",)
        style.map('Treeview', background=[('selected', 'lightblue')])

        CENTER = 'center'

        waiters_frame = tk.Frame(self, width=250, height=215, bg=Constants.background_color)
        waiters_frame.place(anchor='center', x=str(self.width * 0.68), y=str(0.64 * self.height))
        ###########  Creating table #############
        self.waiters_tree = ttk.Treeview(waiters_frame)
        self.waiters_tree['columns'] = ("waiter_id", "waiter_name", "waiter_state")

        ############ creating  for table ################
        horizontal_bar = ttk.Scrollbar(waiters_frame, orient="horizontal")
        horizontal_bar.configure(command=self.waiters_tree.xview)
        self.waiters_tree.configure(xscrollcommand=horizontal_bar.set)
        # horizontal_bar.place(anchor='center',  x=str(width * 0.5), y=str(0.5 * height))

        vertical_bar = ttk.Scrollbar(waiters_frame, orient="vertical")
        vertical_bar.configure(command=self.waiters_tree.yview)
        self.waiters_tree.configure(yscrollcommand=vertical_bar.set)
        # vertical_bar.place(anchor='center',  x=str(width * 0.5), y=str(0.5 * height))

        # defining columns for table
        self.waiters_tree.column("#0", width=0, minwidth=0)
        self.waiters_tree.column("waiter_id", anchor=CENTER, width=80, minwidth=25)
        self.waiters_tree.column("waiter_name", anchor=CENTER, width=80, minwidth=25)
        self.waiters_tree.column("waiter_state", anchor=CENTER, width=80, minwidth=25)

        # defining  headings for table
        self.waiters_tree.heading("waiter_id", text="Waiter No", anchor=CENTER)
        self.waiters_tree.heading("waiter_name", text="Name", anchor=CENTER)
        self.waiters_tree.heading("waiter_state", text="State", anchor=CENTER)

        self.waiters_tree.place(anchor='center', x=str(self.width * 0.09), y=str(0.28 * self.height))
        self.display_waiters()

    def display_waiters(self):
        try:
            waiter_cursor = self.cur.execute("select * from waiter where waiterStatus=:c", {"c": "Free"})
            waiter_fetch = waiter_cursor.fetchall()
            for i in waiter_fetch:
                self.waiters_tree.insert('', 'end', values=i)
        except sqlite3.OperationalError as e:
            messagebox.showwarning("Warning", F"{e}")

    def assign_waiter(self):

        if not self.waiters_tree.selection():
            messagebox.showwarning("Warning", "Select a waiter to proceed")
            return

        curItem = self.waiters_tree.focus()
        contents = (self.waiters_tree.item(curItem))
        selecteditem = contents['values']
        waiterID = selecteditem[0]
        try:
            self.cur.execute("insert into orders values (?, ?, ?, ?)", (self.tracked_table_result,
                                                                        self.tracked_table_result, waiterID,
                                                                        "in_progress"))
            self.cur.execute("update waiter set waiterStatus=? where waiterID=?", ("Busy", waiterID))
            self.cur.execute(F"update restaurant_tables set orderID=? where tableID=?", (self.tracked_table_result,
                                                                                         self.tracked_table_result))
            self.root.db.commit()
            messagebox.showinfo("Message", "Order has been assigned successfully !")
        except AttributeError:
            messagebox.showwarning("Warning", "define a table above")
        self.waiters_tree.delete(*self.waiters_tree.get_children())
        self.display_waiters()


class InProgressOrdersScreen(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.root = root
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.cur = self.root.db.cursor()

        tk.Label(self, text="In-Progress Orders", bg=Constants.background_color, fg="black", font=("Ubuntu", 20)) \
            .pack(pady=25, padx=25)

        # Orders Tree
        self.orders_tree()
        self.display_order_tree_data()

        # Select Order Button
        btn_8 = tk.Button(self, text="Select\nOrder", height=2, width=10, command=self.select_order,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_8.place(anchor='center', x=str(self.width * 0.10), y=str(0.85 * self.height))

        # Refresh Button
        btn_14 = tk.Button(self, text="Refresh", height=2, width=10, command=self.update_list_box,
                           font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_14.place(anchor='center', x=str(self.width * 0.18), y=str(0.85 * self.height))

        # Chef Button
        btn_15 = tk.Button(self, text="Chef", height=2, width=10, command=self.chef,
                           font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_15.place(anchor='center', x=str(self.width * 0.33), y=str(0.85 * self.height))

        # Seat - Item - State Tree
        self.seat_item_state_tree()

        # Back Button
        btn_16 = tk.Button(self, text="Serve\nSeat", height=2, width=10, command=self.serve_seat,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_16.place(anchor='center', x=str(self.width * 0.95), y=str(0.75 * self.height))

        # Back Button
        btn_1 = tk.Button(self, text="Back", height=2, width=10, command=self.back_to_home,
                          font=(Constants.font, 12, 'bold'), bg=Constants.btn_color, fg="White")
        btn_1.place(anchor='center', x=str(self.width * 0.95), y=str(0.85 * self.height))

    def back_to_home(self):
        self.root.frame1.tkraise()

    def orders_tree(self):
        # Table-Seat Tree
        style = ttk.Style()
        style.configure("Treeview", foreground="black", rowheight=40, fieldbackground="white")
        style.map('Treeview', background=[('selected', 'lightblue')])

        CENTER = 'center'

        self.table_frame = tk.Frame(self, width=100, height=400, bg=Constants.background_color)
        self.table_frame.place(anchor='center', x=str(self.width * 0.15), y=str(0.35  * self.height))
        ###########  Creating table #############
        self.table_tree = ttk.Treeview(self.table_frame)
        self.table_tree['columns'] = ("table")

        ############ creating  for table ################
        horizontal_bar = ttk.Scrollbar(self.table_frame, orient="horizontal")
        horizontal_bar.configure(command=self.table_tree.xview)
        self.table_tree.configure(xscrollcommand=horizontal_bar.set)
        # horizontal_bar.place(anchor='center',  x=str(width * 0.5), y=str(0.5 * height))

        vertical_bar = ttk.Scrollbar(self.table_frame, orient="vertical")
        vertical_bar.configure(command=self.table_tree.yview)
        self.table_tree.configure(yscrollcommand=vertical_bar.set)
        # vertical_bar.place(anchor='center',  x=str(width * 0.5), y=str(0.5 * height))

        # defining columns for table
        self.table_tree.column("#0", width=0, minwidth=0)
        self.table_tree.column("table", anchor=CENTER, width=80, minwidth=25)

        # defining  headings for table
        self.table_tree.heading("table", text="Table", anchor=CENTER)

        self.table_tree.place(anchor='center', x=str(self.width * 0.04), y=str(0.25 * self.height))

    def display_order_tree_data(self):
        orders_cursor = self.cur.execute("select tableID from orders where state=:c",
                                         {"c": "in_progress"})
        orders_fetch = orders_cursor.fetchall()
        for i in orders_fetch:
            self.table_tree.insert('', 'end', values=i)

    def update_list_box(self):
        self.table_tree.delete(*self.table_tree.get_children())
        self.display_order_tree_data()

    def select_order(self):
        if not self.table_tree.selection():
            messagebox.showwarning("Warning", "Select table to proceed")
            return
        curItem = self.table_tree.focus()
        contents = (self.table_tree.item(curItem))
        self.selected_table = contents['values']
        self.in_progress_tree.delete(*self.in_progress_tree.get_children())
        in_progress_cursor = self.cur.execute("select seatID , itemID , state from seat where tableID=?",
                                              self.selected_table)
        in_progress_fetch = in_progress_cursor.fetchall()
        for i in in_progress_fetch:
            self.in_progress_tree.insert('', 'end', values=i)

    def seat_item_state_tree(self):
        # Table-Seat Tree
        style = ttk.Style()
        style.configure("Treeview", foreground="black", rowheight=35, fieldbackground="white")
        style.map('Treeview', background=[('selected', 'lightblue')])

        CENTER = 'center'

        self.in_progress_frame = tk.Frame(self, width=300, height=400, bg=Constants.background_color)
        self.in_progress_frame.place(anchor='center', x=str(self.width * 0.35), y=str(0.35 * self.height))
        ###########  Creating table #############
        self.in_progress_tree = ttk.Treeview(self.in_progress_frame)
        self.in_progress_tree['columns'] = ("seat", "item", "state")

        ############ creating  for table ################
        horizontal_bar = ttk.Scrollbar(self.in_progress_frame, orient="horizontal")
        horizontal_bar.configure(command=self.in_progress_tree.xview)
        self.in_progress_tree.configure(xscrollcommand=horizontal_bar.set)
        # horizontal_bar.place(anchor='center',  x=str(width * 0.5), y=str(0.5 * height))

        vertical_bar = ttk.Scrollbar(self.in_progress_frame, orient="vertical")
        vertical_bar.configure(command=self.in_progress_tree.yview)
        self.in_progress_tree.configure(yscrollcommand=vertical_bar.set)
        # vertical_bar.place(anchor='center',  x=str(width * 0.5), y=str(0.5 * height))

        # defining columns for table
        self.in_progress_tree.column("#0", width=0, minwidth=0)
        self.in_progress_tree.column("seat", anchor=CENTER, width=80, minwidth=25)
        self.in_progress_tree.column("item", anchor=CENTER, width=80, minwidth=25)
        self.in_progress_tree.column("state", anchor=CENTER, width=80, minwidth=25)

        # defining  headings for table
        self.in_progress_tree.heading("seat", text="Seat", anchor=CENTER)
        self.in_progress_tree.heading("item", text="Item", anchor=CENTER)
        self.in_progress_tree.heading("state", text="State", anchor=CENTER)

        self.in_progress_tree.place(anchor='center', x=str(self.width * 0.10), y=str(0.25 * self.height))

    def chef(self):
        if not self.in_progress_tree.selection():
            messagebox.showwarning("Warning", "Select seat to proceed")
            return
        curItem = self.in_progress_tree.focus()
        contents = (self.in_progress_tree.item(curItem))
        selecteditem = contents['values']
        seat = selecteditem[0]
        item = selecteditem[1]
        self.cur.execute("update seat set state=? where tableID=? and seatID=? and itemID=?",
                         ('Ready', self.selected_table[0], seat, item))
        self.root.db.commit()
        messagebox.showinfo("Message", F"{item} for seat {seat} is Ready !")

    def serve_seat(self):
        if not self.in_progress_tree.selection():
            messagebox.showwarning("Warning", "Select seat to proceed")
            return
        curItem = self.in_progress_tree.focus()
        contents = (self.in_progress_tree.item(curItem))
        selecteditem = contents['values']
        seat = selecteditem[0]
        item = selecteditem[1]
        self.cur.execute("update seat set state=? where tableID=? and seatID=? and itemID=?",
                         ('Served', self.selected_table[0], seat, item))
        messagebox.showinfo("Message", F"Seat {seat} has been served !")

        seat_check_cursor = self.cur.execute("select * from seat where tableID=:c", {"c": self.selected_table[0]})
        seat_check_fetch = seat_check_cursor.fetchall()
        for i in seat_check_fetch:
            if i[3] != "Served" or not i[3]:
                return
        self.cur.execute("update orders set state=:a where tableID=:b", {"a": 'Completed', "b": self.selected_table[0]})

        complete_order_cursor = self.cur.execute("select * from orders where state=? and tableID=?",
                                                 ("Completed", self.selected_table[0]))
        complete_order_fetch = complete_order_cursor.fetchone()
        waiter = complete_order_fetch[2]
        self.cur.execute("update waiter set waiterStatus=? where waiterID=?", ("Free", waiter))
        self.root.db.commit()
        self.in_progress_tree.delete(*self.in_progress_tree.get_children())


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
        self.frame2 = MenuConfigScreen(self, width=width, height=height, bg=Constants.background_color)
        self.frame3 = RestaurantConfigScreen(self, width=width, height=height, bg=Constants.background_color)
        self.frame4 = PastOrdersScreen(self, width=width, height=height, bg=Constants.background_color)
        self.frame5 = WaiterConfigScreen(self, width=width, height=height, bg=Constants.background_color)
        self.frame6 = NewOrderScreen(self, width=width, height=height, bg=Constants.background_color)
        self.frame7 = InProgressOrdersScreen(self, width=width, height=height, bg=Constants.background_color)

        # place frame widgets in window
        for frame in (self.frame1, self.frame2, self.frame3, self.frame4, self.frame5, self.frame6, self.frame7):
            frame.grid(row=0, column=0, sticky="nesw")

        self.frame1.tkraise()


def test_data(db):
    cur = db.cursor()
    delete_tables(cur)
    inptdata = input_data()
    waiter = 2
    table = 3

    initialization(cur, inptdata)

    order_mode(cur, waiter)

    cooking(cur, table)

    served_customer(cur, table, waiter)

    db.commit()


def main():
    """You can run the program with run console by uncommenting the test_data(db) line.
     Using the run console, you should insert at least 3 tables and you should insert 'water' at least to generate
     correct resutls"""

    db = sqlite3.connect('restaurant.db')
    # test_data(db)
    root = RootWindow(db)
    root.mainloop()
    db.close()

if __name__ == '__main__':
    main()
