import flask
import flask_classful
import sqlite3
import json
import ast
import datetime

create_table_query = ''' CREATE TABLE IF NOT EXISTS Users(
                            id integer PRIMARY KEY,
                            name text NOT NULL,
                            entry_date text,
                            balance integer NOT NULL,
                            withdrawal_limit integer NOT NULL,
                            last_withdraw_date text);
                        '''

app = flask.Flask(__name__)
sql_file = 'ready.sqlite'

def output_json(data, code, headers=None):
    content_type = 'application/json'
    dumped = json.dumps(data)
    if headers:
        headers.update({'Content-Type': content_type})
    else:
        headers = {'Content-Type': content_type}
    response = flask.make_response(dumped, code, headers)
    return response

class serverSideREST(flask_classful.FlaskView):
    representations = {'application/json': output_json}

    def __init__(self):
        self.create_connection()
        print('Doing Database checks......')
        self.reset_withdrawal_limit()
        print('Api Ready!!!')

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

    @flask_classful.route('/getall', methods=['GET'])
    def get_all_users(self):
        print('*************New Request*************')
        print('Client called "Get All Users"')
        status = None
        data = json.loads(flask.request.data)
        data = ast.literal_eval(json.dumps(data))
        username = data['username']
        try:
            self.cur = self.conn.cursor()
            self.cur.execute('''SELECT * FROM Users''')
            q_res = self.cur.fetchall()
            response = json.dumps({'message':q_res})
            status = 200
        except sqlite3.Error as e:
            print(e)
            status = 400
            response = 'Error on database query'
        except Exception as e2:
            print(e2)
            status = 400
            response = 'Error occured'
        finally:
            self.cur.close()
            return {'response': response}, status
    
    @flask_classful.route('/delete/<username>', methods=['DELETE'])
    def delete_user(self, username):
        print('********New Request********')
        print('Client called "Delete User"')
        status = None
        try:
            self.cur = self.conn.cursor()
            self.cur.execute('''SELECT balance FROM Users WHERE name = ?''', (username,))
            balance = str(self.cur.fetchone()[0])
            self.cur.execute('''DELETE FROM Users WHERE name = ?''', (username,))
            status = 200
            response = 'User deleted successfully. Money withdraw upon\
                deletion: ' + balance
        except sqlite3.Error as e:
            print(e)
            status = 400
            response = 'Error on database query'
        except Exception as e2:
            print(e2)
            status = 400
            response = 'Error occurred!'
        finally:
            self.conn.commit()
            self.cur.close()
            return {'response': response}, status

    @flask_classful.route('/deposit', methods=['PUT'])        
    def deposit_amount(self):
        print('********New Request********')
        print('Client called "Deposit Amount"')
        status = None
        data = json.loads(flask.request.data)
        data = ast.literal_eval(json.dumps(data))
        username = data['username']
        amount = data['amount']
        try:
            self.cur = self.conn.cursor()
            if int(amount)>0: 
                if int(amount)%5==0:
                    self.cur.execute('''UPDATE Users SET balance = balance + ? 
                        WHERE name = ?''', (amount, username,))
                    response = 'OK'
                    status = 200
                else: 
                    response = 'Amount must be a multiple of 5. Please re-enter amount.'
                    status = 400
            else:
                response = 'Amount must be a positive number. Please re-enter.'
                status = 400
        except sqlite3.Error as e:
            print(e)
            status = 400
            response = 'Error on database query'
        except Exception as e2:
            print(e2)
            status = 400
            response = 'Error occured'
        finally:
            self.conn.commit()
            self.cur.close()
            return {'response': response}, status

    @flask_classful.route('/withdraw', methods=['PUT'])
    def withdraw_amount(self):
        print('********New Request********')
        print('Client called "Withdraw Amount"')
        status = None
        data = json.loads(flask.request.data)
        data = ast.literal_eval(json.dumps(data))
        username = data['username']
        amount = int(data['amount'])
        try:
            self.cur = self.conn.cursor()
            self.cur.execute('''SELECT balance, withdrawal_limit FROM Users
                    WHERE name = ?''', (username,))
            query_res = self.cur.fetchone()
            balance = query_res[0]
            withdrawal_limit = query_res[1]
            if amount>0:
                if amount%20==0 or amount%50==0 or (amount%50)%20==0:
                    if amount<balance:
                        if amount<=withdrawal_limit:
                            self.cur.execute('''UPDATE Users SET balance = balance - ? 
                                    WHERE name = ?''', (amount,username,))
                            self.cur.execute('''UPDATE Users SET withdrawal_limit = withdrawal_limit - ?
                                    WHERE name = ?''', (amount, username,))
                            self.cur.execute('''UPDATE Users SET last_withdraw_date = ? 
                                    WHERE name = ?''', (datetime.datetime.now(), username,))
                            response = 'OK'
                            status = 200
                        else: 
                            response = 'Amount cannot be greater than withdrawal limit.(' + str(withdrawal_limit) +')'
                            status = 400
                    else: 
                        response = 'Amount cannot be greater than current balance.'
                        status = 400
                else:
                    response = 'Amount is not a multiple of 20 nor 50 nor both.'
                    status = 400
            else:
                response = 'Amount must be a positive number. Please re-enter.'
                status = 400
        except sqlite3.Error as e:
            print(e)
            status = 400
            response = 'Error on database query'
        except Exception as e2:
            print(e2)
            status = 400
            response = 'Error occured'
        finally:
            self.conn.commit()
            self.cur.close()
            return {'response': response}, status

    @flask_classful.route('/balance/<username>', methods=['GET'])
    def show_balance(self, username):
        print('********New Request********')
        print('Client called "Delete User"')
        status = None
        try:
            self.cur = self.conn.cursor()
            self.cur.execute('''SELECT balance FROM Users WHERE name = ?'''
                    , (username,))
            result = self.cur.fetchone()
            print('result-',result[0])
            status = 200
            response = result[0]
        except sqlite3.Error as e:
            print(e)
            status = 400
            response = 'Error on databse query'
        except Exception as e2:
            print(e2)
            status = 400
            response = 'Error Occured'
        finally:
            self.cur.close()
            return {'response': response}, status

    @flask_classful.route('/insert', methods=['POST'])
    def insert_user(self):
        print('********New Request********')
        print('Client called "Delete User"')
        status = None
        data = json.loads(flask.request.data)
        data = ast.literal_eval(json.dumps(data))
        name = data['name']
        balance = data['balance']
        wd_limit = data['wd_limit']
        email = data['email']
        phone_number = data['phone_number']
        try:
            self.cur = self.conn.cursor()
            self.cur.execute('''INSERT INTO Users(name, entry_date, balance, 
                        withdrawal_limit, email, phone_number) VALUES (?, ?, ?, ?, ?, ?)''', 
                        (name, datetime.datetime.now(), balance, 
                        wd_limit, email, phone_number))
            response = 'OK'
            status = 200
        except sqlite3.Error as e:
            print(e)
            status = 400
            response = 'Error on database query.'
        except Exception as e2:
            print(e2)
            status = 400
            response = 'Error Occurred!!!'
        finally:
            self.conn.commit()
            self.cur.close()
            return {'response': response}, status

    @flask_classful.route('/existance/<username>', methods=['GET'])
    def user_exists(self, username):
        print('********New Request********')
        print('Client called "User Existance Check"')
        status = None
        try:
            self.cur = self.conn.cursor()
            self.cur.execute('''SELECT balance FROM Users WHERE name = ?''',
                (username,))
            res = self.cur.fetchone()
            response = (res is not None)
            status = 200
        except sqlite3.Error as e:
            print(e)
            status = 400
            response = 'Error on databse query'
        except Exception as e2:
            print(e2)
            status = 400
            response = 'Error Occurred!!!'
        finally:
            print('Closing cursor......')
            self.cur.close()
            return {'response': response}, status

if __name__ == '__main__':
    serverSideREST.register(app, route_base="/")
    app.run()