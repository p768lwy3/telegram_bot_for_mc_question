from collections import Counter, OrderedDict
import datetime
import os
import pandas as pd
import random
import re
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler


from bot.CONFIG import config
from bot.DBCONFIG import con, cur

queid_cache = {}
greply = range(0)

# start, reset, cancel
def __print__(bot, update, chat_data):
    """
    chat_id = update.message.chat_id
    print(chat_data.get('start'))
    print(chat_data.get('admin'))
    print(chat_data.get('member'))
    print(chat_data.get('qstart'))
    print(chat_data.get('record'))
    """
    print(queid_cache)
    return

def __start__(bot, update, chat_data):
    global queid_cache
    user_id = update.message.from_user.id
    if chat_data.get('start') == True:
        update.message.reply_text('開始左！開始埋右！請用 /join 參加！')
        config['logger'].info('  > Action: /gamestart Error (with started game), ' \
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
    queid_cache[user_id] = {'chat_id': chat_id, 'queid': None} 
    query = ('INSERT INTO TELEGRAM (`Userid`, `Username`) VALUES ( {0}, "{1}")' 
          + 'ON DUPLICATE KEY UPDATE Username = VALUES(Username);').format(user_id, username)
    cur.execute(query)
    con.commit()
    update.message.reply_text('開始！其他人可以用 /join 參加！')
    config['logger'].info('  > Action: /gamestart, From user: %s' % (user_id))
    return

def __reset__(bot, update, chat_data):
    user_id = update.message.from_user.id
    if chat_data.get('start') != True:
        update.message.reply_text('都未開始！ /gamereset 乜嘢？')
        config['logger'].info('  > Action: /gamereset Error (without start), ' \
            ' From user: %s' % (user_id))
        return
    if not user_id in chat_data['admin']:
        update.message.reply_text('Sorry！唔係 Admin 真係大唔曬！')
        config['logger'].info('  > Action: /gamereset Error (without permission), ' \
            ' From user: %s' % (user_id))
        return
    
    # rmk. need a Y/N to confirm the reset
    chat_id = update.message.chat_id
    chat_data['qstart'] = False
    for user_id in chat_data['member']:
        chat_data['record'][user_id] = 0
    update.message.reply_text('Reset 左！')
    config['logger'].info('  > Action: /gamereset, From user: %s' % (user_id))
    return

def __cancel__(bot, update, chat_data):
    user_id = update.message.from_user.id
    if chat_data.get('start') != True:
        update.message.reply_text('都未開始！ /gamecancel 乜嘢？')
        config['logger'].info('  > Action: /gamecancel Error (without start), ' \
            ' From user: %s' % (user_id))
        return
    if not user_id in chat_data['admin']:
        update.message.reply_text('Sorry！唔係 Admin 真係大唔曬！')
        config['logger'].info('  > Action: /gamecancel Error (without permission), ' \
            ' From user: %s' % (user_id))
        return
    for k in list(chat_data):
        del chat_data[k]
    chat_id = update.message.chat_id
    update.message.reply_text('/gamecancel 左')
    config['logger'].info('  > Action: /gamecancel, From user: %s' % (user_id))
    return

# join, kick, quit, administration
def __join__(bot, update, chat_data):
    global queid_cache
    user_id = update.message.from_user.id
    
    if chat_data.get('start') in [None, False]:
        update.message.reply_text('仲未 /gamestart ')
        config['logger'].info('  > Action: /join Error (without start), ' \
            ' From user: %s' % (user_id))
        return
    if user_id in chat_data['member']:
        update.message.reply_text('/join 左！ /join 埋右！')
        config['logger'].info('  > Action: /join Error (joined), ' \
            'From user: %s' % (user_id))
        return
    
    chat_id = update.message.chat_id
    username =  update.message.from_user.username
    username = user_id if username == None else username
    
    chat_data['member'].append(user_id)
    chat_data['record'].setdefault(user_id, 0)
    queid_cache[user_id] = {'chat_id': chat_id, 'queid': None}
    query = ('INSERT INTO TELEGRAM (`Userid`, `Username`) VALUES ( {0}, "{1}")' 
          + 'ON DUPLICATE KEY UPDATE Username = VALUES(Username);').format(user_id, username)
    cur.execute(query)
    con.commit()
    update.message.reply_text('%s 參加左！' % (username))
    config['logger'].info('  > Action: /join, From user: %s' % (user_id))
    return

def __kick__(bot, update, args, chat_data):
    global queid_cache
    user_id = update.message.from_user.id
    
    if chat_data.get('start') in [None, False]:
        update.message.reply_text('仲未 /gamestart ')
        config['logger'].info('  > Action: /kick Error (without start), ' \
            ' From user: %s' % (user_id))
        return
    if not user_id in chat_data['admin']:
        update.message.reply_text('冇權呀！')
        config['logger'].info('  > Action: /kick Error (without permission), '\
            ' From user: %s' % (user_id))
        return
    
    if not args:
        update.message.reply_text('請 /kick @Username 或者 @Userid ')
        config['logger'].info('  > Action: /kick Error, ' \
            ' From user: %s' % (user_id))        
        return
    try:    
        uname = args[0].replace('@', '')
        query = 'SELECT Userid FROM TELEGRAM WHERE Username = "{0}"'.format(uname)
        cur.execute(query)
    except (UnicodeError) as e:
        update.message.reply_text('請使用 @Username 或者 @Userid ')
        config['logger'].info('  > Action: /kick Error, ' \
            ' From user: %s' % (user_id))
        return 
        
    uid = cur.fetchall()[0][0]

    if not uid in chat_data['member']:
        update.message.reply_text('未 /join ')
        config['logger'].info('  > Action: /kick Error (without join), ' \
            ' From user: %s' % (user_id))
        return
    
    chat_id = update.message.chat_id
    chat_data.get('member').remove(uid)
    chat_data.get('record').pop(uid, None)
    queid_cache.pop(user_id)
    update.message.reply_text('踢死左！')
    if uid in chat_data.get('admin'):
        chat_data['admin'].remove(uid)
    config['logger'].info('  > Action: /kick, From user: %s' % (user_id))
    
    if len(chat_data['member']) <= 0:
        chat_data['start'] = False
        chat_data['qstart'] = False
    
    return

def __quit__(bot, update, chat_data):
    pass


def __addadmin__(bot, update, args, chat_data):
    user_id = update.message.from_user.id
    if chat_data.get('start') in [None, False]:
        update.message.reply_text('未 /gamestart ')
        config['logger'].info('  > Action: Add admin Error (without /gamestart), '\
            ' From user: %s' % (user_id))
        return
    if not args:
        update.message.reply_text('請使用 @Username 或者 @Userid ')
        config['logger'].info('  > Action: Add admin Error (without username), '\
            ' From user: %s' % (user_id))
        return
    
    if not user_id in chat_data['admin']:
        update.message.reply_text('Admin 先可以加 Admin')
        logger.info('  > Action: /addadmin Error (without permission), '\
            ' From user: %s' % (user_id))
    try:    
        uname = args[0].replace('@', '')
        query = 'SELECT Userid FROM TELEGRAM WHERE Username = "{0}"'.format(uname)
        cur.execute(query)
    except (UnicodeError) as e:
        update.message.reply_text('請使用 @Username 或者 @Userid ')
        config['logger'].info('  > Action: /addadmin Error, ' \
                ' From user: %s' % (user_id))
        return
    
    uid = cur.fetchall()[0][0]
    if not uid or not uid in chat_data['members']:
        update.message.reply_text('%s 未 /join ' % (uname))
        config['logger'].info('  > Action: Add %s to admin Error (without /join), '\
            ' From user: %s' % (uname, user_id))
    elif uid in chat_data['members'] and uid in chat_data['admin']:
        update.message.reply_text('%s 已經係Admin...' % (uname))
        config['logger'].info('  > Action: Add admin Error, '\
            " From user: %s" % (user_id))
    else:
        update.message.reply_text('Add 左 %s 入 Admin' % (username))
        chat_data['admin'].append(uid)
        config['logger'].info('  > Action: Add %s to admin, '\
            " From user: %s" % (uname, user_id))
    return

"""
def __kickadmin__(bot, update):
    pass
"""

# game
def __grecord__(bot, update, chat_data):
    user_id = update.message.from_user.id
    
    if chat_data.get('start') in [None, False]:
        config['logger'].info('  > Action: Cancel Error (without /start), '\
            'From user: %s' % (user_id))
        update.message.reply_text('未 /gamestart ')
        return
    
    ordered_dict = OrderedDict(sorted(chat_data['record'].items(),
                                      key = lambda x: x[1],
                                      reverse = True))
    string = '依家戰果. 名 (成續) \n'
    for i, (k, v) in enumerate(ordered_dict.items()):
        query = ('SELECT Username FROM TELEGRAM WHERE Userid = {0};').format(k)
        cur.execute(query)
        uname = cur.fetchall()[0][0]
        string += '{0}. {1} ({2}) \n'.format(i + 1, uname, v)
    update.message.reply_text(string)
        
    config['logger'].info("  > Action: Check Record, User: %s" % (user_id))
    return

def __gquestion__(bot, update, chat_data):
    global queid_cache
    user_id = update.message.from_user.id
    
    if chat_data.get('start') in [None, False]:
        config['logger'].info('> Action: Question Error (Without /gamestart), '\
            ' From user: %s' % (user_id))
        update.message.reply_text('未 /gamestart')
        return
    if not user_id in chat_data['admin']:
        config['logger'].info('> Action: Question Error (Without permission), '\
            ' From user: %s' % (user_id))
        update.message.reply_text('You 唔是 admin...')
        return
    if chat_data['qstart'] == True:
        config['logger'].info('> Action: Question start Error, '\
            ' From user: %s' % (user_id))
        update.message.reply_text('已經問緊')
        return
    
    chat_data['qstart'] = True  
    chat_id = update.message.chat_id
    
    query = 'SELECT * FROM HKDSEMATH ORDER BY RAND() LIMIT 1;'
    cur.execute(query)
    result = cur.fetchall()
    qid = result[0][0]; year = result[0][1]; qnumber = result[0][2]; qpath = result[0][4]
    
    qdate = datetime.datetime.now().strftime('%Y-%m-%d')
    query = ('INSERT INTO QUERECORD (`QDate`, `Qid`, `Userid`) '
           + 'VALUES ("{0}", {1}, {2})'.format(qdate, qid, user_id))
    cur.execute(query)
    con.commit()

    update.message.reply_text('{0}年第{1}題：'.format(year, qnumber))
    bot.send_photo(chat_id=chat_id, photo=open(qpath, 'rb'))

    keyboard = [[InlineKeyboardButton('A', callback_data='A'),
                 InlineKeyboardButton('B 啱架啦，拍定手先啦！', callback_data='B')],
                [InlineKeyboardButton('C', callback_data='C'),
                 InlineKeyboardButton('D', callback_data='D')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    player_id = chat_data['member']
    for p in player_id:
        queid_cache[p]['queid'] = cur.lastrowid
        bot.send_message(chat_id = p, text = '{0}年第{1}題：'.format(year, qnumber))
        bot.send_photo(chat_id = p, photo = open(qpath, 'rb'))
        bot.send_message(chat_id = p, text = 'Answer is: ', reply_markup = reply_markup)
        
    config['logger'].info("  > Action: Question %s-%s, "\
        " From user: %s" % (year, qnumber, user_id))
        
    return greply

def __greply__(bot, update):
    global queid_cache
    
    query = update.callback_query
    chat_id = query.message.chat.id
    user_id = query.message.chat.id
    message_id = query.message.message_id
    reply = query.data
    
    bot.edit_message_text(text = ('答左: %s ' % (reply)),
                          chat_id = chat_id,
                          message_id = message_id)
    
    queid = queid_cache[user_id]['queid']
    adate = datetime.datetime.now().strftime('%Y-%m-%d')
    query = ('INSERT INTO ANSRECORD (`Qid`, `ADate`, `Userid`, `Reply`) '
           + 'VALUES ({0}, "{1}", {2}, "{3}")').format(queid, adate, user_id, reply)
    cur.execute(query)
    con.commit()
    
    config['logger'].info('  > Action: answer-%s, User: %s' % (reply, user_id))
    return


def __gcheckans__(bot, update, chat_data):
    global queid_cache

    user_id = update.message.from_user.id
    if chat_data.get('start') in [None, False]:
        update.message.reply_text('未 /gamestart')
        config['logger'].info('  > Action: Check Error (Without /start), '\
            'From user: %s' % (user_id))
        return
    if not user_id in chat_data['admin']:
        update.message.reply_text('You 唔是 admin...')
        config['logger'].info('  > Action: Check Error (Without permission), '\
            ' From user: %s' % (user_id))
        return
    if chat_data['qstart'] in [None, False]:
        update.message.reply_text('未 /gamequestion')
        config['logger'].info('  > Action: Check Error (witout /gamequestion), '\
            ' From user: %s' % (user_id))
        return
    
    chat_id = update.message.chat_id
    chat_data['qstart'] = False
    queid = queid_cache[user_id]['queid']

    query = ('SELECT D.Ans FROM HKDSEMATH D, QUERECORD Q '
          + 'WHERE Q.ID = {0} AND D.Qid = Q.Qid;').format(queid)
    cur.execute(query)
    ans = cur.fetchall()[0][0]
    
    query = 'SELECT ID, Userid, Reply FROM ANSRECORD WHERE Qid = {0};'.format(queid)
    cur.execute(query)
    results = cur.fetchall()
    
    if not results:
        update.message.reply_text('都冇人答，你係咪弱智???')
        config['logger'].info('  > Action: /checkans Error (without answer), '\
            ' From user: %s' % (user_id))
        return
 
    for row in results:
        if row[2] == ans:
            bot.send_message(chat_id = row[1], text = '岩左！')
            query = 'UPDATE ANSRECORD SET Correct = 1 WHERE ID = {0};'.format(row[0])
            cur.execute(query)
        else:
            bot.send_message(chat_id = row[1], text = '錯左！')
            query = 'UPDATE ANSRECORD SET Correct = 0 WHERE ID = {0};'.format(row[0])
            cur.execute(query)         
    con.commit()

    string = '正確答案係： {0} \n'.format(ans)
    string += 'No. Name. Result. \n'
    query = ('SELECT T.Userid, Username, A.Correct FROM ANSRECORD A '
           + 'JOIN TELEGRAM T ON A.Userid = T.Userid WHERE A.Qid = {0};').format(queid)
    cur.execute(query)
    results = cur.fetchall()
    for i, row in enumerate(results):
        if row[2] == 1:
            correct = '岩左'
            chat_data['record'][row[0]] += 1
        else:
            correct = '錯左'
        string += '{0}, {1}, {2} \n'.format(i + 1, row[1], correct)
    update.message.reply_text(string)
    '''
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
    '''
    
    return
