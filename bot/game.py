from collections import Counter, OrderedDict
import os
import pandas as pd
import random
import re
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler

from bot.CONFIG import config

reply_cache = dict()
# rmk, should i form a geneartor to generate a game id???

# start, reset, cancel
def __start__(bot, update, chat_data):
    global reply_cache
    user_id = update.message.from_user.id

    if chat_data.get('start') == True:
        update.message.reply_text('開始左！開始埋右！請用 /join 參加！')
        logger.info('  > Action: /start Error (with started game), ' \
            ' From user: % s' % (user_id))
        return        
    
    chat_id = update.message.chat_id
    username =  update.message.from_user.username
    username = user_id if username == None else username
    
    chat_data['start'] = True
        
    chat_data['admin'] = [user_id]
    chat_data['member'] = [user_id]
    chat_data['qstart'] = False
    chat_data['record'] = {user_id: 0}
    # ??? need to be saved by database?
    chat_data['username'] = {user_id: username}
    # replace this by:
    # query = 'INSERT INTO telegram (`userid`, `username`) VALUES ( {0}, "{1}")'.format(userid, username)
    # cur.execute(query)
    # db.commit()
    reply_cache[chat_id] = {user_id: None}
        
    update.message.reply_text('開始！其他人可以用 /join 參加！')
    logger.info('  > Action: /start, From user: %s' % (user_id))

    return

def __reset__(bot, update, chat_data):
    global reply_cache
    user_id = update.message.from_user_id
    
    if not user_id in chat_data['admin']:
        update.message.reply_text('Sorry！唔係 Admin 真係大唔曬！')
        logger.info('  > Action: /reset Error (without permission), ' \
            ' From user: %s' % (user_id))
        return
    
    if chat_data.get('start') != True:
        update.message.reply_text('都未開始！ /reset 乜嘢？')
        logger.info('  > Action: /reset Error (without start), ' \
            ' From user: %s' % (user_id))
        return
        
    # rmk. need a Y/N to confirm the reset
    # code...
    chat_id = update.message.chat_id
    
    chat_data['qstart'] = False
    for user_id in chat_data['member']:
        chat_data['record'][user_id] = 0
        reply_cache.get(chat_id)[user_id] = None
    
    update.message.reply_text('Reset！')
    logger.info('  > Action: /reset, From user: %s' % (user_id))
    return

def __cancel__(bot, update, chat_data):
    global reply_cache
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    
    if not user_id in chat_data['admin']:
        update.message.reply_text('Sorry！唔係 Admin 真係大唔曬！')
        logger.info('  > Action: /cancel Error (without permission), ' \
            ' From user: %s' % (user_id))
        return
    
    if chat_data.get('start') != True:
        update.message.reply_text('都未開始！ /cancel 乜嘢？')
        logger.info('  > Action: /cancel Error (without start), ' \
            ' From user: %s' % (user_id))
        return
    
    chat_id = update.message.chat_id
    for k, v in chat_data.items():
        del chat_data[k]
    for k, v in reply_cache[chat_id]:
        del reply_cache[chat_id][k]
    
    update.message.reply_text('/cancel 左')
    logger.info('  > Action: /cancel, From user: %s' % (user_id))
        
    return

# join, kick, quit, administration
def __join__(bot, update, chat_data):
    global reply_cache
    user_id = update.message.from_user.id
    
    if chat_data.get('start') in [None, False]:
        update.message.reply_text('仲未 /start ')
        logger.info('  > Action: /join Error (without start), ' \
            ' From user: %s' % (user_id))
        return
    if user_id in chat_data['member']:
        update.message.reply_text('/join 左！ /join 埋右！')
        logger.info('  > Action: /join Error (joined), ' \
            'From user: %s' % (user_id))
    
    chat_id = update.message.chat_id
    username =  update.message.from_user.username
    username = user_id if username == None else username
    
    chat_data['member'].append(user_id)
    chat_data['record'].setdefault(user_id, 0)
    chat_data['username'].setdefault(user_id, username)
    reply_cache.get(chat_id).setdefault(user_id, None)
    update.message.reply_text('%s 參加左！' % (username))
    logger.info('  > Action: /join, From user: %s' % (user_id))
    return

