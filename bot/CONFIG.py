import logging
logging.basicConfig(format='%(asctime)s - %(name)s -  %(levelname)s: \n %(message)s', level = logging.INFO)

config = {
    'TGTOKEN': '424469480:AAGho7jan2s5NKKXHQNDtIrughhjdR0EGr8',
    'INPUT': './data/',
    'START': 2017,
    'END': 2017,
    'logger': logging.getLogger(__name__)
}

