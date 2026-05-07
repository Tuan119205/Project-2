import pyodbc

# =========================
# CONNECT SQL SERVER
# =========================

conn = pyodbc.connect(
    "DRIVER={SQL Server};"
    "SERVER=DESKTOP-8FG65QA\\SQLEXPRESS;"
    "DATABASE=BankingSystem;"
    "Trusted_Connection=yes;"
)

cursor = conn.cursor()

# =========================
# CREATE ACCOUNT
# =========================

def create_account():

    owner = input("Owner name = ")
    balance = float(input("Balance = "))

    cursor.execute(
        """
        INSERT INTO accounts(owner, balance)
        VALUES (?, ?)
        """,
        (owner, balance)
    )

    conn.commit()

    print("Account created successfully")


# =========================
# DEPOSIT
# =========================

def deposit():

    account_id = int(input("Account ID = "))
    amount = float(input("Deposit Amount = "))

    cursor.execute(
        """
        SELECT * FROM accounts
        WHERE id = ?
        """,
        (account_id,)
    )

    account = cursor.fetchone()

    if not account:
        print("Account not found")
        return

    cursor.execute(
        """
        UPDATE accounts
        SET balance = balance + ?
        WHERE id = ?
        """,
        (amount, account_id)
    )

    conn.commit()

    print("Deposit successful")


# =========================
# WITHDRAW
# =========================

def withdraw():

    account_id = int(input("Account ID = "))
    amount = float(input("Withdrawal Amount = "))

    cursor.execute(
        """
        SELECT balance FROM accounts
        WHERE id = ?
        """,
        (account_id,)
    )

    account = cursor.fetchone()

    if not account:
        print("Account not found")
        return

    current_balance = account[0]

    if current_balance < amount:
        print("Insufficient funds")
        return

    cursor.execute(
        """
        UPDATE accounts
        SET balance = balance - ?
        WHERE id = ?
        """,
        (amount, account_id)
    )

    conn.commit()

    print("Withdrawal successful")


# =========================
# TRANSFER MONEY
# =========================

def transfer_money():

    from_account = int(input("From Account ID = "))
    to_account = int(input("To Account ID = "))
    amount = float(input("Transfer Amount = "))

    try:

        # BEGIN TRANSACTION
        conn.autocommit = False

        # kiểm tra sender
        cursor.execute(
            """
            SELECT balance FROM accounts
            WHERE id = ?
            """,
            (from_account,)
        )

        sender = cursor.fetchone()

        if not sender:
            raise Exception("Sender account not found")

        # kiểm tra receiver
        cursor.execute(
            """
            SELECT balance FROM accounts
            WHERE id = ?
            """,
            (to_account,)
        )

        receiver = cursor.fetchone()

        if not receiver:
            raise Exception("Receiver account not found")

        sender_balance = sender[0]

        # kiểm tra tiền
        if sender_balance < amount:
            raise Exception("Insufficient funds")

        # trừ tiền
        cursor.execute(
            """
            UPDATE accounts
            SET balance = balance - ?
            WHERE id = ?
            """,
            (amount, from_account)
        )

        # cộng tiền
        cursor.execute(
            """
            UPDATE accounts
            SET balance = balance + ?
            WHERE id = ?
            """,
            (amount, to_account)
        )

        # lưu history
        cursor.execute(
            """
            INSERT INTO transaction_history
            (from_account, to_account, amount)
            VALUES (?, ?, ?)
            """,
            (from_account, to_account, amount)
        )

        # COMMIT
        conn.commit()

        print("Transfer successful")

    except Exception as e:

        # ROLLBACK
        conn.rollback()

        print("Transfer failed")
        print("Reason:", e)

    finally:

        conn.autocommit = True


# =========================
# TRANSACTION HISTORY
# =========================

def transaction_history():

    cursor.execute(
        """
        SELECT *
        FROM transaction_history
        ORDER BY created_at DESC
        """
    )

    rows = cursor.fetchall()

    print("\n=== TRANSACTION HISTORY ===")

    for row in rows:

        print(
            f"""
Transaction ID: {row[0]}
From Account : {row[1]}
To Account   : {row[2]}
Amount       : {row[3]}
Created At   : {row[4]}
-------------------------
"""
        )


# =========================
# SHOW ACCOUNTS
# =========================

def show_accounts():

    cursor.execute("SELECT * FROM accounts")

    rows = cursor.fetchall()

    print("\n=== ACCOUNTS ===")

    for row in rows:

        print(
            f"""
ID      : {row[0]}
Owner   : {row[1]}
Balance : {row[2]}
-------------------
"""
        )


# =========================
# MENU
# =========================

while True:

    print("""
===== MINI BANKING SYSTEM =====

1. Create account
2. Deposit
3. Withdraw
4. Transfer money
5. Transaction history
6. Show accounts
0. Exit
""")

    choice = input("Choose: ")

    if choice == "1":
        create_account()

    elif choice == "2":
        deposit()

    elif choice == "3":
        withdraw()

    elif choice == "4":
        transfer_money()

    elif choice == "5":
        transaction_history()

    elif choice == "6":
        show_accounts()

    elif choice == "0":
        print("Goodbye OK ")
        break

    else:
        print("Invalid choice")
