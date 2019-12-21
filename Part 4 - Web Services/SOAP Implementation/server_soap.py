import sqlite3
import spyne
import spyne.protocol.soap
import spyne.server.wsgi
import json
import datetime

sql_file = 'ready.sqlite'

class RequestManager(spyne.ServiceBase):

    @spyne.rpc(spyne.Unicode, _returns=spyne.Iterable(spyne.Unicode))
    def request_manager(self, data):
        db = serverDB()
        data = json.loads(data)
        method = data['method']
        if method == 'showbalance':
            response = db.show_balance(data['username'])
            yield json.dumps({'response': response})
        elif method == 'deposit': 
            response = db.deposit_amount(data['username'], data['amount'])
            yield json.dumps({'response': response})
        elif method == 'withdraw': 
            response = db.withdraw_amount(data['username'], data['amount'])
            yield json.dumps({'response': response})
        elif method == 'deleteuser': 
            response = db.delete_user(data['username'])
            yield json.dumps({'response': response})
        elif method == 'insertusers': 
            response = db.insert_users(data['name'],data['balance'],
                data['wd_limit'], data['email'], data['phone_number'])
            yield json.dumps({'response': response})
        elif method == 'getallusers': 
            response = db.get_all_users()
            yield json.dumps({'response': response})
        elif method == 'user_existance':
            response = db.user_exists(data['username'])
            yield json.dumps({'response': response})


