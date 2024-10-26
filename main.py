import time
import json
import telebot

## TOKEN DETAILS
BOT_TOKEN = "7465775302:AAHpcywPC2cHvPu3gGyXzHiNMkpPuvNIrzM"  # Replace with your bot's token

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)

# Initialize user data
# If `users.json` doesn't exist, create it
try:
    data = json.load(open('users.json', 'r'))
except FileNotFoundError:
    data = {
        'users': {},
        'total_amount': 0
    }
    json.dump(data, open('users.json', 'w'))

# Menu function
def menu(id):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('🆔 My Account')
    keyboard.row('➕ Credit', '➖ Debit')
    keyboard.row('💰 Check Balance', '📊 Statistics')
    bot.send_message(id, "*🏡 Home*", parse_mode="Markdown", reply_markup=keyboard)

# Start command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    
    # Initialize user if not already in the data
    if user_id not in data['users']:
        data['users'][user_id] = {
            'total_amount': 0,
            'transactions': []
        }
        json.dump(data, open('users.json', 'w'))
    
    bot.send_message(user_id, "*Welcome to the Personal Finance Bot!*\nUse the menu to manage your finances.", parse_mode="Markdown")
    menu(user_id)

# Handle menu options
@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = str(message.chat.id)
    
    if message.text == '🆔 My Account':
        account_info(user_id)
    elif message.text == '➕ Credit':
        bot.send_message(user_id, "Enter the amount to credit:")
        bot.register_next_step_handler(message, credit_amount)
    elif message.text == '➖ Debit':
        bot.send_message(user_id, "Enter the amount to debit:")
        bot.register_next_step_handler(message, debit_amount)
    elif message.text == '💰 Check Balance':
        check_balance(user_id)
    elif message.text == '📊 Statistics':
        show_statistics(user_id)
    else:
        bot.send_message(user_id, "Invalid command. Please use the menu.")
        menu(user_id)

# Credit amount function
def credit_amount(message):
    try:
        amount = float(message.text)
        user_id = str(message.chat.id)
        
        if amount <= 0:
            bot.send_message(user_id, "Amount must be greater than 0.")
            return
        
        data['users'][user_id]['total_amount'] += amount
        data['users'][user_id]['transactions'].append({'type': 'credit', 'amount': amount})
        json.dump(data, open('users.json', 'w'))
        
        bot.send_message(user_id, f"Successfully credited {amount} to your account.")
        menu(user_id)
    except ValueError:
        bot.send_message(message.chat.id, "Invalid input. Please enter a valid number.")
        menu(message.chat.id)

# Debit amount function
def debit_amount(message):
    try:
        amount = float(message.text)
        user_id = str(message.chat.id)
        
        if amount <= 0:
            bot.send_message(user_id, "Amount must be greater than 0.")
            return
        
        if amount > data['users'][user_id]['total_amount']:
            bot.send_message(user_id, "Insufficient balance!")
            return
        
        data['users'][user_id]['total_amount'] -= amount
        data['users'][user_id]['transactions'].append({'type': 'debit', 'amount': amount})
        json.dump(data, open('users.json', 'w'))
        
        bot.send_message(user_id, f"Successfully debited {amount} from your account.")
        menu(user_id)
    except ValueError:
        bot.send_message(message.chat.id, "Invalid input. Please enter a valid number.")
        menu(message.chat.id)

# Show account info
def account_info(user_id):
    balance = data['users'][user_id]['total_amount']
    transactions = data['users'][user_id]['transactions']
    transaction_history = "\n".join([f"{t['type'].capitalize()}: {t['amount']}" for t in transactions[-5:]]) or "No transactions yet."
    
    message = f"*🆔 Account Info*\n\n💰 Balance: {balance}\n\n📜 Recent Transactions:\n{transaction_history}"
    bot.send_message(user_id, message, parse_mode="Markdown")

# Check balance function
def check_balance(user_id):
    balance = data['users'][user_id]['total_amount']
    bot.send_message(user_id, f"Your current balance is: {balance}")

# Show statistics function
def show_statistics(user_id):
    total_credit = sum(t['amount'] for t in data['users'][user_id]['transactions'] if t['type'] == 'credit')
    total_debit = sum(t['amount'] for t in data['users'][user_id]['transactions'] if t['type'] == 'debit')
    balance = data['users'][user_id]['total_amount']
    
    message = f"*📊 Statistics*\n\nTotal Credit: {total_credit}\nTotal Debit: {total_debit}\nCurrent Balance: {balance}"
    bot.send_message(user_id, message, parse_mode="Markdown")

# Start the bot
if __name__ == '__main__':
    bot.polling(none_stop=True)
      
