"""
Class that represents a worker process to get the digits from a picture containing the measurement of a sensor
"""
__author__ = 'cesar'

from picture import Picture
from detection import Detection
from apiclient.discovery import build
import requests

VMX_SERVER = 'http://vmx-server.ddns.net:80'
MODEL = '560e632c54953b2729ed7c4c951529861b99'


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
        r = requests.get('{0}/process_image?image={1}&model={2}'.format(VMX_SERVER, self.pic.get_public_url(), MODEL))
        if r.status_code == 200:
            number = []
            objects = r.json()['objects']
            for o in objects:
                if Detection.is_detection(o):
                    number.append(Detection(o))
            reading = ''
            for num in sorted(number, key=lambda n: n.center):
                reading += str(num.value)
            print 'Number in image [{0}]: {1}'.format(self.pic.get_public_url(), reading)
            try:
                r = self._post_result_to_app_engine()
                if r:
                    print 'Result successfully posted to AppEngine!'
                else:
                    print '->>> Something is wrong!'
            except Exception as e:
                # TODO: Retry request ..
                print 'Can not post result to AppEngine, retry task!'
                print e.__str__()

        else:
            print(r.status_code)

    def _post_result_to_app_engine(self, result):
        """
        Notifies the main app in app engine by calling its API. app engine is responsible of deleting the task from
        the task queue after successfully updating the reading entity on the datastore
            :return: True if success, Exception otherwise
        """
        api_root = 'https://ocr-backend.appspot.com/_ah/api'
        api = 'backend'
        version = 'v1'
        discovery_url = '%s/discovery/v1/apis/%s/%s/rest' % (api_root, api, version)
        print discovery_url
        backend = build(api, version, discoveryServiceUrl=discovery_url)

        payload = {"error": "",
                   "result": result,
                   "task_name": self.task_name,
                   "task_payload": self.task_payload
                   }

        request = backend.meter().create(body=payload)
        response = request.execute()
        print response
        if response['ok'] == 'true':
            return True
        else:
            raise Exception

