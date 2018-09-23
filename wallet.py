import os

import requests
import json
import sys
from blessed import Terminal

RPC_ADDRESS = "http://localhost:1761"
WALLET_FILE = "wallets.json"

wallet = None
term = Terminal()


def main():
    global wallet
    print(term.enter_fullscreen)
    print(term.move_y(term.height // 2 - 2) +
          term.center('Welcome to ITCOWallet').rstrip())
    print(term.move_y(term.height // 2 - 1) +
          term.center('Press Any Key to Continue').rstrip())
    term.inkey()
    print(term.clear)
    if post("{}") is None:
        print("Failed to connect to ITCO node. Make sure node is running with correct config.")
        sys.exit(1)
    if not os.path.exists(WALLET_FILE):
        touch = open(WALLET_FILE, 'w+')
        touch.close()

    with open(WALLET_FILE, 'r') as f:
        try:
            wallets = json.load(f)
        except json.JSONDecodeError:
            wallets = None

    if wallets is None:
        print("No wallet could be detected. Creating one for you...")
        wallet = create_wallet()['wallet']
        with open(WALLET_FILE, 'w') as f:
            json.dump({"main": wallet}, f)

    while wallet is None:
        print(term.clear)
        print("Which wallet would you like to open?")
        print("Do not enter a wallet name to default to \"main\".")
        for w in wallets:
            print(w)
        wallet_name = input("\nEnter wallet name: ")
        if not wallet_name:
            wallet_name = "main"
        if wallet_name in wallets:
            wallet = wallets[wallet_name]
        else:
            print(term.clear)
            print("Wallet not found with name: " + wallet_name)
            print("Press any key to try again...")
            term.inkey()
    print(term.clear)
    print("Opened wallet.")
    print()
    balances = wallet_balances(wallet)['balances']
    for balance in balances:
        print("Balance: " + balances[balance]['balance'] + " ITCO \nAddress: " + balance)

    # Begin main loop

    while True:
        print(term.move(term.height - term.get_location(timeout=5)[1] - 1, 0))
        command = input("ITCO Wallet > ")
        if not command:
            print("No command entered.")
            continue
        if command == "help":
            print("Add help pages!")
        elif command == "balances":
            print(term.clear)
            balances = wallet_balances(wallet)['balances']
            for balance in balances:
                print("Balance: " + balances[balance]['balance'] + " ITCO \nAddress: " + balance)
        elif command == "quit" or command[0] == "exit":
            print(term.clear)
            exit(0)
        elif command == "clear":
            print(term.clear)
        else:
            print("Command not found, try using the help command.")


def wallet_balances(wallet):
    data = {
        "action": "wallet_balances",
        "wallet": wallet
    }
    return post(data).json()


def wallet_info(wallet):
    data = {
        "action": "wallet_info",
        "wallet": wallet
    }
    return post(data).json()


def create_wallet():
    data = {
        "action": "wallet_create"
    }
    return post(data).json()


def post(data):
    try:
        return requests.post(RPC_ADDRESS, data=json.dumps(data))
    except requests.exceptions.RequestException:
        return None


if __name__ == "__main__":
    main()
