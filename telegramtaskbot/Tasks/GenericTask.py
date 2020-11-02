import json
from abc import abstractmethod
from typing import List

import telegram
from telegram.ext import JobQueue
from telegramtaskbot.Tasks.Task import Task


class GenericTask(Task):
    """
    Basic task users can subscribe to.

    Attributes
    ----------   
    job_name : str
        the name of the task

    job_actual_value : str
        the string to get the actual value fo the task

    generic : bool
        defines if the task looks the same for each user

    show_subscribe_buttons : bool
        if the subscribe and unsubscribe buttons should be shown or not

    Methods
    ----------
    callback(self, context: telegram.ext.CallbackContext) -> None
        Execute the task and use the context to send the message.

    start(self, jobs: List[telegram.ext.Job], update: telegram.Update, context: telegram.ext.CallbackContext) -> None
        Starts the task by button

    start_command(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None
        Starts the task by command

    stop_command(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None
        Stops the task by command

    stop(self, jobs: List[telegram.ext.Job], update: telegram.Update, context: telegram.ext.CallbackContext) -> None
        Stops the task by button

    save_user(self, user: str) -> None
        Add the user to the subscriber list

    load_users(self) -> List[str]
        Get all the subscribed users
    """

    job_name: str
    job_actual_value: str
    generic = True
    show_subscribe_buttons = False

    def __init__(self, job_queue: JobQueue = None) -> None:
        super().__init__()
        self.job_actual_value = 'actual_' + self.job_name
        self._start([], job_queue, self.job_name)

    @abstractmethod
    def callback(self, context: telegram.ext.CallbackContext) -> None:
        pass

    def start(self, jobs: List[telegram.ext.Job], update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        self._handle_start(context, update.callback_query.message.chat_id)

    def start_command(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        self._handle_start(context, update.message.chat_id)

    def _handle_start(self, context: telegram.ext.CallbackContext, chat_id: str, with_message: bool = True) -> None:
        if with_message:
            context.bot.send_message(chat_id=chat_id,
                                     text=f'Thank you for subscribing')
        self.save_user(chat_id)
        self.logger.debug(f'User {chat_id} subscribed')

    def stop(self, jobs: List[telegram.ext.Job], update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        self._handle_stop(context, update.callback_query.message.chat_id)

    def stop_command(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        self._handle_stop(context, update.message.chat_id)

    def _handle_stop(self, context: telegram.ext.CallbackContext, chat_id: str, with_message: bool = True) -> None:
        users = self.load_users()
        users.remove(chat_id)
        self._save_to_json(users)
        self.logger.debug(f'User {chat_id} unsubscribed')
        if with_message:
            context.bot.send_message(
                chat_id=chat_id, text=f'You succesfully unsubscribed')

    def save_user(self, user: str) -> None:
        users = self.load_users()
        users.append(user)
        final_users = list(set(users))
        self._save_to_json(final_users)

    def _save_to_json(self, users: List[str]) -> None:
        data = {'users': users}
        with open(self.filename + '.json', 'w+') as outfile:
            json.dump(data, outfile)
        self.logger.debug('Saved User')

    def load_users(self) -> List[str]:
        users = []
        try:
            with open(self.filename + '.json') as json_file:
                data = json.load(json_file)
                users = data['users']
        except IOError:
            users = []
            self.logger.error("File not accessible")
        finally:
            return users
