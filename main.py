from bot import action, game, beta_function
from bot.CONFIG import config

import telegram
from telegram.ext import Filters, Updater, CallbackQueryHandler, CommandHandler, MessageHandler, ConversationHandler, InlineQueryHandler

#xresult = range(0)

if __name__ == "__main__":
    updater = Updater(config['TGTOKEN'])
    dp = updater.dispatcher
    
    # add handler
    dp.add_handler(CommandHandler('question', action.__question__, pass_args = True))
    dp.add_handler(CommandHandler('checkans', action.__check__, pass_args = True))
    dp.add_handler(CommandHandler('help', action.__help__))
    dp.add_handler(MessageHandler(Filters.command, action.__unknown__))
    #dp.add_handler(CommandHandler('check', __check__, pass_args=True))
    
    #dp.add_handler(CommandHandler('gamestart', __gamestart__, pass_chat_data = True))
    #dp.add_handler(CommandHandler('join', __join__, pass_chat_data = True))
    #dp.add_handler(CommandHandler('quit', __quit__, pass_user_data = True, pass_chat_data = True))
    #dp.add_handler(CommandHandler('cancelgame', __cancelgame__, pass_chat_data = True))
    

    #dp.add_handler(CommandHandler('gamequestion', __gamequestion__, pass_chat_data = True))
    #dp.add_handler(CommandHandler('gamerecord', __gamerecord__, pass_chat_data = True))
    #dp.add_handler(CallbackQueryHandler(__Xresult__, pass_chat_data = True))
    #dp.add_handler(
    #dp.add_handler(CommandHandler('addadmin', __addadmin__, pass_args = True, pass_chat_data = True))
    #dp.add_handler(CommandHandler('selfquestion', __selfquestion__, pass_args = True))
    # 
    # dp.add_handler()
    

    #dp.add_handler(InlineQueryHandler(__inlineanswer__))
    
    updater.start_polling()
    updater.idle()
