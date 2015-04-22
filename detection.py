"""
A class containing the details of a number detection by VMXserver
"""
__author__ = 'cesar'

MINIMUM_SCORE_FOR_DETECTION = 0.3


class Detection:
    center = ()
    score = None
    value = None

    @classmethod
    def is_detection(cls, object):
        """
        Determines if an object supplied qualifies as a detection.
            :param object: JSON response from VMXserver containing the info of a detection candidate
            :return: True all criteria is met, False otherwise
        """
        if object['score'] > MINIMUM_SCORE_FOR_DETECTION:
            return True
        else:
            return None

    def __init__(self, object):
        """
        Determines if an object supplied qualifies as a detection and if does returns the detection object.
            :param object: JSON response from VMXserver containing the info of a detection candidate
            :return: Detection object if all criteria is met, Exception otherwise
        """
        if self.is_detection(object):
            center_x = int(int(object['bb'][0])+int(object['bb'][2])/2)
            center_y = int(int(object['bb'][1])+int(object['bb'][3])/2)
            self.center = (center_x, center_y)

            self.score = float(object['score'])
            self.value = int(object['name'])
        else:
            raise FalseDetectionException


class FalseDetectionException(Exception):
    def __init__(self, value):
        self.value = value
        # TODO logging!! logging.exception('[Reading] - Get Error: '+value, exc_info=True)

    def __str__(self):
        return repr(self.value)
