from abc import abstractmethod
from typing import List

import telegram
from telegram.ext import JobQueue

from telegramtaskbot.Tasks.Task import Task


class GenericTask(Task):
    job_actual_value: str
    generic = True
    show_subscribe_buttons = False

    def __init__(self, job_queue: JobQueue = None):
        super().__init__()
        self.job_actual_value = 'actual_' + self.job_name

    @abstractmethod
    def callback(self, context: telegram.ext.CallbackContext):
        pass

    def start(self, jobs: List[telegram.ext.Job], update: telegram.Update, context: telegram.ext.CallbackContext):
        self.handle_start(context, update.callback_query.message.chat_id)

    def start_command(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        self.handle_start(context, update.message.chat_id)

    def handle_start(self, context: telegram.ext.CallbackContext, chat_id: str):
        context.bot.send_message(chat_id=chat_id,
                                 text=f'Thank you for subscribing')
        self.save_user(chat_id)
        self.logger.debug(f'User {chat_id} subscribed')

    def stop(self, jobs: List[telegram.ext.Job], update: telegram.Update, context: telegram.ext.CallbackContext):
        self.handle_stop(context, update.callback_query.message.chat_id)

    def stop_command(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        self.handle_stop(context, update.message.chat_id)

    def handle_stop(self, context: telegram.ext.CallbackContext, chat_id: str):
        users = self.load_users()
        users.remove(chat_id)
        self.save_to_json(users)
        self.logger.debug(f'User {chat_id} unsubscribed')
        context.bot.send_message(chat_id=chat_id, text=f'You succesfully unsubscribed')
