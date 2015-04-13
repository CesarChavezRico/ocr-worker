"""
Class that represents an picture containing the measurement of a sensor
"""
__author__ = 'Cesar'

import googleapiclient.discovery as api_discovery
from googleapiclient.http import MediaFileUpload
from googleapiclient import errors
import httplib2
from StringIO import StringIO
import credentials
from PIL import Image


class Picture():

    pic = Image
    cropped = Image
    reading_id = ''
    storage_api = None

    def __init__(self, reading_id):
        """
        Image object constructor. Gets the reading from the Cloudstore, also creates the object to interact with the
        storage_api.
            :param: reading_id: the URLsafe Datastore identifier of the reading provided by the user
            :return: Image from the reading
        """
        http = httplib2.Http()
        c = credentials.get_credentials()
        if c:
            self.storage_api = api_discovery.build('storage', 'v1', http=c.authorize(http))
            request = self.storage_api.objects().get_media(bucket='ocr-test-pics', object=reading_id)
            resp = request.execute()
            self.pic = Image.open(StringIO(resp))
            self.reading_id = reading_id
            self.extract_region_of_interest(save=True)
        else:
            print 'Error getting credentials'

    def extract_region_of_interest(self, save=False):
        """
        Crops self.pic to extract the region of interest.
        Crop size is determined as a function of the image size, type of image (red, green, blue .. see CL photo app)
        and the relative size of the region of interest in both X and Y. It is also assumed that the region of interest
        is in the approximate center of the original image.
            :param: save (boolean): is set to True, the cropped image is saved to the data store.
            :return: (None) stores the new image in self.cropped
        """
        redYpercent = .07
        redXpercent = .45

        blueYpercent = .09
        blueXpercent = .55

        greenYpercent = .15
        greenXpercent = .65

        # Determine cut size based on type of image
        # cut_size (portionX, portionY)
        if 'red' in self.reading_id:
            text = 'red'
            cut_size = (self.pic.size[0]*redXpercent, self.pic.size[1]*redYpercent)
        elif 'blue' in self.reading_id:
            text = 'blue'
            cut_size = (self.pic.size[0]*blueYpercent, self.pic.size[1]*blueXpercent)
        elif 'green' in self.reading_id:
            text = 'green'
            cut_size = (self.pic.size[0]*greenYpercent, self.pic.size[1]*greenXpercent)
        else:
            text = 'production'
            cut_size = (self.pic.size[0]*redXpercent, self.pic.size[1]*redYpercent)

        print ('Image Size ({1}) = {0}'.format(self.pic.size, text))

        # image_center (centerX, centerY)
        image_center = self.pic.size[0]/2, self.pic.size[1]/2

        # box (startX, startY, endX, endY)
        box = ((image_center[0]-int(cut_size[0]/2)), (image_center[1]-int(cut_size[1]/2)),
               (image_center[0]+int(cut_size[0]/2)), (image_center[1]+int(cut_size[1]/2)))
        self.cropped = self.pic.crop(box)

        if save:
            try:
                # Save temp file
                self.cropped.save('/home/Cesar/temp/{0}'.format(self.reading_id))
                media_body = MediaFileUpload('/home/Cesar/temp/{0}'.format(self.reading_id),
                                             mimetype='image/jpg')
                body = {
                    'name': self.reading_id
                }
                request = self.storage_api.objects().insert(bucket='ocr-test-pics-cropped',
                                                            body=body,
                                                            media_body=media_body)
                resp = request.execute()
            except errors.HttpError, error:
                print 'An error occurred: %s' % error
            else:
                print 'Image [{0}] saved successfully!!'.format(resp['name'])

    def get_reading_id(self):
        """
        Gets the reading_id associated with the picture.
            :return: reading_id (string)
        """
        return self.reading_id