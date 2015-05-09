"""
A class containing the details of a number detection by VMXserver
"""
__author__ = 'cesar'

import config


class Detection:
    center = ()
    beginX = None
    endX = None
    score = None
    value = None

    @classmethod
    def is_detection(cls, obj):
        """
        Determines if an object supplied qualifies as a detection.
            :param obj: JSON response from VMXserver containing the info of a detection candidate
            :return: True all criteria is met, False otherwise
        """
        if obj['score'] > config.MINIMUM_SCORE_FOR_DETECTION:
            return True
        else:
            return None

    def __init__(self, obj):
        """
        Determines if an object supplied qualifies as a detection and if does returns the detection object.
            :param obj: JSON response from VMXserver containing the info of a detection candidate
            :return: Detection object if all criteria is met, Exception otherwise
        """
        if self.is_detection(obj):
            center_x = int(int(obj['bb'][0])+int(obj['bb'][2])/2)
            center_y = int(int(obj['bb'][1])+int(obj['bb'][3])/2)
            self.center = (center_x, center_y)

            self.score = float(obj['score'])
            self.value = int(obj['name'])

            self.beginX = int(obj['bb'][0])
            self.endX = int(obj['bb'][2])

        else:
            config.logging.debug('Criteria not met for [{0}] detection. Score: {1}'.format(int(obj['name']),
                                                                                           float(obj['score'])))
            raise FalseDetectionException('False Detection')


class FalseDetectionException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
