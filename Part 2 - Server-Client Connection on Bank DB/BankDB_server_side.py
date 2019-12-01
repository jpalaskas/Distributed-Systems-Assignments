#server side of the Bank Database
#first run python -m Pyro4.naming and afterwards
#run the server and the client programs
import sqlite3
import datetime
import Pyro4

'''
Users Table consists of the following(as show in the query in the main):
id, name, entry_date, balance, withdrawal_limit (per day), last_withdraw_date
----------------------------------------------------------------------
The user can choose between Deposition, Withdrawal and checking hiw current 
balance. Also, he has the ability to delete his account.

'''
#a password mechanism could be added

create_table_query = ''' CREATE TABLE IF NOT EXISTS Users(
                            id integer PRIMARY KEY,
                            name text NOT NULL,
                            entry_date text,
                            balance integer NOT NULL,
                            withdrawal_limit integer NOT NULL,
                            last_withdraw_date text);
                            '''

db_name = 'ready'

@Pyro4.expose
class BankDB(object):
    def __init__(self):
        self.create_connection()

        if self.db_isempty(): 
            self.insert_values()
        
        self.reset_withdrawal_limit()
        print('Object Initialized')

    def create_connection(self):
        '''
        create a database connection to the SQLite database
            specified by the db_name given by the user.
        :param db_name: database name
        :return: Connection object or None(on failure)
        '''
        try:
            self.conn = sqlite3.connect(db_name + '.sqlite')
            print('Connected Successfully!!!')
        except sqlite3.Error as e:
            print(e)

    def create_table(self, create_table_query):
        '''
        Create Users table if it does not already exists
        (table's existance is checked through another function)
        :param conn: Connection object
        :param create_table_query: the given query to create 
        the Users table if it does not already exist
        '''
        try:
            self.cur = self.conn.cursor()
            self.cur.execute(create_table_query)
        except sqlite3.Error as e:
            print('Error while creating table...')
            print(e)
        finally:
            self.cur.close()

    def db_isempty(self):
        '''
        Check if the database is empty
        :param conn: Connection Object
        :return: True or False if the executed query returns 
        at least one result or nothing
        '''
        try:
            self.cur = self.conn.cursor()
            self.cur.execute('''SELECT * FROM Users''')
            row = self.cur.fetchone()
            return row is None
        except sqlite3.Error as e:
            print(e)
        finally:
            self.cur.close()

    def user_indb(self, name):
        '''
        Check if the user exists in the database
        :param name: the user's username
        :return: True or False depending on the user's existance 
        in tha database
        '''
        try:
            self.cur = self.conn.cursor()
            self.cur.execute('''SELECT name FROM Users''')
            rows = self.cur.fetchall()
            for row in rows:
                if name in row:
                    return True
            return False
        except sqlite3.Error as e:
            print(e)
        finally:
            self.cur.close()

    def insert_values(self):
        '''
        If the database is empty or the user wants to add this 
        function is called to add one or more users.
        :param conn: Connection Object
        '''
        try:
            self.cur = self.conn.cursor()
            print('Enter user values splitted by space in the following order')
            print('Name Balance Withdrawal_Limit')
            print('Enter "Exit" to stop inserting data.')
            user_values = input('Enter User Values...')
            while user_values!='Exit':
                splitted_uv = user_values.split()
                self.cur.execute('''INSERT INTO Users(name, entry_date, balance, 
                withdrawal_limit) VALUES (?, ?, ?, ?)''', (splitted_uv[0],
                datetime.datetime.now(), splitted_uv[1], splitted_uv[2]))
                user_values = input('Enter User Values (Again)...')
        except sqlite3.Error as e:
            print(e)
        finally: 
            self.conn.commit()
            print('Data committed.')
            self.cur.close()

    def show_balance(self, name):
        '''
        given the username this fucntion shows the id, name, current 
        balance of the user
        :param conn: Connection Object
        :param name: User name (string)
        '''
        try:
            self.cur = self.conn.cursor()
            self.cur.execute('''SELECT balance FROM Users WHERE name = ?'''
                    , (name,))
            print('Showing Balance to user...')
            return self.cur.fetchone()
        except sqlite3.Error as e:
            print(e)
        finally:
            print('Closing cursor...')
            self.cur.close()

    def withdraw(self, name, amount):
        '''
        if the amount given for withdrawal satisfies the requirements
        it is withdraw.
        :param conn: Connection Object
        :param name: User name (string)
        '''
        try:
            self.cur = self.conn.cursor()
            self.cur.execute('''SELECT balance, withdrawal_limit FROM Users
                    WHERE name = ?''', (name,))
            query_res = self.cur.fetchone()
            balance = query_res[0]
            withdrawal_limit = query_res[1]
            if amount>0:
                if amount%20==0 or amount%50==0 or (amount%50)%20==0:
                    if amount<balance:
                        if amount<=withdrawal_limit:
                            self.cur.execute('''UPDATE Users SET balance = balance - ? 
                                    WHERE name = ?''', (amount,name,))
                            self.cur.execute('''UPDATE Users SET withdrawal_limit = withdrawal_limit - ?
                                    WHERE name = ?''', (amount, name,))
                            self.cur.execute('''UPDATE Users SET last_withdraw_date = ? 
                                    WHERE name = ?''', (datetime.datetime.now(), name,))
                            return 'OK'
                        else: 
                            return 'Amount cannot be greater than withdrawal limit.(' + str(withdrawal_limit) +')'
                    else: 
                        return 'Amount cannot be greater than current balance.'
                else:
                    return 'Amount is not a multiple of 20 nor 50 nor both.'
            else:
                return 'Amount must be a positive number. Please re-enter.'
        except sqlite3.Error as e:
            print(e)
        finally:
            self.conn.commit()
            self.cur.close()

    def deposit(self, name, amount):
        '''
        if the amount given for deposition satisfies the requirements
        it is deposited.
        :param conn: Connection Object
        :param name: User name (string)
        '''
        try:
            self.cur = self.conn.cursor()
            self.cur.execute('''UPDATE Users SET balance = balance + ? 
                    WHERE name = ?''', (int(amount),name,))
        except sqlite3.Error as e:
            print(e)
        finally:
            self.conn.commit()
            self.cur.close()
            return 'Deposition completed successfully.'

    def reset_withdrawal_limit(self):
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
            self.cur = self.conn.cursor()
            self.cur.execute('''SELECT name, last_withdraw_date FROM Users''')
            names = self.cur.fetchall()
            for name in names:
                if name[1]==None: continue
                x = str(name[1]).split('-')
                if x[1]==current_month and x[2][:2]==current_day: continue
                self.cur.execute('''UPDATE Users SET withdrawal_limit = 200
                            WHERE name = ?''', (name[0],))
        except sqlite3.Error as e:
            print(e)
        finally:
            self.conn.commit()
            print('Withdrawal day limits reseted.')
            self.cur.close()

    def delete_user(self, name):
        '''
        The user is deleted and (by logic) the current balance is returned 
        to the user to be deleted
        :param conn: Connection Object
        :param name: Username (string)
        '''
        try:
            self.cur = self.conn.cursor()
            self.cur.execute('''SELECT balance FROM Users WHERE name = ?''', (name,))
            balance = self.cur.fetchone()[0]
            self.cur.execute('''DELETE FROM Users WHERE name = ?''', (name,))
        except sqlite3.Error as e:
            print(e)
        finally:
            self.conn.commit()
            self.cur.close()
            return 'User deleted successfully. Money withdraw upon deleting account:' + str(balance)


if __name__ == '__main__':
    daemon = Pyro4.Daemon()  # make a Pyro daemon
    ns = Pyro4.locateNS()  # find the name server
    uri = daemon.register(BankDB)  # register the greeting maker as a Pyro object
    ns.register("HM1", uri)  # register the object with a name in the name server
    print('Ready!!!')
    daemon.requestLoop()  
