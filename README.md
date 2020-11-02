# telegram-task-bot
Library to setup telegram bots with recurring tasks.

# Usage
`pip install telegram-task-bot`

## `.env` Variables
1) `ALLOWED_USERS` specifies the users which are allowed, if `any`, every one is allowed to use the bot.
1) `BOT_TOKEN` the token of the bot.
1) `START_MESSAGE` the message to be send as response to the start command.


## Classes
There are several classes included in this Package.

### Task
Base class for recurring tasks.

#### Configuration
* `job_name: str` Name of the job defined in this task
* `disable_notifications: bool` Disable notifications, flag send to the telegram server
* `generic: bool` Defines if the task looks the same for each user 
* `first_time:time` First time to run the task, 0 is now takes a `datetime.time`
* `repeat_time: timedelta` Defines the time between two executions of the job, takes `datetime.timedelta`
* `filename: str` Filename under which data specific to this job should be saved

### GenericTask
More specific class which adds the possiblity to get the actual value and implements user handling.
The data is saved to a `JSON` file.
The callback method ( `callback(self, context: telegram.ext.CallbackContext)`) must be implemented.

### UrlTask
Extension of the `GenericTask` to simplify the usage for jobs calling a URL and returning the link/ response to the subscribers.
It retries every 2 seconds until it gets a response.

This class adds a `url` field where the information lies.

The `handle_response(self, response: Response)` must be implemented to extract the data from the request and return the message string.

# Example Project
https://github.com/bb4L/digitec_daily_bot

# License
[LGPLv3](LICENSE)