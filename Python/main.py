import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext.filters import Filters
from queue import Queue

TOKEN = 6202478643:AAE2YZDJOZytvUb2xYCf22s6cXC-bPX0Q9Y

# Dictionary to store the selected chat link or ID to track
chat_to_track = {}

# Function to get the chat ID from a link or ID
def get_chat_id(chat_reference):
    # If chat_reference is a link, get the ID from the link
    if chat_reference.startswith("https://t.me/"):
        return chat_reference.split("/")[-1]
    # If chat_reference is a numeric chat ID, return it
    elif chat_reference.isdigit():
        return chat_reference
    # If chat_reference is neither a link nor a numeric chat ID, return None
    else:
        return None

# Function to handle the /start command
def start_command(update, context):
    message = update.message
    chat_id = message.chat.id
    command = message.text.strip().lower()
    command_parts = command.split()
    if len(command_parts) == 2:
        command_arg = command_parts[1]
        target_chat_id = get_chat_id(command_arg)
        if target_chat_id is not None:
            chat_to_track[chat_id] = target_chat_id
            context.bot.send_message(chat_id=chat_id, text=f"Now tracking the chat with ID: {target_chat_id}")
        else:
            context.bot.send_message(chat_id=chat_id, text="Invalid format for link or chat ID.")
    else:
        context.bot.send_message(chat_id=chat_id, text="Invalid command format. Use /start link_or_chat_ID")

# Function to handle new messages in the chat
def handle_new_message(update, context):
    message = update.message
    chat_id = message.chat.id
    text = message.text

    # Check if this chat is being tracked
    if chat_id in chat_to_track:
        target_chat_id = chat_to_track[chat_id]

        if text and "https://privnote.com" in text:
            # Send "typing" action to notify the user of screenshot upload
            context.bot.send_chat_action(chat_id=chat_id, action='typing')
            time.sleep(1)

            # Open the link in a headless browser using Selenium
            options = Options()
            options.add_argument("--headless")  # Open the browser in the background
            driver = webdriver.Chrome(options=options)
            driver.get(text)

            # Take a screenshot of the opened page
            screenshot_file = "screenshot.png"
            driver.save_screenshot(screenshot_file)

            # Send the screenshot to Telegram
            context.bot.send_photo(chat_id=chat_id, photo=open(screenshot_file, "rb"))

            # Close the browser and remove the screenshot file
            driver.quit()
            os.remove(screenshot_file)

# Create an instance of Updater and register the /start command and new message handlers
update_queue = Queue()
updater = Updater(TOKEN, update_queue=update_queue)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler("start", start_command))
dispatcher.add_handler(MessageHandler(Filters.text, handle_new_message))

# Start the bot and begin message polling
updater.start_polling()
updater.idle()
