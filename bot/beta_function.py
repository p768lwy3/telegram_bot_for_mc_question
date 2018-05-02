def custom_keyboard(inputs):
    custom_keyboard = []; l = []
    for idx, i in enumerate(inputs):
        l.append(InlineKeyboardButton(i, callback_data=i))
        if (idx+1) % 2 == 0 or (idx+1) == len(inputs):
            custom_keyboard.append(l)
            l = []
    return custom_keyboard
    
def __selfquestion__(bot, update, args):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    reply_markup = InlineKeyboardMarkup(custom_keyboard(args))
    bot.send_message(chat_id=chat_id,
                     text='Plz Choose: ',
                     reply_markup=reply_markup)
    return

