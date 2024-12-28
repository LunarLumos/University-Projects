```yaml
# Delicious Eats Food Delivery Management System

## Overview 📚
description: |
  The Delicious Eats Food Delivery Management System is designed to automate the operations of a restaurant. It includes an admin interface for managing dishes and orders, as well as a customer interface for placing and managing orders. The system helps in reducing manual work and improving the efficiency of food delivery services.

project:
  course: "CIS 122 & 122L - Structured Programming with Lab"
  semester: "Fall 2024"
  assignment_title: "Delicious Eats Food Delivery Management System"
  author:
    name: "LunarLumos"
    github: "https://github.com/LunarLumos"
    email: "lunar.lumos@example.com"

---

## Features ⚙️

### Admin Features 🔑
admin:
  - **Add New Dish**: Add a new dish to the menu with details like ID, name, description, price, and preparation time.
  - **Modify Dish**: Update the details of an existing dish based on its Dish ID.
  - **Delete Dish**: Remove a dish from the menu.
  - **View All Dishes**: View all dishes currently available in the system.
  - **Search for Dishes**: Search for dishes by name.
  - **Sales Report**: Generate a sales report showing the total sales from all orders.

### Customer Features 🛍️
customer:
  - **View Dishes**: Customers can browse the available dishes.
  - **Place Order**: Customers can place an order by selecting the dish and quantity.
  - **Cancel Order**: Customers can cancel an order by providing the order ID.
  - **View Orders**: Customers can view the status of their placed orders.
  - **Search for Dishes**: Customers can search dishes by name or description.

---

## Menu Structure 📜

### Admin Menu 🔑
```bash
Admin Menu:
1. View All Dishes
2. Add New Dish
3. Modify Dish
4. Delete Dish
5. Search for Dishes
6. Sales Report
7. Exit
Enter your choice:
```

### Customer Menu 🛍️
```bash
Customer Menu:
1. View All Dishes
2. Place Order
3. Cancel Order
4. View All Orders
5. Search for Dishes
6. Exit
Enter your choice:
```

---

## Sales Report Example 📈
```bash
Sales Report:
Order ID: O4 | Dish: Wine | Quantity: 2 | Total: 2000 tk
Order ID: O5 | Dish: Milk | Quantity: 8 | Total: 480 tk
------------------------------------------------
Total Sales: 2960 tk
```

---

## Example Usage 🎥

1. **Placing an Order (Customer)** 🛒:
```bash
Enter your name: John Doe
Enter your address: 123 Street, City
Enter your contact number: 1234567890
Available Dishes:
Dish ID: 1 | Name: Pizza | Price: 500 tk | Time: 20 min | Description: Delicious Cheese Pizza
Dish ID: 2 | Name: Pasta | Price: 300 tk | Time: 15 min | Description: Creamy Pasta

Enter Dish ID to order: 1
Enter quantity: 2

Your Order ID is: O101
Order placed successfully!
```

---

## How to Run 🏃‍♂️

### Step 1: Clone the Repository
```bash
git clone https://github.com/LunarLumos/Delicious_Eats_Management_System.git
```

### Step 2: Navigate to the Project Directory
```bash
cd Delicious_Eats_Management_System
```

### Step 3: Compile the Code
```bash
gcc -o food_delivery_system main.c
```

### Step 4: Run the Program
```bash
./food_delivery_system
```

---

## License ⚖️

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact ✨

**Author**: [LunarLumos](https://github.com/LunarLumos)  
Email: **lunar.lumos@example.com**

---

## Conclusion 🚀

The **Delicious Eats Food Delivery Management System** is a complete terminal-based solution to manage restaurant orders and dish details. It helps both **Admins** and **Customers** interact with the restaurant system in an easy and efficient way. With this system, Amina successfully automated the entire food delivery management process for the **Delicious Eats** restaurant.

---

```
