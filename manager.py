__author__ = 'cesar'

from apiclient.discovery import build
import httplib2
import credentials
import time
import threading

from worker import Worker

POLLING_INTERVAL = 10


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
            print 'Error getting credentials'
    except httplib2.ServerNotFoundError as e:
        print 'error {0}'.format(e.message)
        return None

while True:
    tasks = _get_task_from_queue()
    task = tasks[0]
    if task:
        print 'Assigning Task: {0}'.format(task['id'])
        w = Worker(task['id'], 'pay-load')
        # spawn a new thread for the new worker to do his thing
        work_thread = threading.Thread(target=w.do_your_thing)
        work_thread.daemon = True
        work_thread.start()
    else:
        print 'No tasks available'
    time.sleep(POLLING_INTERVAL)