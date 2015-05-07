"""
Configuration file
"""
__author__ = 'Cesar'

import logging

# Logging
logging.basicConfig(format='%(asctime)s - [%(levelname)s]: %(message)s',
                    filename='/home/logs/ocr_worker.log',
                    level=logging.DEBUG)


# Minimum detection level
MINIMUM_SCORE_FOR_DETECTION = 0.1