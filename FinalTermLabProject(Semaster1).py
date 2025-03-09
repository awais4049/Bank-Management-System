def main():
    user_accounts = []

    def main_menu():
        print("Press 1 to Create a new account.")
        print("Press 2 to Login.")
        print("Press 3 to exit.")

        while True:
            button = input("Enter your choice (1/2/3): ")
            if button.isdigit() and 1 <= int(button) <= 3:
                break
            else:
                print("Wrong Input.")
        return button

    def create_account():
        while True:
            name = input("Enter your name: ")
            if name.isalpha():
                break
            else:
                print("Name should be only in letters")
                
                
        password = input("Enter password: ")
        password2 = input("Enter the password again: ")

        while password != password2 or len(password) < 8:
            if password != password2:
                print("Passwords do not match.")

            if len(password) < 8:
                print("Password length should be at least 8 characters.")

            password = input("Enter password: ")
            password2 = input("Enter the password again: ")

        initial_balance = float(input("Enter your initial amount: "))
        account = {"Name": name, "Password": password, "Initial Balance": initial_balance}
        user_accounts.append(account)

    def login_user():
        login_name = input("Enter your name: ")
        login_password = input("Enter password: ")

        for account in user_accounts:
            if login_name == account["Name"] and login_password == account["Password"]:
                print("Logged in.")
                return account["Initial Balance"]
        print("User not found.")
        return None

    def add_income(initial_balance):
        amount = float(input("Enter amount you want to add: "))
        initial_balance += amount
        print(f"Amount updated successfully. Your balance is now {initial_balance}")
        return initial_balance

    def add_expense(initial_balance):
        expense = float(input("Enter expense: "))
        initial_balance -= expense
        print(f"Amount updated successfully. Your balance is now {initial_balance}")
        return initial_balance

    def check_balance(initial_balance):
        print(f"Your current balance is: {initial_balance}")

    current_balance = 0

    while True:
        choice = main_menu()

        if choice == "1":
            create_account()
        elif choice == "2":
            current_balance = login_user()
            if current_balance:
                while True:
                    print("Logged-in Menu")
                    print("Press 4 to Add income.")
                    print("Press 5 to Add Expense.")
                    print("Press 6 to Check Balance.")
                    print("Press 7 to Log Out")

                    login_choice = input("Enter your choice (4/5/6/7): ")

                    if login_choice == "4":
                        current_balance = add_income(current_balance)
                    elif login_choice == "5":
                        current_balance = add_expense(current_balance)
                    elif login_choice == "6":
                        check_balance(current_balance)
                    elif login_choice == "7":
                        print("Logged Out.")
                        break
                    else:
                        print("Invalid choice. Please try again.")
                        
        elif choice == "3":
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")


main()