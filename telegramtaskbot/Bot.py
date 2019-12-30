import json
import logging
import os
from typing import List

import telegram
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, Filters, CallbackQueryHandler

logging.basicConfig(filename='telegramTaskBot.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


class TelegramTaskBot(object):
    jobs: List[telegram.ext.Job] = []
    default_button_list: List[InlineKeyboardButton] = []
    cmd_fun = {}
    job_names = {}

    def __init__(self, tasks: []):
        load_dotenv()
        self.updater = Updater(token=os.getenv('BOT_TOKEN'), use_context=True)
        self.dispatcher = self.updater.dispatcher
        default_filter = self.get_default_filter()
        self.dispatcher.add_handler(CommandHandler('start', self.start, default_filter))
        self.dispatcher.add_handler(CallbackQueryHandler(self.handle_button, default_filter))

        self.TASKS = [task(self.updater.job_queue) for task in tasks]

        for task in self.TASKS:
            self.cmd_fun[task.job_start_name] = task.start
            self.cmd_fun[task.job_stop_name] = task.stop
            self.default_button_list.extend(task.get_inline_keyboard())
            if task.generic:
                self.dispatcher.add_handler(CommandHandler(task.job_start_name, task.start_command, default_filter))
                self.dispatcher.add_handler(CommandHandler(task.job_stop_name, task.stop_command, default_filter))

        self.load_from_json()

    @staticmethod
    def get_default_filter():
        str_value = os.getenv('ALLOWED_USERS')
        if 'any' in str_value or 'ANY' in str_value:
            default_filter = None
        else:
            allowed_users = [int(i) for i in str_value.split(',')]
            default_filter = Filters.user(user_id=allowed_users)
        return default_filter

    def start(self, update, context):
        reply_markup = InlineKeyboardMarkup(self.build_menu(self.default_button_list, n_cols=2))
        context.bot.send_message(chat_id=update.effective_chat.id, text=os.getenv('START_MESSAGE'),
                                 reply_markup=reply_markup)

    def run(self):
        self.updater.start_polling(clean=True)

    def handle_button(self, update, context):
        query = update.callback_query
        self.cmd_fun.get(query.data)(self.jobs, update, context)
        self.save_to_json()
        logging.info('after save')

    def load_from_json(self):
        try:
            with open('saved_jobs.json') as json_file:
                data = json.load(json_file)
                for job in data['jobs']:
                    for task in self.TASKS:
                        if task.job_name == job['name']:
                            task._start(self.jobs, self.updater.job_queue, job['context'])
                logging.info(f'Loaded {len(data["jobs"])} from JSON')
        except IOError:
            logging.info("File not accessible")

    def save_to_json(self):
        data = {'jobs': []}
        for job in self.jobs:
            data['jobs'].append({
                'context': job.context,
                'name': job.name,
            })
        with open('saved_jobs.json', 'w') as outfile:
            json.dump(data, outfile)

    @staticmethod
    def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
        if header_buttons:
            menu.insert(0, header_buttons)
        if footer_buttons:
            menu.append(footer_buttons)
        return menu
