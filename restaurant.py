import sqlite3
import tkinter as tk
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


def system():
    background_color = "#3A7FF6"
    btn_color = "#294D8B"
    width = 1366
    height = 768
    font = 'Calibri'
    root = tk.Tk()
    root.geometry(F"{width}x{height}")
    root.title("Restaurant Management System")

    canvas = tk.Canvas(root, width=width, height=height, bg=background_color)
    canvas.grid(columnspan=3, rowspan=3)
    title = tk.Label(root, text="Welcome to \n Restaurant Management System", font=(font, 25, 'bold'),
                     fg="White", bg="grey", anchor=tk.W)
    title.place(anchor='center', x=str(width / 2), y=str(0.1 * height))

    # Restaurant Configuration Button
    btn_1_label = tk.StringVar(value="Restaurant Configuration")
    btn_1 = tk.Button(root, textvariable=btn_1_label, height=2, width=25, command=lambda: configure_restaurant(),
                      font=(font, 12, 'bold'), bg=btn_color, fg="White")
    btn_1.place(anchor='center', x=str(width / 2), y=str(0.25 * height))

    # Menu Configuration Button
    btn_2_label = tk.StringVar(value="Menu Configuration")
    btn_2 = tk.Button(root, textvariable=btn_2_label, height=2, width=25, command=lambda: configure_menu(),
                      font=(font, 12, 'bold'), bg=btn_color, fg="White")
    btn_2.place(anchor='center', x=str(width / 2), y=str(0.35 * height))

    # Waiter Configuration Button
    btn_3_label = tk.StringVar(value="Waiters Configuration")
    btn_3 = tk.Button(root, textvariable=btn_3_label, height=2, width=25, command=lambda: configure_waiters(),
                      font=(font, 12, 'bold'), bg=btn_color, fg="White")
    btn_3.place(anchor='center', x=str(width / 2), y=str(0.45 * height))

    # Past Orders Button
    btn_4_label = tk.StringVar(value="Past\nOrders")
    btn_4 = tk.Button(root, textvariable=btn_4_label, height=2, width=10, command=lambda: past_orders(),
                      font=(font, 12, 'bold'), bg=btn_color, fg="White")
    btn_4.place(anchor='center', x=str(width*0.95), y=str(0.85 * height))

    # In-Progress Orders Button
    btn_5_label = tk.StringVar(value="In-Progress\nOrders")
    btn_5 = tk.Button(root, textvariable=btn_5_label, height=2, width=10, command=lambda: in_progress_orders2(),
                      font=(font, 12, 'bold'), bg=btn_color, fg="White")
    btn_5.place(anchor='center', x=str(width * 0.88), y=str(0.85 * height))

    # New Orders Button
    btn_6_label = tk.StringVar(value="+ New Order")
    btn_6 = tk.Button(root, textvariable=btn_6_label, height=2, width=10, command=lambda: in_progress_orders2(),
                      font=(font, 12, 'bold'), bg=btn_color, fg="White")
    btn_6.place(anchor='center', x=str(width * 0.05), y=str(0.85 * height))

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


def main():
    system()

    # inptdata = input_data()
    #
    # db = sqlite3.connect('restaurant.db')
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
