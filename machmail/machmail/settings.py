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

# CLIENT_SECRET_FILE = '/Users/mwilson/src/predicatelogic/clients/machinima/client_secret.json'
# example query (q) examples
# more here: https://support.google.com/mail/answer/7190?hl=en&visit_id=1-636414433124921064-1340851932&rd=1
DEFAULT_SENDER = 'from:mfwilson@gmail.com' 
DEFAULT_SUBJECT = 'subject:Test Filter Text'
HAS_ATTACHEMENT = 'has:attachement'
DEFAULT_TIME = 'newer_than:2d'
DEFAULT_LABEL = 'processed'

# default search for 
DEFAULT_QUERY = 'has:attachment newer_than:2d'
