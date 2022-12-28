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

    def check(self):
        """This method check if there is a saved configuration in the database
        :return True if there is data
        :return False if there is no data"""

    def write_configuration(self):
        """Write restaurant configuration in the database"""
        if self.check():
            print("You already have data in database")
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
        for i in range(1, self.number +1):
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



def main():
    table = int(input("Insert the number of tables: "))
    seats = [0]*table
    for i in range(table):
        seats[i] = int(input(F"Insert the number of seats in table {i+1}: "))
    res = RestaurantConfiguration(table, seats)
    res.dic()
    # print(F"Number of tables is {res.tables}. Number of seats are as follows {res.seats}")
    print(res.data)
    menu = MenuConfiguration().menu_config()
    print(F"List of menu items: {menu}")
    waiter = Waiters(5)
    print(F"The list of waiters is: {waiter.creating_waiters()}")



if __name__ == '__main__':
    main()
