#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DISHES_FILE "dishes.txt"
#define ORDERS_FILE "orders.txt"
#define ADMIN_USERNAME "admin"
#define ADMIN_PASSWORD "password123"

// Function to check if an order exists by reading the orders file
int order_exists(const char *order_id) {
    char command[512];
    snprintf(command, sizeof(command), "grep -q '^%s,' %s", order_id, ORDERS_FILE);
    return system(command) == 0;
}

// Function to cancel an order
void cancel_order() {
    char order_id[20];
    printf("Enter the Order ID to cancel (e.g., O1, O2, O3):\n");
    scanf("%s", order_id);

    if (!order_exists(order_id)) {
        printf("Error: Order ID %s not found!\n", order_id);
        return;
    }

    char command[512];
    snprintf(command, sizeof(command), "sed -i 's/^%s,.*/%s,*,*,*,*,*,*,*,Canceled/' %s", order_id, order_id, ORDERS_FILE);
    system(command);
    printf("Order %s canceled successfully!\n", order_id);
}

// Function to display all orders
void display_orders() {
    printf("All Orders:\n");
    char command[512];
    snprintf(command, sizeof(command), "awk -F',' '{print \"Order ID: \"$1\" | Customer: \"$2\" | Dish: \"$6\" | Quantity: \"$7\" | Total: \"$8\" tk | Status: \"$9}' %s", ORDERS_FILE);
    system(command);
}

// Function to display all dishes with the required format
void display_dishes() {
    printf("All available dishes:\n");
    char command[512];
    snprintf(command, sizeof(command), "awk -F',' '{print \"Dish ID: \"$1\" | Name: \"$2\" | Price: \"$4\" tk | Time: \"$5\" min | Description: \"$3}' %s", DISHES_FILE);
    system(command);
}

// Function to search for dishes by name
void search_dishes() {
    char search_term[50];
    printf("Enter dish name to search for (part of name):\n");
    scanf(" %[^\n]s", search_term);

    char command[512];
    snprintf(command, sizeof(command), "grep -i '%s' %s | awk -F',' '{print \"Dish ID: \"$1\" | Name: \"$2\" | Price: \"$4\" tk | Time: \"$5\" min | Description: \"$3}'", search_term, DISHES_FILE);
    system(command);
}

// Function to add a new dish
void add_dish() {
    char dish_id[10], dish_name[50], dish_description[100], dish_price[10], dish_prep_time[10];
    printf("Enter Dish ID (e.g., 1, 2, 3):\n");
    scanf("%s", dish_id);
    printf("Enter Dish Name:\n");
    scanf(" %[^\n]s", dish_name);
    printf("Enter Dish Description:\n");
    scanf(" %[^\n]s", dish_description);
    printf("Enter Dish Price (in tk):\n");
    scanf("%s", dish_price);
    printf("Enter Dish Preparation Time (in minutes):\n");
    scanf("%s", dish_prep_time);
    
    char command[512];
    snprintf(command, sizeof(command), "echo \"%s,%s,%s,%s,%s\" >> %s", dish_id, dish_name, dish_description, dish_price, dish_prep_time, DISHES_FILE);
    system(command);

    printf("Dish '%s' added successfully!\n", dish_name);
}

// Function to update a dish
void update_dish() {
    char dish_id[10];
    printf("Enter the Dish ID to update (e.g., 1, 2, 3):\n");
    scanf("%s", dish_id);

    char command[512];
    snprintf(command, sizeof(command), "grep -q '^%s,' %s", dish_id, DISHES_FILE);
    if (system(command) != 0) {
        printf("Error: Dish not found!\n");
        return;
    }

    char new_dish_name[50], new_dish_description[100], new_dish_price[10], new_dish_prep_time[10];
    printf("Enter new Dish Name (or press Enter to keep the current):\n");
    scanf(" %[^\n]s", new_dish_name);
    printf("Enter new Dish Description (or press Enter to keep the current):\n");
    scanf(" %[^\n]s", new_dish_description);
    printf("Enter new Dish Price (or press Enter to keep the current):\n");
    scanf("%s", new_dish_price);
    printf("Enter new Dish Preparation Time (or press Enter to keep the current):\n");
    scanf("%s", new_dish_prep_time);

    snprintf(command, sizeof(command), "sed -i 's/^%s,.*/%s,%s,%s,%s,%s/' %s", dish_id, dish_id, new_dish_name, new_dish_description, new_dish_price, new_dish_prep_time, DISHES_FILE);
    system(command); 
    printf("Dish '%s' updated successfully!\n", dish_id);
}

// Function to delete a dish
void delete_dish() {
    char dish_id[10];
    printf("Enter the Dish ID to delete (e.g., 1, 2, 3):\n");
    scanf("%s", dish_id);

    char command[512];
    snprintf(command, sizeof(command), "grep -q '^%s,' %s", dish_id, DISHES_FILE);
    if (system(command) != 0) {
        printf("Error: Dish not found!\n");
        return;
    }

    snprintf(command, sizeof(command), "sed -i '/^%s,/d' %s", dish_id, DISHES_FILE);
    system(command);
    printf("Dish with ID %s deleted successfully!\n", dish_id);
}