def __kick__(bot, update, args, chat_data):
    global reply_cache
    user_id = update.message.from_user.id
    
    if chat_data.get('start') in [None, False]:
        update.message.reply_text('仲未 /start ')
        logger.info('  > Action: /kick Error (without start), ' \
            ' From user: %s' % (user_id))
        return
    if not user_id in chat_data['admin']:
        update.message.reply_text('冇權呀！')
        logger.info('  > Action: /kick Error (without permission), '\
            ' From user: %s' % (user_id))
        return
        
    target_id = args[0] # some processing    
    if not target_id in chat_data['member']:
        update.message.reply_text('未 /join ')
        logger.info('  > Action: /kick Error (witout join), ' \
            ' From user: %s' % (user_id))
    
    chat_id = update.message.chat_id
    username = update.message.from_user.username
    username = user_id if username == None else username
    
    chat_data['member'].remove(user_id)
    chat_data['record'].pop(user_id, None)
    chat_data['username'].pop(user_id, None)
    reply_cache.get(chat_id).pop(user_id, None)
    return

"""
def __addadmin__(bot, update, args, chat_data):
    user_id = update.message.from_user.id
    if chat_data.get('start') in [None, False]:
        logger.info('> Action: Add admin Error (without /start), User: %s' % (user_id))
        update.message.reply_text('未 /gamestart ')
        return
    if not args:
        logger.info('> Action: Add admin Error (without username), User: %s' % (user_id))
        update.message.reply_text('冇 @username ，格式係 /addadmin @username')
        return
    
    username = args[0].replace('@', '')
    if user_id in chat_data['admin']:
        if chat_data.get('start') in [None, False]:
            logger.info("> Action: Add %s to admin Error (without /gamestart), User: %s" % (username, user_id))
            update.message.reply_text('未 /gamestart ')
    
        else:
            target_id = None
            for k, v in chat_data['usernames'].items():
                if v == username:
                    target_id = k
            
            if target_id == None or not target_id in chat_data['members']:
                logger.info("> Action: Add %s to admin Error (without /join), User: %s" % (username, user_id))
                update.message.reply_text('未 /join ')
    
            elif target_id in chat_data['members'] and target_id in chat_data['admin']:
                logger.info("> Action: Add admin Error, User: %s" % (user_id))
                update.message.reply_text('你已經係Admin...')

            else:
                logger.info("> Action: Add %s to admin, User: %s" % (username, user_id))
                update.message.reply_text('Add 左 %s 入 Admin' % (username))
                chat_data['admin'].append(target_id)
    else:
        logger.info('> Action: Add % s to admin Error (without permission), User: %s' % (username, user_id))
        update.message.reply_text('Admin 先可以加 Admin')
    return
    
def __kickadmin__(bot, update):
    pass
"""

# game
def __grecord__(bot, update, chat_data):
    global reply_cache
    user_id = update.message.from_user.id
    logger.info("> Action: Check Record, User: %s" % (user_id))
    if chat_data.get('start') in [None, False]:
        logger.info('> Action: Cancel Error (without /start), User: %s' % (user_id))
        update.message.reply_text('Not /start game')
    elif chat_data.get('records') != None:
        logger.info('> Action: Check Record, User: %s' % (user_id))
        ordered_dict = OrderedDict(sorted(chat_data['records'].items(),
                                          key = lambda x: x[1],
                                          reverse = True))
        string = '依家戰果. 名 (成續)\n'
        for i, (k, v) in enumerate(ordered_dict.items()):
            string += '{0}. {1} ({2})\n'.format(i + 1, chat_data['usernames'][k], v)
        update.message.reply_text(string)
    else:
        logger.info('> Action: Record Error, User: %s' % (user_id))
        update.message.reply_text('系統問題...')
    return

