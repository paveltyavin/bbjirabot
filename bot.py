from telegram.ext import Updater
import logging
from api import Api
import settings

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class Bot(object):
    start_text = """Здравствуйте.

У меня только один интерфейс.
Просто наберите номер версии релиза, и я напишу вам номера тасков и небольшое описание.
Например, годится запрос '26'"""
    def start(self, bot, update):
        bot.sendMessage(update.message.chat_id, text=self.start_text)

    def help(self, bot, update):
        bot.sendMessage(update.message.chat_id, text=self.start_text)

    def echo(self, bot, update):
        telegram_username = update.message.from_user.name

        jira_username = settings.TELEGRAM_TO_JIRA.get(telegram_username)

        if jira_username:
            version_name = update.message.text
            issues = self.a.get_issues(version_name=version_name, username=jira_username)
            response_text = "\n".join(["{}browse/{} - {}".format(
                settings.JIRA_URL,
                issue.key,
                issue.fields.summary,
            ) for issue in issues])
            if response_text == "":
                response_text = "Пусто"
            bot.sendMessage(update.message.chat_id, text=response_text)
        else:
            response_text = 'Ваш телеграм логин не ассоциирован ни с каким jira логином.'

        bot.sendMessage(update.message.chat_id, text=response_text)

    def error(bot, update, error):
        logger.warn('Update "%s" caused error "%s"' % (update, error))

    def __init__(self):
        self.a = Api()

        # Create the EventHandler and pass it your bot's token.
        updater = Updater(settings.TELEGRAM_TOKEN)

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        # on different commands - answer in Telegram
        dp.addTelegramCommandHandler("start", self.start)
        # dp.addTelegramCommandHandler("help", help)

        # on noncommand i.e message - echo the message on Telegram
        dp.addTelegramMessageHandler(self.echo)

        # log all errors
        dp.addErrorHandler(self.error)

        # Start the Bot
        updater.start_polling()

        # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()


if __name__ == '__main__':
    bot = Bot()
