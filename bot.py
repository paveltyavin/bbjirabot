from telegram.ext import Updater
import logging
from api import Api
import settings

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class Bot(object):
    telegram_to_jira = {}
    pending_telegram_to_jira = set([])
    # Define a few command handlers. These usually take the two arguments bot and
    # update. Error handlers also receive the raised TelegramError object in error.
    def start(self, bot, update):
        bot.sendMessage(update.message.chat_id, text='Hi!')

    def help(self, bot, update):
        bot.sendMessage(update.message.chat_id, text='Help!')

    def echo(self, bot, update):
        telegram_username = update.message.from_user.name

        if telegram_username in self.pending_telegram_to_jira:
            jira_username = update.message.text
            self.telegram_to_jira[telegram_username] = jira_username
            if jira_username not in self.a.members:
                response_text = 'Такой пользователь не найден в группе {} . Попробуйте еще раз'.format(settings.JIRA_GROUP)
                logger.info(response_text)
                bot.sendMessage(update.message.chat_id, text=response_text)
                return

            logger.info('telegram_username = {} . jira_username = {}'.format(telegram_username, jira_username))
            bot.sendMessage(update.message.chat_id, text='Спасибо. Теперь можно указать версию релиза, по которой вы хотите найти таски')
            self.pending_telegram_to_jira.remove(telegram_username)
            return

        jira_username = self.telegram_to_jira.get(telegram_username)
        if jira_username is None:
            bot.sendMessage(
                update.message.chat_id,
                text='Напишите ваше Имя пользователя в jira, пожалуйста. Его можно найти тут {}{}'.format(
                    settings.JIRA_URL, 'secure/ViewProfile.jspa'
                )
            )
            logger.info('telegram_username = {} . No jira_username'.format(telegram_username))
            self.pending_telegram_to_jira.add(telegram_username)
        else:
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

    def error(bot, update, error):
        logger.warn('Update "%s" caused error "%s"' % (update, error))

    def __init__(self):
        self.a = Api()
        self.telegram_to_jira = settings.TELEGRAM_TO_JIRA

        # Create the EventHandler and pass it your bot's token.
        updater = Updater(settings.TELEGRAM_TOKEN)

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        # on different commands - answer in Telegram
        # dp.addTelegramCommandHandler("start", start)
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
