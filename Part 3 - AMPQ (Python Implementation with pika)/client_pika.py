import pika
import uuid
import json
import datetime 
'''
*This is the client side of the application
*The user can choose between Deposition, Withdrawal and checking his current 
balance. Also, he has the ability to delete his account. Also, a user can insert 
values to create another user and he can get all the info in the database.
*Each method takes a message as a parameter that can difer between methods
    -For example, at one time it can be only the username or it can be a 
    json of the whole user's info so the insert to the databse can be achieved.
*Each method calls it's respective queue so that it can send the correct 
    -request to the correct queue.
***EXITING SERVER APP BY PRESSING -> Ctrl+C
'''

class client_side:
    def __init__(self):

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            'dove.rmq.cloudamqp.com',
            5672,
            'hlnxvzxs',
            pika.PlainCredentials('hlnxvzxs', 
            'Vx5dzCFmvkEclRNvHN7nYDgLN2yA6IYf')))

        self.channel = self.connection.channel()
        result = self.channel.queue_declare('', exclusive=True)
        print(result)
        self.callback_queue = result.method.queue
        print(self.callback_queue)
        self.channel.basic_consume(self.callback_queue, self.response_handle)
        self.client_menu()
    # wait for the response and if the correlation id is the same then assign
    # the body to the response
    def response_handle(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body
    
    def show_client_balance(self, message):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='show',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id
            ),
            body=message
        )
        # wait for the response
        while self.response is None:
            self.connection.process_data_events()

    def user_existance(self, message):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='existance',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id
            ),
            body=message
        )
        while self.response is None:
            self.connection.process_data_events()
    
    def withdraw_amount(self, message):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='withdraw',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id
            ),
            body=message
        )
        while self.response is None:
            self.connection.process_data_events()

    def deposit_amount(self, message):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='deposit',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id
            ),
            body=message
        )
        while self.response is None:
            self.connection.process_data_events()

    def delete_user(self, message):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='delete',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id
            ),
            body=message
        )
        while self.response is None:
            self.connection.process_data_events()

    def get_all_users(self, message):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='getall',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id
            ),
            body=message
        )
        while self.response is None:
            self.connection.process_data_events()

    def insert_users(self, message):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='insert',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id
            ),
            body=message
        )
        while self.response is None:
            self.connection.process_data_events()

    # User's menu where he is presented with the available actions each time
    # after the authentication that he exists
    # A higher level of authenication cna be implemented but it still won't
    # be ofa sufficient level as db fields will still be used and there wont be
    # no security for the database's privacy
    def client_menu(self):
        print('******Welcome******')
        
        # A user enter his name and if he does not exist then he cant proceed
        while True:
            username = input('Enter username --- ')
            self.user_existance(username)
            if self.response.decode('utf-8') == 'True': 
                print('User Exists!!!')
                break
            else:
                print('Error!!! User not found!!!')
        
        # the user is presented with the available actions
        while True:
            print('Actions Available: Deposit, Withdraw, Show Balance, Delete Account,\
                    Insert Users, Get All Users, Exit')
            action = input('Please enter the desired action - ')
            if action == 'Deposit':
                while True:
                    amount = input('Enter the desired amount for deposition --- ')
                    message = username + ' ' + amount
                    self.deposit_amount(message)
                    res = self.response.decode('utf-8')
                    if res == 'OK': break
                    else: print(res)
            elif action == 'Withdraw':
                while True:
                    amount = input('Enter the desired amount for withdrawal --- ')
                    message = username + ' ' + amount
                    self.withdraw_amount(message)
                    res = self.response.decode('utf-8')
                    if res == 'OK': break
                    else: print(res)
                print('Transaction Completed.')
            elif action == 'Show Balance':
                self.show_client_balance(username)
                print('Current Balance: ', self.response.decode('utf-8f'))
            elif action == 'Delete Account':
                self.delete_user(username)
                print(self.response.decode('utf-8'))
            elif action == 'Insert Users': 
                while True:
                    print('Enter user\'s values -----------')
                    name = input('Enter user\'s username --- ')
                    balance = input('Enter user\'s balance --- ')
                    wd_limit = input('Enter user\'s withdrawal limit per day --- ')
                    email = input('Enter user\'s email address --- ')
                    phone_number = input('Enter user\'s phone number --- ')
                    message = json.dumps({
                        "name": name,
                        "balance": balance,
                        "wd_limit": wd_limit,
                        "email": email,
                        "phone_number": phone_number
                    })
                    self.insert_users(message)
                    msg = self.response.decode('utf-8')
                    if msg == 'OK': print('User added Successfully!!!!!')
                    else: print(msg)
                    choice = input('-----------Add more users? (Y/N)------------')
                    if choice == 'N': break
            elif action == 'Get All Users': 
                self.get_all_users(username)
                resp = json.loads(self.response.decode('utf-8'))
                for line in resp['response']:
                    print(line)
            elif action == 'Exit':
                print('Exiting.......')
                print('Goodbye!!!')
                break
            #if the entered action is not valid he is promted for re-entering
            else:
                print('No such action found.')
                print('You will be prompted to re-enter action....')

if __name__ == '__main__':
    client = client_side()