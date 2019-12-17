import sqlite3
import pika
import datetime
import json 

sql_file = 'ready.sqlite'

'''
Users Table consists of the following(as show in the query below):
id, name, entry_date, balance, withdrawal_limit (per day), last_withdraw_date, 
email, phone_number
----------------------------------------------------------------------
The user can choose between Deposition, Withdrawal and checking his current 
balance. Also, he has the ability to delete his account. Also, a user can insert 
values to create another user and he can get all the info in the database.
The same checks that existed in the previous assignments are implemented here as well.
'''

create_table_query = ''' CREATE TABLE IF NOT EXISTS Users(
                            id integer PRIMARY KEY,
                            name text NOT NULL,
                            entry_date text,
                            balance integer NOT NULL,
                            withdrawal_limit integer NOT NULL,
                            last_withdraw_date text);
                        '''

class server_side:   
    def __init__(self):
        self.create_connection()
        print('Doing Database checks.......')
        self.reset_withdrawal_limit()

        print(' [x] Awaiting RPC Requests.....')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            'dove.rmq.cloudamqp.com',
            5672,
            'hlnxvzxs',
            pika.PlainCredentials('hlnxvzxs', 
            'Vx5dzCFmvkEclRNvHN7nYDgLN2yA6IYf')))  
        self.channel = self.connection.channel()

        print('*********Decalring Queues on channel**********')
        self.channel.queue_declare(queue='existance')
        self.channel.queue_declare(queue='getall')
        self.channel.queue_declare(queue='insert')
        self.channel.queue_declare(queue='deposit')
        self.channel.queue_declare(queue='withdraw')
        self.channel.queue_declare(queue='show')
        self.channel.queue_declare(queue='delete')

        # associating queues with their respective methods
        print('*******Consuming Queues on channel********')
        self.channel.basic_consume('existance', self.user_exists)
        self.channel.basic_consume('getall', self.get_all_users)
        self.channel.basic_consume('insert', self.insert_users)
        self.channel.basic_consume('deposit', self.deposit_amount)
        self.channel.basic_consume('withdraw', self.withdraw_ammount)
        self.channel.basic_consume('show',self.show_user_balance)
        self.channel.basic_consume('delete', self.delete_user)

        print('*******Starting to consume**********')
        self.channel.start_consuming()

    def create_connection(self):
        '''
        create a database connection to the SQLite database
            specified by the db_name given above
        '''
        try:
            self.conn = sqlite3.connect(sql_file)
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

    def show_user_balance(self, channel, method, properties, body):
        '''
        *****ALL THE PARAMETERS ARE THE SAME IN ALL THE OTHER FUNCTIONS AS WELL*****
        :param channel: the channel(means of communication) we use
        :param method: the association between method and queue(routing key)
        :param properties: the basic properties consisted of the callback queue
            and the correlation id
        :param body: the message coming from the client side
        '''
        print('****************New request**************')
        print('Client called "Show Balance"')
        username = body.decode('utf-8')
        try:
            self.cur = self.conn.cursor()
            self.cur.execute('''SELECT balance FROM Users WHERE name = ?'''
                    , (username,))
            result = self.cur.fetchone()
            print('result-',result[0])
            response = result[0]
        except sqlite3.Error as e:
            print(e)
        finally:
            print('Closing cursor...')
            self.cur.close()
        # publish the message passing all the necessary parameters
        self.channel.basic_publish(
            exchange= '',
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id
            ),
            body=str(response)
        )
        # we acknowledge the message
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def user_exists(self, channel, method, properties, body):
        print('***********New Request**************')
        print('Checking if given user exists in the database....')
        username = body.decode('utf-8')
        try:
            self.cur = self.conn.cursor()
            self.cur.execute('''SELECT balance FROM Users WHERE name = ?''',
                (username,))
            res = self.cur.fetchone()
            print(res is not None)
            response = (res is not None)
            print(response)
        except sqlite3.Error as e:
            print(e)
        finally:
            print('Closing cursor......')
            self.cur.close()
        
        self.channel.basic_publish(
            exchange= '',
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id
            ),
            body=str(response)
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)
        
    def withdraw_ammount(self, channel, method, properties, body):
        print('*************New Request*************')
        print('Client called "Withdraw Amount"')
        pieces = body.decode('utf-8').split()
        print(pieces)
        username = pieces[0]
        amount = int(pieces[1])
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
        finally:
            self.conn.commit()
            self.cur.close()
            
        self.channel.basic_publish(
            exchange= '',
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id
            ),
            body=response
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def deposit_amount(self, channel, method, properties, body):
        print('*************New Request*************')
        print('Client called "Deposit Amount"')
        pieces = body.decode('utf-8').split()
        username = pieces[0]
        amount = int(pieces[1])
        try:
            self.cur = self.conn.cursor()
            if int(amount)>0: 
                if int(amount)%5==0:
                    self.cur.execute('''UPDATE Users SET balance = balance + ? 
                        WHERE name = ?''', (amount, username,))
                    response = 'OK'
                else: 
                    response = 'Amount must be a multiple of 5. Please re-enter amount.'
            else:
                response = 'Amount must be a positive number. Please re-enter.'
        except sqlite3.Error as e:
            print(e)
        finally:
            self.conn.commit()
            self.cur.close()
        
        self.channel.basic_publish(
            exchange= '',
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id
            ),
            body=response
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def delete_user(self, channel, method, properties, body):
        print('*************New Request*************')
        print('Client called "Deposit Amount"')
        username = body.decode('utf-8').split()
        try:
            self.cur = self.conn.cursor()
            self.cur.execute('''SELECT balance FROM Users WHERE name = ?''', (username,))
            balance = self.cur.fetchone()[0]
            self.cur.execute('''DELETE FROM Users WHERE name = ?''', (username,))
        except sqlite3.Error as e:
            print(e)
        finally:
            self.conn.commit()
            self.cur.close()
            response = 'User deleted successfully. Money withdraw upon deleting account:' + str(balance)
        
        self.channel.basic_publish(
            exchange= '',
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id
            ),
            body=response
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def get_all_users(self, channel, method, properties, body):
        print('*************New Request*************')
        print('Client called "Get All Users"')
        try:
            self.cur = self.conn.cursor()
            self.cur.execute('''SELECT * FROM Users ''')
            response = self.cur.fetchall()
            print(response)
        except sqlite3.Error as e:
            print(e)
        finally:
            self.conn.commit()
            self.cur.close()
        
        self.channel.basic_publish(
            exchange= '',
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id
            ),
            body= json.dumps({'response': response})
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def insert_users(self, channel, method, properties, body):
        print('*************New Request*************')
        print('Client called "Insert Users"')
        data = json.loads(body)
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
        except sqlite3.Error as e:
            print(e)
            response = 'Error Occurred!!!'
        finally:
            self.conn.commit()
            self.cur.close()

        self.channel.basic_publish(
            exchange= '',
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id
            ),
            body= response
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == '__main__':
    server = server_side()