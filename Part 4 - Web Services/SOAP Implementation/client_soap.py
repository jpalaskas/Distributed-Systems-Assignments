import zeep
import json

client = zeep.Client('http://localhost:8000/?wsdl')

print('********Welcome********')

while True:
    username = input('Please enter your username --- ')
    print('Sending request about the user\'s existance.....')
    message = json.dumps({
        'username': username,
        'method': 'user_existance'
    })
    resp = client.service.request_manager(message)
    response = json.loads(resp[0])
    if response['response']: 
        print('User Exists....')
        break
    else:
        print('User not found.')
        print('You will be prompted to re-enter your username....')

while True:
    print('Actions Available: Deposit, Withdraw, Show Balance, Delete Account,\
        Insert Users, Get All Users, Exit')
    action = input('Please enter the desired action - ')
    if action == 'Deposit': 
        print('Sending request to get user\'s current balance.....')
        amount = input('Enter the desired amount for deposition: ')
        message = json.dumps({
            'username': username,
            'amount': amount,
            'method': 'deposit'
        })
        resp = client.service.request_manager(message)
        response = json.loads(resp[0])
        print(response['response'])
        if response['response']=='OK':
            print('Amount deposited successfully!!!')
        else: print(response['response'])
    elif action == 'Withdraw': 
        print('Sending request to get user\'s current balance.....')
        amount = input('Enter the desired amount for withdrawal: ')
        message = json.dumps({
            'username': username,
            'amount': amount,
            'method': 'withdraw'
        })
        resp = client.service.request_manager(message)
        response = json.loads(resp[0])
        if response['response']=='OK':
            print('Amount withdrawn successfully!!!')
    elif action == 'Show Balance': 
        print('Sending request to get user\'s current balance.....')
        message = json.dumps({
            'username': username,
            'method': 'showbalance'
        })
        resp = client.service.request_manager(message)
        response = json.loads(resp[0])
        print(response['response'])
    elif action == 'Delete Account': 
        print('Sending request to get user\'s current balance.....')
        message = json.dumps({
            'username': username,
            'method': 'deleteuser'
        })
        resp = client.service.request_manager(message)
        response = json.loads(resp[0])
        if not response['response'].startswith('Error'):
            print(response['response'])
            print('Exiting Program')
            break
        else:
            print(response['response'])
    elif action == 'Insert Users': 
        while True:
            print('Sending request to get user\'s current balance.....')
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
                "phone_number": phone_number,
                'method': 'insertusers'
            })
            resp = client.service.request_manager(message)
            response = json.loads(resp[0])
            if response['response']=='OK':
                print('User added successfully!!!')
            else:
                print(response['response'])
            choice = input('Do you want to add more users? (Y/N)')
            if choice == 'N' or choice=='n': break
    elif action == 'Get All Users': 
        print('Sending request to get user\'s current balance.....')
        message = json.dumps({
            'method': 'getallusers'
        })
        resp = client.service.request_manager(message)
        response = json.loads(resp[0])
        for item in response['response']:
            print(item)
    elif action == 'Exit': 
        print('Exiting......')
        break
    else: 
        print('No such action found.')
        print('You will be prompted to re-enter action....')

print('Goodbye')