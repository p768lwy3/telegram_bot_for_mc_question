import logging
import os
import pandas as pd
import random
import re
import time
import telegram

from bot.CONFIG import config
from bot.DBCONFIG import con, cur

def __question__(bot, update, args):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    if len(args) <= 0:
        query = 'SELECT * FROM HKDSEMATH ORDER BY RAND() LIMIT 1;'
        cur.execute(query)
        result = cur.fetchall()
        year = result[0][1]; qnumber = result[0][2]; qpath = result[0][4]
        update.message.reply_text(('%s, Q.%s' % (year, qnumber)))
        bot.send_photo(chat_id = chat_id, photo = open(qpath, 'rb'))
        config['logger'].info('  > Action: /question, From user: %s' % (user_id))
    
    else:
        r = re.compile('^[0-9]{6}$')
        search = ', '.join(list(filter(r.match, args)))
        if not search:
            update.message.reply_text('似乎冇你 search 嘅嘢')
            config['logger'].info('  > Action: /question Error, From user: %s' % (user_id))
            return
        query = 'SELECT * FROM HKDSEMATH WHERE Qid in ({0});'.format(search)
        cur.execute(query)
        results = cur.fetchall()
        if not results:
            update.message.reply_text('似乎冇你 search 嘅嘢')
            config['logger'].info('  > Action: /question Error, From user: %s' % (user_id))
            return
        for row in results:
            year = row[1]; qnumber = row[2]; qpath = row[4]
            update.message.reply_text('%s, Q.%s' % (year, qnumber))
            bot.send_photo(chat_id = chat_id, photo = open(qpath, 'rb'))
            config['logger'].info("  > Action: /question %s-%s, From user: %s" 
                    % (year, qnumber, user_id))                
            time.sleep(2)
    return

def __check__(bot, update, args):
    if not args:
        update.message.reply_text('/check yyyyqq')
        return
    user_id = update.message.from_user.id
    r = re.compile('^[0-9]{6}$')
    search = ', '.join(list(filter(r.match, args)))
    query = 'SELECT * FROM HKDSEMATH WHERE Qid in ({0});'.format(search)
    cur.execute(query)
    results = cur.fetchall()
    if not results:
        update.message.reply_text('似乎冇你 search 嘅嘢')
        config['logger'].info('  > Action: /question Error, From user: %s' % (user_id))
        return
    for row in results:
        year = row[1]; qnumber = row[2]; ans = row[3]
        update.message.reply_text('%s, Q.%s, Ans: %s.' % (year, qnumber, ans))
        config['logger'].info("  > Action: /check %s-%s, From user: %s" 
            % (year, qnumber, user_id))   
        time.sleep(2)          
    return

def __unknown__(bot, update):
    bot.send_message(chat_id = update.message.chat_id, text = '無呢個 Command。想知有咩 Command 就用 /help 。')
    config['logger'].info('  > Action: Unknown Command, From user: %s' % (update.message.from_user.id))
    return

def __help__(bot, update):
    text = ('/question YYYYQQ YYYYQQ... 查題目 \n' \
            '/question random gen 一題 \n')
    bot.send_message(chat_id = update.message.chat_id, text = text)
    config['logger'].info('  > Action: call /help, From user: %s' % (update.message.from_user.id))
    return
