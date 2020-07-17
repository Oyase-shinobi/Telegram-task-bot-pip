import time as timer
from abc import abstractmethod

import requests
import telegram
from telegram.ext import JobQueue

from requests import Response
from telegram import InlineKeyboardButton

from telegramtaskbot.Tasks.GenericTask import GenericTask


class UrlTask(GenericTask):
    disable_notifications = True
    url: str

    def callback(self, context: telegram.ext.CallbackContext):
        self.logger.info(f'Run {self.job_name}')
        users = self.load_users()
        response_message = self.get_data()
        self.logger.info(f'Notifying {len(users)} users for {self.job_name}')
        for user in users:
            try:
                self.logger.info(f'Notifying {user}')
                context.bot.send_message(chat_id=user, text=response_message,
                                         disable_notification=self.disable_notifications)
            except telegram.TelegramError as e:
                self.logger.info(f'Error occurred while notifying {user}')
                self.logger.error(e.message)

    def get_actual_value(self, joblist: [], update: telegram.Update, context: telegram.ext.CallbackContext):
        self.handle_get_actual_value(context, update.callback_query.message.chat_id)

    def get_actual_value_cmd(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        self.handle_get_actual_value(context, update.message.chat_id)

    def handle_get_actual_value(self, context: telegram.ext.CallbackContext, chat_id: str):
        self.logger.debug(f'Get actual value from {self.job_name} for {chat_id}')
        data: str = self.get_data()
        self.logger.debug(f'Send message to {chat_id} with content: \"{" ".join(data.splitlines())}\"')
        context.bot.send_message(chat_id=chat_id, text=data)

    def get_data(self):
        return self.handle_response(self.get_response())

    @abstractmethod
    def handle_response(self, response: Response):
        pass

    def get_response(self):
        count = 0
        response = requests.get(self.url)
        if response.status_code != 200:
            while response.status_code != 200:
                timer.sleep(2)
                resp = requests.get(self.url)
                count += 1
                response = resp
        self.logger.debug(f'{self.job_name} tried for {count} times')
        return response

    def get_inline_keyboard(self):
        buttons = [
            InlineKeyboardButton(f"Get actual Value for {self.job_name}", callback_data=self.job_actual_value),
        ]
        if self.show_subscribe_buttons:
            buttons.append(InlineKeyboardButton(f"Subscribe for {self.job_name}", callback_data=self.job_start_name))
            buttons.append(InlineKeyboardButton(f"Unsubscribe for {self.job_name}", callback_data=self.job_stop_name))
        return buttons
