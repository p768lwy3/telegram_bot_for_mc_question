import logging
logging.basicConfig(format='%(asctime)s - %(name)s -  %(levelname)s: \n %(message)s', level = logging.INFO)

config = {
    'TGTOKEN': '',
    'INPUT': './data/',
    'START': 2017,
    'END': 2017,
    'logger': logging.getLogger(__name__)
}

