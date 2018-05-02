import logging
import os
import pandas as pd
import random
import re
import time
import telegram

from bot.CONFIG import config

def __question__(bot, update, args):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    
    if len(args) <= 0:
        # This could be change to random.choice(folder_list), 
        # where adding a folder_list in config by search the data folder
        year = str(random.randint(config['START'], config['END']))
        folder = config['INPUT'] + ('%s/' % (year))
        qnumber = str(random.randint(1, len(os.listdir(folder)) - 1))
        update.message.reply_text(('%s, Q.%s' % (year, qnumber)))
        bot.send_photo(chat_id = chat_id, photo = open(folder + ('%s.png' % (qnumber)), 'rb'))
        config['logger'].info('  > Action: /question, From user: %s' % (user_id))
    
    else:
        r = re.compile('^[0-9]{6}$')
        for arg in args:
            if r.match(arg):
                year = arg[:4]
                qnumber = str(int(arg[4:]))
                folder = config['INPUT'] + ('%s/' % (year))
                if not os.path.isdir(folder):
                    update.message.reply_text('冇呢年')
                    config['logger'].info('  > Action: error /question %s %s ' \
                        '(with unknown year), From user: %s' 
                        % (year, qnumber, user_id))
                    continue
                pfile = folder + ('%s.png' % (qnumber))
                if not os.path.exists(pfile):
                    update.message.reply_text('冇呢題')
                    config['logger'].info('  > Action: error /question %s %s ' \
                        ' (with unknown question number), From user: %s' 
                        % (year, qnumber, user_id))
                    continue
                update.message.reply_text('%s, Q.%s' % (year, qnumber))
                bot.send_photo(chat_id = chat_id, photo = open(pfile, 'rb'))
                config['logger'].info("  > Action: /question %s-%s, From user: %s" 
                    % (year, qnumber, user_id))                
            else:
                update.message.reply_text('%s 唔岩格式！請用 /question YYYYQQ ' \
'                   (e.g. 201701) 格式！' % (arg))
                config['logger'].info(" > Action: /question Error (incorrect format), " \
                    " From user: %s" % (user_id))
                continue
            time.sleep(5)
    return

def __check__(bot, update, args):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    r = re.compile('^[0-9]{6}$')
    if len(args) <= 0:
        update.message.reply_text('%s 唔岩格式！請用 /question YYYYQQ ' \
'                   (e.g. 201701) 格式！'% (arg))
        config['logger'].info('  > Action: /check Error (incorrect format), From user: %s' % 
            (user_id))
    else:
        for arg in args:
            if r.match(arg):
                year = arg[:4]
                qnumber = int(arg[4:])
                folder = config['INPUT'] + ('%s/' % (year))
                if not os.path.isdir(folder):
                    update.message.reply_text('冇呢年')
                    config['logger'].info('  > Action: error /check %s %s ' \
                        '(with unknown year), From user: %s' 
                        % (year, qnumber, user_id))
                    continue
                afile = folder + 'ans.csv'
                if not os.path.exists(afile):
                    update.message.reply_text('冇呢年答案')
                    config['logger'].info('  > Action: error /check %s %s ' \
                        ' (with no answer file), From user: %s' 
                        % (year, qnumber, user_id))
                d = pd.read_csv(afile)
                if not (d.index == (qnumber - 1)).any():
                    update.message.reply_text('冇呢題答案')
                    config['logger'].info('  > Action: error /check %s %s ' \
                        ' (with no answer), From user: %s'
                        % (year, qnumber, user_id))
                ans = d.Ans[qnumber - 1]
                update.message.reply_text('%s Q.%s Ans: %s ' % (year, qnumber, ans))
                config['logger'].info('  >Action: /check %s %s ' \
                    ' From user: %s' % (year, qnumber, user_id))
            else:
                update.message.reply_text('%s 唔岩格式！請用 /check YYYYQQ ' \
'                       (e.g. 201701) 格式！'% (arg))
                config['logger'].info('  > Action: /check Error (incorrect format), From user: %s' % 
                    (user_id))
                continue
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

def __answer__(bot, update):
    pass
