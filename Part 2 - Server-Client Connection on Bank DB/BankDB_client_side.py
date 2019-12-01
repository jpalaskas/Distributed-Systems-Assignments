#client side for BankDB
import Pyro4

connection_with_server = Pyro4.Proxy("PYRONAME:HM1")

print('***Welcome***')

user_existance = ''
while True:
    user_name = input('Enter your name --- ')
    try:
        user_existance = connection_with_server.user_indb(user_name)
    except Exception:
        print("Pyro traceback:")
        print("".join(Pyro4.util.getPyroTraceback()))
    if user_existance: break
    else: 
        print('Username does not exist in the database.')
        print('Please re-enter username correctly.')
     

while True:    
    print('Actions Available: Deposit, Withdraw, Show Balance, Delete Account, Exit')
    action = input('Please enter the desired action - ')
    if action=='Deposit':
        while True:
                amount = input('Enter the amount for deposit - ')
                if int(amount)>0: 
                    if int(amount)%5==0: break
                    else: 
                        print('Amount must be a multiple of 5. Please re-enter amount.')
                else:
                    print('Amount must be a positive number. Please re-enter.')
        print(connection_with_server.deposit(user_name, amount))
    elif action=='Withdraw':
        while True:
            inp = input('Enter the amount for withdrawal - ')
            amount = int(inp)
            ser_reply = ''
            try:
                ser_reply = connection_with_server.withdraw(user_name, amount)
            except Exception:
                print("Pyro traceback:")
                print("".join(Pyro4.util.getPyroTraceback()))
            if ser_reply!='OK':
                print('Withdrawal Failed!!!')
                print(ser_reply)
            else: break
        print('Withdrawal Successful')
    elif action=='Show Balance':
        try:
            res = connection_with_server.show_balance(user_name)
            print('Current Balance:', res[0])
        except Exception:
            print("Pyro traceback:")
            print("".join(Pyro4.util.getPyroTraceback()))
    elif action=='Delete Account':
        try:    
            print(connection_with_server.delete_user(user_name))
        except Exception:
            print("Pyro traceback:")
            print("".join(Pyro4.util.getPyroTraceback()))
    elif action=='Exit': break
    else : print('No such action found. Please re-enter.')

print('Exiting BankDB...')
print('Goodbye!')