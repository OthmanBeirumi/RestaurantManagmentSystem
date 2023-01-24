# **The Restaurant Platform System**

The restaurant platform is a digital system that enable the management of the restaurant tasks. 
This platform is used by managers to organize the tables and the orders of the customers so 
they can get what they asked for without any mistakes. The proper organization can be 
achieved with this system where customers receive exactly what they ordered.
The platform is able to show the menu, the number of tables and the number of seats in each 
table.
The platform consists of five stages, occurring one after another.
1. Restaurant configuration. In this stage, the user defines the number of tables in the 
restaurant and the number of seats in each table.
2. Menu configuration. In this stage, the user can define a list of food and beverages 
associated with prices.
3. Order configuration. In this stage, the user can see the menu list and can place order 
consisting of the items in the menu. Once the order is completed, it is assigned to the 
waiter to inform the chef to start preparing the food.
4. Cooking process. The waiter can pick up the food from chef only if they are ready. Each 
item received by the customer is marked by “served”.
5. Billing process. The program in this stage can generate the bills for the tables only if all 
items has been delivered to the customers. The billing information includes all items 
placed in this table and their prices as well as the total.

These stages can be accessed at anytime and without any prior order only if there is data stored 
in the database.

### **Capabilities of the program**

The restaurant platform system will have the following modes:

**• Initialization mode**

The program allows the user to get access to this platform. The user must define tables and 
seats using the interface. Then the user defines the menu list by appending food and beverages 
with prices. The user also defines the waiters that will serve the customers later on. These 
preferences should be saved to the SQLite database.

**• Order mode**

The program allows the user to take orders from customers. The order is a collection of the 
items requested by the customer from the menu list. The program should be able to detect 
whether the item is available. Each item should be marked as “pending” until it is ready and 
delivered to the customer. Then it will be marked “Served”.

**• Retrieving mode**

All orders placed using the platform will be automatically stored in the database. The program 
is able to show completed orders and orders in progress. The program also shows the total for 
the completed orders as well as the items in each order.

**• Statistics Mode**

In the statistics mode, the completed orders in the database are loaded and analyzed once. The 
following statistics are displayed for those orders: most popular food, most popular beverage 
and their corresponding cumulative number.

The program will have GUI interface (graphical interface). When the program is started, a menu 
will be displayed and the user can choose from the above moods. Then, in each mood, the 
input from the mouse/keyboard is handled as need. Running the program requires “tkinter” 
package.