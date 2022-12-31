import sqlite3

class RestaurantConfiguration:
    def __init__(self, tables, seats):
        """Arguments: tables is the number of tables, seats is the number of seats per table"""
        self.tables = tables
        self.seats = seats
        self.data = {}

    def dic(self):
        """This method combines the tables with their corresponding number of seats"""
        for i in range(1, self.tables+1):
            self.data[i] = self.data.get(i, self.seats[i-1])

    # def check(self):
    #     """This method check if there is a saved configuration in the database
    #     :return True if there is data
    #     :return False if there is no data"""

    def write_configuration(self):
        """Write restaurant configuration in the database"""
        # if self.check():
        #     print("You already have data in database")
        db = sqlite3.connect('restaurant.db')
        db.execute('create table if not exists configuration (tables integer, seats integer)')

class MenuConfiguration:
    def __init__(self,
                 # itemname, itemprice
                 ):
        """Arguments: itemname is the name of an item in the menu, item price is the price of this item"""
        # self.itemname = itemname
        # self.itemprice = itemprice
        self.menu = {}

    def menu_config(self):
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



class Order:
    def __init__(self, table, items):
        """Arguments: """
        self.table = table
        self.items = items
        self.state = "pending"
        self.order = []

    def table_seats(self):
        """"""
        # while True:

def input_data():
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


def main():

    inptdata = input_data()

    db = sqlite3.connect('restaurant.db')

    cur = db.cursor()

    cur.execute('create table if not exists seat (seatID integer, tableID integer)')
    cur.execute("create table if not exists restaurant_tables (tableID integer, orderID integer)")

    for i, k in inptdata[0].data.items():
        for m in range(1, k+1):
            cur.executemany("insert into seat values (?, ?)", [(m, i)])
        cur.executemany("insert into restaurant_tables values (?, ?)", [(i, None)])

    for row in cur.execute("select * from seat"):
        print(row)
    print("****************************")
    for row in cur.execute("select * from restaurant_tables"):
        print(row)

    cur.execute('create table if not exists menu (itemID integer, itemPrice integer)')

    for i, k in inptdata[1].items():
        cur.executemany("insert into menu values (?, ?)", [(i, k)])
    print("****************************")
    for row in cur.execute("select * from menu"):
        print(row)

    cur.execute('create table if not exists waiter (waiterID integer, waiterName text, waiterStatus text)')

    for i, k in inptdata[2].items():
        cur.executemany("insert into waiter values (?, ?, ?)", [(i, k, "Free")])
    print("****************************")
    for row in cur.execute("select * from waiter"):
        print(row)

    # cur.execute('create table if not exists orders (orderID integer, tableID integer, waiterID integer, state text)')

    # ////////////// PLACE ORDER //////////////////

    cur.execute('create table if not exists seat_order (seatID integer, itemID integer, state text)')

    cur.execute("select *` from seat where tableID=:c", {"c": 3})
    selected_seat = cur.fetchall()
    print(selected_seat)
    # cur.execute("insert into seat_order (?, ?, ?)", [("select seatID from seat", "select itemID from menu", "pending")])

    # for i, k in waiters.items():
    #     cur.executemany("insert into waiter values (?, ?, ?)", [(i, k, "Free")])
    # print("****************************")
    # for row in cur.execute("select * from waiter"):
    #     print(row)

    # ////////////// DELETE TABLES ////////////////
    cur.execute("drop table seat")

    cur.execute("drop table menu")

    cur.execute("drop table restaurant_tables")

    cur.execute("drop table waiter")

    db.commit()

    db.close()


if __name__ == '__main__':
    main()
