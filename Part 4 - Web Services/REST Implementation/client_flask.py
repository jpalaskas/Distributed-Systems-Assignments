import requests
import json
import ast

#  Each user has the ability to delete only his account

print('**********Welcome**********')

while True:
    username = input('Enter your username --- ')
    print('Sending request to authenticate user.....')
    req = requests.get('http://127.0.0.1:5000/existance/' + username)
    reqq = req.content.decode('utf-8')
    resp = json.loads(reqq)
    if resp['response']:
        print('Authentication Successful!!!')
        break
    else:
        print('User not found.')
        print('You will be prompted to re-enter your username')

while True:
    print('Actions Available: Deposit, Withdraw, Show Balance, Delete Account,\
        Insert Users, Get All Users, Exit')
    action = input('Please enter the desired action - ')
    if action == 'Deposit': 
        while True:
            amount = input('Please enter the desired amount for deposition --- ')
            print('Sending request to deposit an amount to user\'s account.....')
            message = json.dumps({
                'username':username,
                'amount':amount
            })
            req = requests.put('http://127.0.0.1:5000/deposit', data= message)
            reqq = req.content.decode('utf-8')
            resp = json.dumps(json.loads(reqq))
            response = ast.literal_eval(resp)
            if response['response'] == 'OK':
                print('Deposition Successful!!!')
                break
            else:
                print(response['response']) 
                print('You will be prompted to re-enter amount.....')
    elif action == 'Withdraw': 
        while True:
            amount = input('Please enter the desired amount for withdrawal --- ')
            print('Sending request to withdraw an amount from user\'s account.....')
            message = json.dumps({
                'username':username,
                'amount':amount
            })
            req = requests.put('http://127.0.0.1:5000/withdraw', data= message)
            reqq = req.content.decode('utf-8')
            resp = json.dumps(json.loads(reqq))
            response = ast.literal_eval(resp)
            if response['response'] == 'OK':
                print('Withdrawal Successful!!!')
                break
            else:
                print(response['response']) 
                print('You will be prompted to re-enter amount.....')
    elif action == 'Show Balance': 
        print('Sending request to get user\'s current balance.....')
        req = requests.get('http://127.0.0.1:5000/balance/' + username)
        reqq = req.content.decode('utf-8')
        resp = json.dumps(json.loads(reqq))
        response = ast.literal_eval(resp)
        print('Current Balance: ' + response['response'])
    elif action == 'Delete Account': 
        print('Sending request to delete user\'s account.....')
        req = requests.delete('http://127.0.0.1:5000/delete/' + username)
        reqq = req.content.decode('utf-8')
        resp = json.dumps(json.loads(reqq))
        response = ast.literal_eval(resp)
        print(response['response'])
    elif action == 'Insert Users': 
        while True:
            print('Sending request to insert a new user account.....')
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
            req = requests.post('http://127.0.0.1:5000/insert', data= message)
            reqq = req.content.decode('utf-8')
            resp = json.dumps(json.loads(reqq))
            response = ast.literal_eval(resp)
            if response['response'] == 'OK':
                print('User Creation Successful!!!')
                break
            else:
                print(response['response']) 
                print('You will be prompted to re-enter amount.....')
    elif action == 'Get All Users':
        print('Sending request to get all users in the database.....')
        message = json.dumps({'username':username})
        req = requests.get("http://127.0.0.1:5000/getall", data=message)
        reqq = req.content.decode('utf-8')
        resp = json.dumps(json.loads(reqq))
        response = ast.literal_eval(resp)
        res_msg = json.loads(response['response'])
        for line in res_msg['message']:
            print(line)
    elif action == 'Exit': 
        print('Exiting......')
        break
    else: 
        print('No such action found.')
        print('You will be prompted to re-enter action....')

print('Goodbye')