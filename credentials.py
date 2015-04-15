"""
Class that handles all the requirements for authentication within the same GC project
"""
__author__ = 'Cesar'


import requests
from oauth2client import client as oauth2_client


def get_credentials():
    """
    Gets the credentials needed to perform the authentication within the same project
        :return: credentials
    """
    metadata_server = 'http://metadata/computeMetadata/v1/instance/service-accounts'
    service_account = 'default'
    token_uri = '{0}/{1}/token'.format(metadata_server, service_account)
    headers = {'Metadata-Flavor': 'Google'}
    r = requests.get(token_uri, headers=headers)
    if r.status_code == 200:
        d = r.json()
        return oauth2_client.AccessTokenCredentials(d['access_token'], 'my-user-agent/1.0')
    else:
        print r.status_code
        print r.content
        return False
