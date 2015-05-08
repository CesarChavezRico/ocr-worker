"""
Configuration file
"""
__author__ = 'Cesar'

import logging

# Logging
logging.basicConfig(format='%(asctime)s - [%(levelname)s]: %(message)s',
                    filename='/home/logs/ocr_worker.log',
                    level=logging.DEBUG)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("googleapiclient").setLevel(logging.WARNING)
logging.getLogger("oauth2client").setLevel(logging.WARNING)

# Minimum detection level
MINIMUM_SCORE_FOR_DETECTION = 0.1


# Time between task polling
POLLING_INTERVAL = 10
