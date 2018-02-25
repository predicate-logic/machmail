from argparse import Namespace

TIMEOUT=600

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/<APPLICATION_NAME>.json
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
                    'https://mail.google.com/',
                    'https://www.googleapis.com/auth/gmail.modify']
APPLICATION_NAME = 'machinima-gmail-utility'

FLAGS = Namespace(auth_host_name='localhost', auth_host_port=[8080, 8090],
                  logging_level='ERROR', noauth_local_webserver=False)

# default search for 
# search docs: https://support.google.com/mail/answer/7190?hl=en
# DEFAULT_QUERY = 'from:mfwilson@gmail.com has:attachment newer_than:2d'
# DEFAULT_QUERY = 'has:attachment newer_than:2d'
DEFAULT_QUERY = 'label:UNREAD'
