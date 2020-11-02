import json
import logging
from abc import abstractmethod
from datetime import timedelta
from typing import List

import telegram
from telegram import InlineKeyboardButton
from telegram.ext import JobQueue


class Task(object):
    """
    A repeating task.

    Attributes
    ----------

    job_name : str
        the name of the task

    job_start_name : str
        the string identifier of the start command

    job_stop_name : str
        the string identifier of the stop command

    disable_notifications : bool
        bool if notifications should be disabled or not

    generic : bool
        defines if the task looks the same for each user

    first_time : int
        when the first run of the task should be

    repeat_time : timedelta
        the time until the task is rerun

    filename : str
        name for the filename for the to store information/subscribed users

    logger : Logger
        the logger for the task

    Methods
    ----------
    callback(self, context: telegram.ext.CallbackContext) -> None
        Send the message.

    start(self, jobs: List[telegram.ext.Job], update: telegram.Update, context: telegram.ext.CallbackContext) -> None
        Starts the task by button

    start_command(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None
        Starts the task by command

    stop_command(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None
        Stops the task by command

    stop(self, jobs: List[telegram.ext.Job], update: telegram.Update, context: telegram.ext.CallbackContext) -> None
        Stops the task by button

    get_inline_keyboard(self) -> List[InlineKeyboardButton]
        Returns the list of buttons to be shown
    """

    job_name: str
    job_start_name: str
    job_stop_name: str
    disable_notifications: bool = True
    generic: bool = False
    first_time = 0
    repeat_time: timedelta = timedelta(seconds=5)
    filename: str = ''
    logger = logging.getLogger(__name__)

    def __init__(self, job_queue: JobQueue = None) -> None:
        self.job_start_name = 'start_' + self.job_name
        self.job_stop_name = 'stop_' + self.job_name

    @abstractmethod
    def callback(self, context: telegram.ext.CallbackContext) -> None:
        context.bot.send_message(
            chat_id=context.job.context, text=f'Callback from {self.job_name}')

    def start(self, jobs: List[telegram.ext.Job], update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        context.bot.send_message(chat_id=update.callback_query.message.chat_id,
                                 text=f'Setting the job {self.job_name} up')
        self._start(jobs, context.job_queue,
                    update.callback_query.message.chat_id)

    @abstractmethod
    def start_command(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        """Start the task."""

        pass

    @abstractmethod
    def stop_command(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        """Stop the task."""

        pass

    def _start(self, jobs: List[telegram.ext.Job], job_queue: JobQueue, chat_id) -> None:
        new_job = job_queue.run_repeating(
            self.callback, self.repeat_time, context=chat_id, first=self.first_time)
        new_job.name = self.job_name
        jobs.append(new_job)

    def stop(self, jobs: List[telegram.ext.Job], update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        num_jobs = len(jobs)
        chat_id = update.callback_query.message.chat_id
        count = 0
        jobs_to_stop = [job for job in jobs if (
            job.context == chat_id and job.name == self.job_name)]
        for job_to_stop in jobs_to_stop:
            job_to_stop.schedule_removal()
            count += 1
            idx = jobs.index(job_to_stop)
            jobs.pop(idx)
        self.logger.info(
            f' stopped {count} of {num_jobs} jobs for chat_id={chat_id}')

    def get_inline_keyboard(self) -> List[InlineKeyboardButton]:
        """Returns a List[InlineKeyboardButton] containing all the relevant buttons."""

        return [InlineKeyboardButton(f"Start {self.job_name} task", callback_data=self.job_start_name),
                InlineKeyboardButton(
                    f"Stop {self.job_name} task", callback_data=self.job_stop_name),
                ]
