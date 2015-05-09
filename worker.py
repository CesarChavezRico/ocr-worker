"""
Class that represents a worker process to get the digits from a picture containing the measurement of a sensor
"""
__author__ = 'cesar'

import config
from picture import Picture
from detection import Detection, FalseDetectionException
from apiclient.discovery import build
import requests

VMX_SERVER = 'http://vmx-server.ddns.net:80'
MODEL = '0c69d0a7b4a3b39d0ba32c8ec67b1f01f5d7'


class Worker():

    pic = Picture
    task_name = ''
    task_payload = ''

    def _is_int(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

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
        reading = ''
        r = requests.get('{0}/process_image?image={1}&model={2}'.format(VMX_SERVER, self.pic.get_public_url(), MODEL))
        if r.status_code == 200:
            number = []
            objects = r.json()['objects']

            for o in objects:
                try:
                    digit = Detection(o)
                except FalseDetectionException:
                    pass
                else:
                    number.append(digit)
                    config.logging.debug('Detected: [{0}] with a score of: {1}'.format(digit.value, digit.score))
            config.logging.debug('End getting digits')

            try:
                # Get digit with highest score
                number.sort(key=lambda n: n.score, reverse=True)
                highest_score = number[0]
                config.logging.debug('The digit with highest score is: {0}, score {1}'
                                     .format(highest_score.value, highest_score.score))

                # Get digit size
                digit_size = highest_score.endX - highest_score.beginX
                config.logging.debug('Digit size = {0}'.format(digit_size))

                # Sort digits according to location on image to generate the reading
                count = 0
                number.sort(key=lambda n: n.center)
                for num in number:
                    if count > 0:
                        pixels_between = num.beginX - number[count-1].endX
                        config.logging.debug('{0} Pixels between {1} and {2}'.format(pixels_between,
                                                                                     number[count-1].value,
                                                                                     num.value))
                        if pixels_between < digit_size*2:
                            # Contiguous digits
                            reading += str(num.value)
                        else:
                            # To much pixels between characters we missed one! =(
                            reading += '_{0}'.format(str(num.value))
                    else:
                        config.logging.debug('Starting distance measurement with: {0}'.format(num.value))
                        reading += str(num.value)
                    count += 1
                config.logging.info('Number in image [{0}]: {1}'.format(self.pic.get_public_url(), reading))

                # Check if reading is good and complete
                if self._is_int(reading):
                    if len(reading) > 4:
                        try:
                            r = self._post_result_to_app_engine(reading)
                            if r:
                                config.logging.info('Result successfully posted to AppEngine!')
                        except Exception as e:
                            # TODO: Retry request ..
                            config.logging.error('Error posting to AppEngine: {0}, retry task!'.format(e.__str__()))
                    else:
                        # Wrong reading notification (Incomplete)
                        raise IndexError
                else:
                    # Wrong reading notification (Not an Int)
                    raise IndexError
            except IndexError:
                config.logging.warning('The response [{0}] is not valid. Something is wrong!'.format(reading))
                try:
                    r = self._notify_error_to_app_engine(reading)
                    if r:
                        config.logging.info('Error successfully notified to AppEngine!')
                except Exception as e:
                    # TODO: Retry request ..
                    config.logging.error('Error posting to AppEngine: {0}, retry task!'.format(e.__str__()))

        else:
            config.logging.error('Error in response from VMXserver: {0}'.format(r.status_code))
            config.logging.error('Error in response from VMXserver content: {0}'.format(r.content))

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
        backend = build(api, version, discoveryServiceUrl=discovery_url)

        payload = {"error": "",
                   "result": result,
                   "task_name": self.task_name,
                   "task_payload": self.task_payload
                   }

        request = backend.reading().set_image_processing_result(body=payload)
        response = request.execute()
        if response['ok']:
            return True
        else:
            config.logging.error('Bad Response from AppEngine: {0}'.format(response))
            raise Exception

    def _notify_error_to_app_engine(self, error):
        """
        Notifies the main app in app engine that there's an error by calling its API. app engine is responsible
        of deleting the task from the task queue after successfully notifying the user that the image sent could not
        be processed.
            :return: True if success, Exception otherwise
        """
        api_root = 'https://ocr-backend.appspot.com/_ah/api'
        api = 'backend'
        version = 'v1'
        discovery_url = '%s/discovery/v1/apis/%s/%s/rest' % (api_root, api, version)
        backend = build(api, version, discoveryServiceUrl=discovery_url)

        payload = {"error": error,
                   "result": 0,
                   "task_name": self.task_name,
                   "task_payload": self.task_payload
                   }

        request = backend.reading().set_image_processing_result(body=payload)
        response = request.execute()
        if response['ok']:
            return True
        else:
            config.logging.error('Bad Response from AppEngine: {0}'.format(response))
            raise Exception
