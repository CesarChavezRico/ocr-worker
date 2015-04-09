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
    cropped = Image
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
            self.extract_region_of_interest()
        else:
            print 'Error getting credentials'

    def extract_region_of_interest(self):
        """
        Crops self.pic to extract the region of interest.
        Crop size is determined as a function of the image size, type of image (red, green, blue .. see CL photo app)
        and the relative size of the region of interest in both X and Y. It is also assumed that the region of interest
        is in the approximate center of the original image.
            :return: (None) stores the new image in self.cropped
        """
        redYpercent = .07
        redXpercent = .45

        blueYpercent = .09
        blueXpercent = .55

        greenYpercent = .15
        greenXpercent = .65

        # Determine cut size based on type of image
        # cut_size
        if 'red' in self.reading_id:
            text = 'red'
            cut_size = (self.pic.size[0]*redXpercent, self.pic.size[1]*redYpercent)
        elif 'blue' in self.reading_id:
            text = 'blue'
            cut_size = (self.pic.size[1]*blueYpercent, self.pic.size[0]*blueXpercent)
        elif 'green' in self.reading_id:
            text = 'green'
            cut_size = (self.pic.size[1]*greenYpercent, self.pic.size[0]*greenXpercent)

        print ('Image Size ({2}) = {0}, {1}'.format(self.pic.size[1], self.pic.size[0], text))

        # order in which we specify the coordinates is:
        # startY:startX, endY:endX

        image_center = self.pic.size[0]/2, self.pic.size[1]/2
        box = ((image_center[1]-cut_size[1]/2), (image_center[0]-cut_size[0]/2),
               (image_center[1]+cut_size[1]/2), (image_center[0]+cut_size[0]/2))
        self.cropped = self.pic.crop(box)

    def get_reading_id(self):
        """
        Gets the reading_id associated with the picture.
            :return: reading_id (string)
        """
        return self.reading_id