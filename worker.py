"""
Class that represents a worker process to get the digits from a picture containing the measurement of a sensor
"""
__author__ = 'cesar'

from picture import Picture


class Worker():

    pic = Picture
    task_name = ''
    task_payload = ''

    def __init__(self, task_name, task_payload):
        """
        Worker constructor. Prepares the picture to work on.
            :param task_name:
            :param task_payload:
            :return: A Worker object
        """
        self.task_name = task_name
        self.task_payload = task_payload
        p, image_name = task_name.split('--')
        self.pic = Picture('{0}.jpg'.format(image_name))

    def do_your_thing(self):
        """
        Self managed thread that makes the necessary work to get the digits from the user provided picture. At the
        end calls _post_result_to_app_engine to notify app engine about the result of the processing.
            :return:
        """
        print 'Reporting for Duty! to work on: {0}'.format(self.pic.get_public_url())

    def _post_result_to_app_engine(self, result):
        """
        Notifies the main app in app engine by calling its API. app engine is responsible of deleting the task from
        the task queue after successfully updating the reading entity on the datastore
            :return: True if success, Exception otherwise
        """
