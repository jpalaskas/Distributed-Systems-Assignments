import sqlite3
import datetime
'''
Users Table consists of the following(as show in the query in the main):
id, name, entry_date, balance, withdrawal_limit (per day), last_withdraw_date
----------------------------------------------------------------------
The user can choose between Deposition, Withdrawal and checking hiw current 
balance. Also, he has the ability to delete his account.

'''
def create_connection(db_name):
    '''
    create a database connection to the SQLite database
        specified by the db_name given by the user.
    :param db_name: database name
    :return: Connection object or None(on failure)
    '''
    try:
        conn = sqlite3.connect(db_name + '.sqlite')
        print('Connected Successfully!!!')
        return conn
    except sqlite3.Error as e:
        print(e)
    
    return None

def create_table(conn, create_table_query):
    '''
    Create Users table if it does not already exists
    (table's existance is checked through another function)
    :param conn: Connection object
    :param create_table_query: the given query to create 
    the Users table if it does not already exist
    '''
    try:
        cur = conn.cursor()
        cur.execute(create_table_query)
    except sqlite3.Error as e:
        print('Error while creating table...')
        print(e)
    finally:
        cur.close()

def db_isempty(conn):
    '''
    Check if the database is empty
    :param conn: Connection Object
    :return: True or False if the executed query returns 
    at least one result or nothing
    '''
    try:
        cur = conn.cursor()
        cur.execute('''SELECT * FROM Users''')
        row = cur.fetchone()
        return row is None
    except sqlite3.Error as e:
        print(e)
    finally:
        cur.close()

def insert_values(conn):
    '''
    If the database is empty or the user wants to add this 
    function is called to add one or more users.
    :param conn: Connection Object
    '''
    try:
        cur = conn.cursor()
        print('Enter user values splitted by space in the following order')
        print('Name Balance Withdrawal_Limit')
        print('Enter "Exit" to stop inserting data.')
        user_values = input('Enter User Values...')
        while user_values!='Exit':
            splitted_uv = user_values.split()
            cur.execute('''INSERT INTO Users(name, entry_date, balance, 
            withdrawal_limit) VALUES (?, ?, ?, ?)''', (splitted_uv[0],
            datetime.datetime.now(), splitted_uv[1], splitted_uv[2]))
            user_values = input('Enter User Values (Again)...')
    except sqlite3.Error as e:
        print(e)
    finally: 
        conn.commit()
        print('Data committed.')
        cur.close()

def show_balance(conn, name):
    '''
    given the username this fucntion shows the id, name, current 
    balance of the user
    :param conn: Connection Object
    :param name: User name (string)
    '''
    try:
        cur = conn.cursor()
        cur.execute('''SELECT id, name, balance FROM Users WHERE name = ?'''
                , (name,))
        print(cur.fetchone())
    except sqlite3.Error as e:
        print(e)
    finally:
        cur.close()

def withdraw(conn, name):
    '''
    if the amount given for withdrawal satisfies the requirements
    it is withdraw.
    :param conn: Connection Object
    :param name: User name (string)
    '''
    try:
        cur = conn.cursor()
        cur.execute('''SELECT balance, withdrawal_limit FROM Users
                WHERE name = ?''', (name,))
        query_res = cur.fetchone()
        balance = query_res[0]
        withdrawal_limit = query_res[1]
        while True:
            x = input('Please enter the amount for withdrawal - ')
            amount = int(x)
            if amount>0:
                if amount%20==0 or amount%50==0 or (amount%50)%20==0:
                    if amount<balance:
                        if amount<=withdrawal_limit:
                            cur.execute('''UPDATE Users SET balance = balance - ? 
                                    WHERE name = ?''', (amount,name,))
                            cur.execute('''UPDATE Users SET withdrawal_limit = withdrawal_limit - ?
                                    WHERE name = ?''', (amount, name,))
                            cur.execute('''UPDATE Users SET last_withdraw_date = ? 
                                    WHERE name = ?''', (datetime.datetime.now(), name,))
                            break
                        else: 
                            print('Amount cannot be greater than current balance.')  
                    else: 
                        print('Amount cannot be greater than current balance.')
                else:
                    print('Amount is not a multiple of 20 nor 50 nor both.')
            else:
                print('Amount must be a positive number. Please re-enter.')
    except sqlite3.Error as e:
        print(e)
    finally:
        conn.commit()
        print('Withdrawal Completed Successfully!!!')
        cur.close()