def __gquestion__(bot, update, chat_data):
    global reply_cache
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    
    if chat_data.get('start') in [None, False]:
        logger.info('> Action: Question Error (Without /start), User: %s' % (user_id))
        update.message.reply_text('未 /gamestart')
        return
    if not user_id in chat_data['admin']:
        logger.info('> Action: Question Error (Without permission), User: %s' % (user_id))
        update.message.reply_text('You 唔是 admin...')
        return
    if chat_data['qstart'] == True:
        logger.info('> Action: Question start Error, User: %s' % (user_id))
        update.message.reply_text('已經問緊')
        return
    
    chat_data['qstart'] = True  
    year = str(random.randint(config['START'], config['END']))
    folder = config['INPUT'] + '{0}/'.format(year)
    qnumber = str(random.randint(1, len(os.listdir(folder)) - 1))
    
    chat_data['year'] = year
    chat_data['qnumber'] = qnumber
    
    logger.info("> Action: Question %s-%s, User: %s" % (year, qnumber, user_id))
    update.message.reply_text('{0}年第{1}題：'.format(year, qnumber))
    bot.send_photo(chat_id=chat_id, photo=open(folder + '{0}.png'.format(qnumber), 'rb'))
    
    keyboard = [[InlineKeyboardButton('A', callback_data='A'),
                 InlineKeyboardButton('B啱架啦，拍定手先啦！', callback_data='B')],
                [InlineKeyboardButton('C', callback_data='C'),
                 InlineKeyboardButton('D', callback_data='D')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    player_id = chat_data['members']
    for p in player_id:
        bot.send_message(chat_id = p, text = '{0}年第{1}題：'.format(year, qnumber))
        bot.send_photo(chat_id = p, photo=open(folder + '{0}.png'.format(qnumber), 'rb'))
        bot.send_message(chat_id = p, text='Answer is: ', reply_markup=reply_markup)
        
    return xresult
    
def __greply__(bot, update):
    global reply_cache
    query = update.callback_query
    chat_id = query.message.chat.id
    user_id = query.message.chat.id
    message_id = query.message.message_id
    
    logger.info('> Action: answer-%s, User: %s' % (query.data, user_id))
    bot.edit_message_text(text = ('答左%s' % (query.data)),
                          chat_id = chat_id,
                          message_id = message_id)
    
    reply_cache[user_id]['reply'] = query.data
    return

def __check_answer__(bot, update, chat_data):
    # it is better to save the user names also.
    # also, it is better to add a admin right for check ans
    global reply_cache
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    if chat_data['start'] in [None, False]:
        logger.info('> Action: Check Error (Without /start), User: %s' % (user_id))
        update.message.reply_text('未 /gamestart')
        return
    if not user_id in chat_data['admin']:
        logger.info('> Action: Check Error (Without permission), User: %s' % (user_id))
        update.message.reply_text('You 唔是 admin...')
        return
    if chat_data['qstart'] in [None, False]:
        logger.info('> Action: Check Error (witout /gamequestion), User: %s' % (user_id))
        update.message.reply_text('未 /gamequestion')
        return
    chat_data['qstart'] = False
    
    keys = []
    for k, v in reply_cache.items():
        if v['chat_id'] == chat_id:
            keys.append(k)
    
    year = chat_data['year']
    qnumber = chat_data['qnumber']
    logger.info("> Action: Check %s-%s, User: %s" % (year, qnumber, user_id))
    try:
        folder = config['INPUT'] + '{0}/'.format(year)
        if not os.path.isdir(folder):
            # check folder exist, if not print no this year...
            update.message.reply_text('冇呢年...')
            return
        
        afile = folder + 'ans.csv'
        if not os.path.exists(afile):
            update.message.reply_text('冇呢年答案...')
            return
        
        d = pd.read_csv(afile)
        # check if the row exist...
        if not (d.index == (int(qnumber) - 1)).any():
            update.message.reply_text('冇呢題答案...')
            return
        
        ans = d.Ans[int(qnumber) - 1]
        
        update.message.reply_text('{0}年第{1}題嘅答案係： {2}'.format(year, qnumber, ans))
    except:
        logger.info('> Action: Check Ans Error, User: %s' % (user_id))
        update.message.reply_text('冇答案...')
        return
    
    chat_data['reply'] = []
    if len(chat_data['reply']) > 0:
        reply.clear()
    string = 'no, id, result \n'
    for i, k in enumerate(keys):
        chat_data['reply'].append(reply_cache[k]['reply'])
        string += '{0}, {1}, {2} \n'.format(i+1, chat_data['usernames'][k], reply_cache[k]['reply'])
        if reply_cache[k]['reply'] == ans:
            chat_data['records'][k] += 1
    
    update.message.reply_text(string)
    
    #plot
    chat_data['reply'] = [v for v in chat_data['reply'] if v != None]
    ChineseFont = FontProperties(fname = './font/hanazono-20130222/HanaMinA.ttf')
    D = dict(Counter(chat_data['reply']))
    plt.bar(range(len(D)), list(D.values()), align='center', alpha=0.5)
    plt.xticks(range(len(D)), list(D.keys()))
    plt.title('{0}年第{1}題'.format(year, qnumber), fontproperties=ChineseFont)
    rfile = './cache/{0}_{1}_{2}.png'.format(chat_id, year, qnumber)
    plt.savefig(rfile)
    
    bot.send_message(chat_id =chat_id, text = '結果：'.format(year, qnumber))
    bot.send_photo(chat_id =chat_id, photo=open(rfile, 'rb'))     
    
    return    
