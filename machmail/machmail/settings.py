from argparse import Namespace

TIMEOUT=600

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/<APPLICATION_NAME>.json
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
                    'https://mail.google.com/',
                    'https://www.googleapis.com/auth/gmail.modify']
CLIENT_SECRET_FILE = '/Users/mwilson/src/predicatelogic/clients/machinima/client_secret.json'
APPLICATION_NAME = 'machinima-gmail-utility'

FLAGS = Namespace(auth_host_name='localhost', auth_host_port=[8080, 8090],
                  logging_level='ERROR', noauth_local_webserver=False)