def deposit(conn, name):
    '''
    if the amount given for deposition satisfies the requirements
    it is deposited.
    :param conn: Connection Object
    :param name: User name (string)
    '''
    try:
        cur = conn.cursor()
        while True:
            amount = input('Enter the amount for deposit - ')
            if int(amount)>0: 
                if int(amount)%5==0: break
                else: print('Amount must be a multiple of 5. Please re-enter amount.')
            else: print('Amount must be a positive number. Please re-enter.')
        cur.execute('''UPDATE Users SET balance = balance + ? 
                WHERE name = ?''', (int(amount),name,))
    except sqlite3.Error as e:
        print(e)
    finally:
        conn.commit()
        print('Deposition completed successfully.')
        cur.close()

def reset_withdrawal_limit(conn):
    '''
    Upon execution this function is called to check whether the day 
    of the last withdrawal is the same as the day of the current execution.
    If the day is different, the withdrawal day limit for each user that fulfils
    the requirements is reseted back to default.
    :param conn: Connection Object
    '''
    current_date = datetime.datetime.now()
    splitted = str(current_date).split('-')
    current_month = splitted[1]
    current_day = splitted[2][:2]
    try:
        cur = conn.cursor()
        cur.execute('''SELECT name, last_withdraw_date FROM Users''')
        names = cur.fetchall()
        for name in names:
            if name[1]==None: continue
            x = str(name[1]).split('-')
            if x[1]==current_month and x[2][:2]==current_day: continue
            cur.execute('''UPDATE Users SET withdrawal_limit = 200
                        WHERE name = ?''', (name[0],))
    except sqlite3.Error as e:
        print(e)
    finally:
        conn.commit()
        print('Withdrawal day limits reseted.')
        cur.close()

def delete_user(conn, name):
    '''
    The user is deleted and (by logic) the current balance is returned 
    to the user to be deleted
    :param conn: Connection Object
    :param name: Username (string)
    '''
    try:
        cur = conn.cursor()
        cur.execute('''SELECT balance FROM Users WHERE name = ?''', (name,))
        balance = cur.fetchone()
        cur.execute('''DELETE FROM Users WHERE name = ?''', (name,))
    except sqlite3.Error as e:
        print(e)
    finally:
        conn.commit()
        print('User deleted successfully. Money withdraw upon deleting account:', balance)
        cur.close()

def main():
    db_name = input('Please enter the name of the database - ')
    #if len(db_name) < 1 : db_name = 'table' 
    
    create_table_query = ''' CREATE TABLE IF NOT EXISTS Users(
				        id integer PRIMARY KEY,
				        name text NOT NULL,
				        entry_date text,
			         	balance integer NOT NULL,
				        withdrawal_limit integer NOT NULL,
                        last_withdraw_date text);
		                '''
    
    conn = create_connection(db_name)
    
    while conn is None:
        print('Error while creating/connecting to the database.')
        print('Please retry entering the database name.')
        db_name = input('Enter name ---')
        conn = create_connection(db_name)
    
    create_table(conn, create_table_query)
    
    if db_isempty(conn): 
        print('Database is empty. Please insert some Values.')
        insert_values(conn)
    
    choice = input('Do you want to add more Users? (Answer - Y/N)')
    if choice=='Y': insert_values(conn)
    
    reset_withdrawal_limit(conn)

    username = input('Please enter your name - ')
    
    while True:    
        print('Actions Available: Deposit, Withdraw, Show Balance, Delete Account')
        action = input('Please enter the desired action - ')
        if action=='Deposit':
            deposit(conn, username)
        elif action=='Withdraw':
            withdraw(conn, username)
        elif action=='Show Balance':
            show_balance(conn, username)
        elif action=='Delete Account':
            delete_user(conn, username)
        else : print('No such action found. Please re-enter.')
        more = input('More actions?(Answer - Y/N)')
        if more == 'N': break

if __name__ == '__main__':
    main()