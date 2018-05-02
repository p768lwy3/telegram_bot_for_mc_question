from bot import action, game, beta_function
from bot.CONFIG import config

import pymysql
import telegram
from telegram.ext import Filters, Updater, CallbackQueryHandler, CommandHandler, MessageHandler, ConversationHandler, InlineQueryHandler

greply = range(0)


if __name__ == "__main__":

    updater = Updater(config['TGTOKEN'])
    dp = updater.dispatcher

    
    # add handler
    dp.add_handler(CommandHandler('question', action.__question__, pass_args = True))
    dp.add_handler(CommandHandler('checkans', action.__check__, pass_args = True))
    dp.add_handler(CommandHandler('gamestart', game.__start__, pass_chat_data = True))
    dp.add_handler(CommandHandler('gamereset', game.__reset__, pass_chat_data = True))
    dp.add_handler(CommandHandler('gamecancel', game.__cancel__, pass_chat_data = True))
    dp.add_handler(CommandHandler('join', game.__join__, pass_chat_data = True))
    #dp.add_handler(CommandHandler('quit', __quit__, pass_user_data = True, pass_chat_data = True))
    dp.add_handler(CommandHandler('kick', game.__kick__, pass_args = True, pass_chat_data = True))
    dp.add_handler(CommandHandler('addadmin', game.__addadmin__, pass_args = True, pass_chat_data = True))
    dp.add_handler(CommandHandler('record', game.__grecord__, pass_chat_data = True))
    dp.add_handler(CommandHandler('gamequestion', game.__gquestion__, pass_chat_data = True))
    dp.add_handler(CommandHandler('gamecheck', game.__gcheckans__, pass_chat_data = True))
    dp.add_handler(CallbackQueryHandler(game.__greply__))

    #dp.add_handler(CommandHandler('selfquestion', __selfquestion__, pass_args = True))
    
    dp.add_handler(CommandHandler('print', game.__print__, pass_chat_data = True))
    dp.add_handler(CommandHandler('help', action.__help__))
    dp.add_handler(MessageHandler(Filters.command, action.__unknown__))
    
    updater.start_polling()
    updater.idle()
