__author__ = 'cesar'

import config
from apiclient.discovery import build
from apiclient.errors import HttpError
import httplib2
import credentials
import time
import threading

from worker import Worker


def _get_task_from_queue():
    """
    Gets and leases one available tasks from the pull task queue.
        :return: Leased Task.
    """
    try:
        http = httplib2.Http()
        c = credentials.get_credentials()
        if c:
            task_api = build('taskqueue', 'v1beta2', http=c.authorize(http))
            lease_req = task_api.tasks().lease(project='ocr-backend',
                                               taskqueue='image-processing-queue',
                                               leaseSecs=60,
                                               numTasks=1)
            result = lease_req.execute()
            if 'items' in result:
                return result['items']
            else:
                return None

        else:
            config.logging.error('Error getting credentials')
    except httplib2.ServerNotFoundError as e:
        config.logging.error('HTTP Error {0}'.format(e.message))
        return None

    except HttpError as e:
        config.logging.error('HTTP Error {0}'.format(e.message))
        return None

    except Exception as e:
        config.logging.error('Unknown Error {0}'.format(e.message))
        return None

while True:
    tasks = _get_task_from_queue()
    if tasks is not None:
        task = tasks[0]
        config.logging.info('Assigning Task: {0}'.format(task['id']))
        payload = task['payloadBase64'].decode('base64')
        w = Worker(task['id'], payload)
        # spawn a new thread for the new worker to do his thing
        work_thread = threading.Thread(target=w.do_your_thing)
        work_thread.daemon = True
        work_thread.start()
    else:
        config.logging.debug('No tasks available')
    time.sleep(config.POLLING_INTERVAL)