class serverDB:
    def __init__(self):
        self.create_connection()
        print('Doing database checks......')
        self.reset_withdrawal_limit()

    def create_connection(self):
        '''
        create a database connection to the SQLite database
            specified by the db_name given above
        '''
        try:
            self.conn = sqlite3.connect(sql_file, check_same_thread=False)
            print('*********Server connected to DB*********')
        except sqlite3.Error as e:
            print(e)
    
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
            count = 0
            for name in names:
                if name[1]=='' or name[1]=='NULL' or name[1]==None: continue
                x = str(name[1]).split('-')
                if x[1]==current_month and x[2][:2]==current_day: continue
                self.cur.execute('''UPDATE Users SET withdrawal_limit = 200
                            WHERE name = ?''', (name[0],))
                count = count + 1
        except sqlite3.Error as e:
            print(e)
        finally:
            self.conn.commit()
            print('Withdrawal day limits reseted.')
            if count != 0:
                print('Changed ', count, ' withdrawal day limits.')
            self.cur.close()

    def show_balance(self, name):
        print('********New Request********')
        print('Client called "Show User Balance"')
        try:
            self.cur = self.conn.cursor()
            self.cur.execute('''SELECT balance FROM Users WHERE name = ?'''
                    , (name,))
            result = self.cur.fetchone()
            print('result-',result[0])
            response = result[0]
        except sqlite3.Error as e:
            print(e)
            response = 'Error on database query'
        except Exception as e2:
            print(e2)
            response = 'Error Occured!!!'
        finally:
            self.cur.close()
            return response
    
    def deposit_amount(self, name, amount): 
        print('********New Request********')
        print('Client called "Withdraw Amount"')
        try:
            self.cur = self.conn.cursor()
            if int(amount)>0: 
                if int(amount)%5==0:
                    self.cur.execute('''UPDATE Users SET balance = balance + ? 
                        WHERE name = ?''', (amount, name,))
                    response = 'OK'
                else: 
                    response = 'Amount must be a multiple of 5. Please re-enter amount.'
            else:
                response = 'Amount must be a positive number. Please re-enter.'
        except sqlite3.Error as e:
            print(e)
            response = 'Error on database query'
        except Exception as e2:
            print(e2)
            response = 'Error occured'
        finally:
            self.conn.commit()
            self.cur.close()
            return response

    def withdraw_amount(self, name, salary): 
        print('********New Request********')
        print('Client called "Withdraw Amount"')
        try:
            self.cur = self.conn.cursor()
            self.cur.execute('''SELECT balance, withdrawal_limit FROM Users
                    WHERE name = ?''', (name,))
            query_res = self.cur.fetchone()
            balance = query_res[0]
            withdrawal_limit = query_res[1]
            amount = int(salary)
            if amount>0:
                if amount%20==0 or amount%50==0 or (amount%50)%20==0:
                    if amount<balance:
                        if amount<=withdrawal_limit:
                            self.cur.execute('''UPDATE Users SET balance = balance - ? 
                                    WHERE name = ?''', (amount, name,))
                            self.cur.execute('''UPDATE Users SET withdrawal_limit = withdrawal_limit - ?
                                    WHERE name = ?''', (amount, name,))
                            self.cur.execute('''UPDATE Users SET last_withdraw_date = ? 
                                    WHERE name = ?''', (datetime.datetime.now(), name,))
                            response = 'OK'
                        else: 
                            response = 'Amount cannot be greater than withdrawal limit.(' + str(withdrawal_limit) +')'
                    else: 
                        response = 'Amount cannot be greater than current balance.'
                else:
                    response = 'Amount is not a multiple of 20 nor 50 nor both.'
            else:
                response = 'Amount must be a positive number. Please re-enter.'
        except sqlite3.Error as e:
            print(e)
            response = 'Error on database query'
        except Exception as e2:
            print(e2)
            response = 'Error occured'
        finally:
            self.conn.commit()
            self.cur.close()
            return response

    def delete_user(self, name): 
        print('********New Request********')
        print('Client called "Delete User"')
        try:
            self.cur = self.conn.cursor()
            self.cur.execute('''SELECT balance FROM Users WHERE name = ?''', (name,))
            balance = str(self.cur.fetchone()[0])
            self.cur.execute('''DELETE FROM Users WHERE name = ?''', (name,))
            response = 'User deleted successfully. Money withdraw upon\
                deletion: ' + balance
        except sqlite3.Error as e:
            print(e)
            response = 'Error on database query'
        except Exception as e2:
            print(e2)
            response = 'Error Occured!!!'
        finally:
            self.conn.commit()
            self.cur.close()
            return response

    def insert_users(self, name, balance, wd_limit, email, phone_number): 
        print('********New Request********')
        print('Client called "Delete User"')
        try:
            self.cur = self.conn.cursor()
            self.cur.execute('''INSERT INTO Users(name, entry_date, balance, 
                        withdrawal_limit, email, phone_number) VALUES (?, ?, ?, ?, ?, ?)''', 
                        (name, datetime.datetime.now(), balance, 
                        wd_limit, email, phone_number))
            response = 'OK'
        except sqlite3.Error as e:
            print(e)
            response = 'Error on database query'
        except Exception as e2:
            print(e2)
            response = 'Error Occured!!!'
        finally:
            self.conn.commit()
            self.cur.close()
            return response

    def get_all_users(self): 
        print('********New Request********')
        print('Client called "Get All Users"')
        try:
            self.cur = self.conn.cursor()
            self.cur.execute('''SELECT * FROM Users''')
            q_res = self.cur.fetchall()
            print(q_res)
            response = q_res
        except sqlite3.Error as e:
            print(e)
            response = 'Error on database query'
        except Exception as e2:
            print(e2)
            response = 'Error Occured!!!'
        finally:
            self.cur.close()
            return response

    def user_exists(self, name):
        print('********New Request********')
        print('Client called "User Existance Check"')
        try:
            self.cur = self.conn.cursor()
            self.cur.execute('''SELECT balance FROM Users WHERE name = ?''',
                (name,))
            res = self.cur.fetchone()
            response = (res is not None)
        except sqlite3.Error as e:
            print(e)
            response = 'Error on databse query'
        except Exception as e2:
            print(e2)
            response = 'Error Occurred!!!'
        finally:
            self.cur.close()
            return response

app = spyne.Application(
    [RequestManager], 
    'spyne.dbconn.soap',
    in_protocol=spyne.protocol.soap.Soap11(validator='lxml'),
    out_protocol=spyne.protocol.soap.Soap11()    
)

wsgi_application = spyne.server.wsgi.WsgiApplication(app)

if __name__ == '__main__':
    import logging
    import wsgiref.simple_server

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)

    logging.info("listening to http://127.0.0.1:8000")
    logging.info("wsdl is at: http://localhost:8000/?wsdl")

    server = wsgiref.simple_server.make_server('127.0.0.1', 8000, wsgi_application)
    server.serve_forever()