void generate_sales_report() {
    printf("Sales Report:\n");
    printf("Order details:\n");
    char command[512];
    snprintf(command, sizeof(command),
             "awk -F, '{ print \"Order ID: \" $1 \" | Dish: \" $6 \" | Quantity: \" $7 \" | Total: \" $8 \" tk\"; total += $8 } END { print \"------------------------------------------------\"; print \"Total Sales: \" total \" tk\" }' %s", 
             ORDERS_FILE);

    system(command);
}

// Function to place an order
void place_order() {
    char customer_name[50], customer_address[100], customer_phone[20], dish_id[10], quantity[10];
    char dish_name[50], dish_price[10], command[512];
    int total_cost;

    printf("Enter your name:\n");
    scanf(" %[^\n]s", customer_name);
    printf("Enter your address:\n");
    scanf(" %[^\n]s", customer_address);
    printf("Enter your contact number:\n");
    scanf("%s", customer_phone);
    printf("Available Dishes:\n");
    system("awk -F',' '{print \"Dish ID: \"$1\" | Name: \"$2\" | Price: \"$4\" tk | Time: \"$5\" min | Description: \"$3}' dishes.txt");

    printf("Enter Dish ID to order (e.g., 1, 2, 3):\n");
    scanf("%s", dish_id);
    printf("Enter quantity:\n");
    scanf("%s", quantity);

    snprintf(command, sizeof(command), "grep '^%s,' %s | cut -d ',' -f2,4", dish_id, DISHES_FILE);
    FILE *fp = popen(command, "r");

    if (!fp) {
        printf("Error: Dish not found!\n");
        return;
    }

    fgets(command, sizeof(command), fp); 
    fclose(fp);


    sscanf(command, "%49[^,],%9s", dish_name, dish_price);

    total_cost = atoi(dish_price) * atoi(quantity);

    snprintf(command, sizeof(command), "wc -l < %s", ORDERS_FILE);
    fp = popen(command, "r");
    int order_count;
    fscanf(fp, "%d", &order_count);
    fclose(fp);

    snprintf(command, sizeof(command),
             "echo 'O%d,%s,%s,%s,%s,%s,%s,%d,Pending' >> %s",
             order_count + 1, customer_name, customer_address, customer_phone,
             dish_id, dish_name, quantity, total_cost, ORDERS_FILE);

    system(command);

    printf("Order placed successfully! Your Order ID is: O%d\n", order_count + 1);
}


// Admin Menu
void admin_menu() {
    while (1) {
        int choice;
        printf("Admin Menu:\n");
        printf("1. View All Dishes\n");
        printf("2. Add New Dish\n");
        printf("3. Update Dish\n");
        printf("4. Delete Dish\n");
        printf("5. Search for Dishes\n");
        printf("6. Sales Report\n");
        printf("7. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);

        switch (choice) {
            case 1: display_dishes(); break;
            case 2: add_dish(); break;
            case 3: update_dish(); break;
            case 4: delete_dish(); break;
            case 5: search_dishes(); break;
            case 6: generate_sales_report(); break;
            case 7: exit(0); break;
            default: printf("Invalid choice!\n"); break;
        }
    }
}

// Customer Menu
void customer_menu() {
    while (1) {
        int choice;
        printf("Customer Menu:\n");
        printf("1. View All Dishes\n");
        printf("2. Place Order\n");
        printf("3. Cancel Order\n");
        printf("4. View All Orders\n");
        printf("5. Search for Dishes\n");
        printf("6. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);

        switch (choice) {
            case 1: display_dishes(); break;
            case 2: place_order(); break;
            case 3: cancel_order(); break;
            case 4: display_orders(); break;
            case 5: search_dishes(); break;
            case 6: exit(0); break;
            default: printf("Invalid choice!\n"); break;
        }
    }
}

// Main
int main() {
    char user_type[20];
    printf("Welcome to Delicious Eats!\n");
    printf("Are you an Admin or Customer? (Enter 'admin' or 'customer'):\n");
    scanf("%s", user_type);

    if (strcmp(user_type, "admin") == 0) {
        char username[50], password[50];
        printf("Enter username:\n");
        scanf("%s", username);
        printf("Enter password:\n");
        scanf("%s", password);

        if (strcmp(username, ADMIN_USERNAME) == 0 && strcmp(password, ADMIN_PASSWORD) == 0) {
            printf("Authentication successful!\n");
            admin_menu();
        } else {
            printf("Invalid username or password!\n");
        }
    } else if (strcmp(user_type, "customer") == 0) {
        customer_menu();
    } else {
        printf("Invalid selection! Exiting...\n");
        exit(1);
    }

    return 0;
}
