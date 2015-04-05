"""
Class that represents an picture containing the measurement of a sensor
"""
__author__ = 'Cesar'

import googleapiclient.discovery as api_discovery
import httplib2
from StringIO import StringIO
import credentials
from PIL import Image


class Picture():

    pic = Image
    reading_id = ''

    def __init__(self, reading_id):
        """
        Image object constructor. Gets the reading from the Cloudstore
            :param: reading_id: the URLsafe Datastore identifier of the reading provided by the user
            :return: Image from the reading
        """
        http = httplib2.Http()
        c = credentials.get_credentials()
        if c:
            s = api_discovery.build('storage', 'v1', http=c.authorize(http))
            r = s.objects().get_media(bucket='ocr-test-pics', object=reading_id)
            resp = r.execute()
            self.pic = Image.open(StringIO(resp))
            self.reading_id = reading_id
        else:
            print 'Error getting credentials'

    def get_reading_id(self):
        """
        Gets the reading_id associated with the picture.
            :return: reading_id (string)
        """
        return self.reading_id