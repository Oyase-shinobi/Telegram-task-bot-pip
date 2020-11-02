import time as timer
from abc import abstractmethod
from typing import List

import requests
import telegram
from requests import Response
from telegram import InlineKeyboardButton
from telegram.ext import JobQueue
from telegramtaskbot.Tasks.GenericTask import GenericTask


class UrlTask(GenericTask):
    """
    A task based on a http request.

    Attributes
    ----------
    job_name : str
        the name of the task

    disable_notifications : bool
        bool if notifications should be disabled or not

    url : str
        the url where the data for the message lies

    Methods
    ----------
    callback(self, context: telegram.ext.CallbackContext) -> None
        Execute the task and use the context to send the message.

    get_actual_value(self, joblist: [], update: telegram.Update, context: telegram.ext.CallbackContext) -> None
        Returns the current value for the task.

    get_actual_value_cmd(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None
        Called whe tapping on the button to get the actual value

    handle_get_actual_value(self, context: telegram.ext.CallbackContext, chat_id: str) -> None
        Writes te actual walue to the given context and chat_id

    get_data(self) -> str
        Returns the data/message text to be send

    handle_response(self, response: Response) -> str
        Handles the response and transforms it into the message text to be send

    get_response(self) -> Response
        Returns the response for the given url

    get_inline_keyboard(self) -> List[InlineKeyboardButton]
        Returns the list of buttons to be shown
    """

    job_name: str
    disable_notifications = True
    url: str

    def callback(self, context: telegram.ext.CallbackContext) -> None:
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

    def get_actual_value(self, joblist: [], update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        """Function for te mapping to send the actual value after button is pressed."""

        self.handle_get_actual_value(
            context, update.callback_query.message.chat_id)

    def get_actual_value_cmd(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        """Handles command to get the actual value."""

        self.handle_get_actual_value(context, update.message.chat_id)

    def handle_get_actual_value(self, context: telegram.ext.CallbackContext, chat_id: str) -> None:
        """Send the actual value/message with the given context to the chat_id."""

        self.logger.debug(
            f'Get actual value from {self.job_name} for {chat_id}')
        data = self.get_data()
        self.logger.debug(
            f'Send message to {chat_id} with content: \"{" ".join(data.splitlines())}\"')
        context.bot.send_message(chat_id=chat_id, text=data)

    def get_data(self) -> str:
        """Returns the data to be send as message."""

        return self.handle_response(self.get_response())

    @abstractmethod
    def handle_response(self, response: Response) -> str:
        """Handle the given response and return the actual message to be send."""

        pass

    def get_response(self) -> Response:
        """Returns the response for the set url."""

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

    def get_inline_keyboard(self) -> List[InlineKeyboardButton]:
        """Returns a List[InlineKeyboardButton] containing all the relevant buttons."""

        buttons = [
            InlineKeyboardButton(
                f"Get actual Value for {self.job_name}", callback_data=self.job_actual_value),
        ]
        if self.show_subscribe_buttons:
            buttons.append(InlineKeyboardButton(
                f"Subscribe for {self.job_name}", callback_data=self.job_start_name))
            buttons.append(InlineKeyboardButton(
                f"Unsubscribe for {self.job_name}", callback_data=self.job_stop_name))
        return buttons
