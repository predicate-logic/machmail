#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Command line wrapper
"""

# stock libs
import os
import sys
import json
import click
import base64
import logging
import httplib2
import multiprocessing


# google related libs
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# app specific libs
from machmail import settings
from machmail import __version__
from machmail.util.log import setup_logging
# from machmail.util.mutex import create_mutex_file


setup_logging()
log = logging.getLogger('default')


def set_console_log_level(level):
    """Set log level to increase console verbosity.  Usually for implementing a --verbose flag."""

    # set console logger to a higher logging level
    [h.setLevel(level) for h in log.handlers if type(h) == logging.StreamHandler]
    log.info('Logging level changed to {}.'.format(level))


class State(object):
    def __init__(self):
        self.verbose = 0
        self.quiet = False


pass_state = click.make_pass_decorator(State, ensure=True)


# Shared CLI option(s)
# Set console/file level log verbosity
def verbose_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.verbose = value

        # turn on verbose console logging?
        if state.verbose == 1:
            set_console_log_level(logging.INFO)
            log.warn("Verbose console logging enabled.")
        elif state.verbose == 2:
            set_console_log_level(logging.DEBUG)
            log.warn("Debug console logging enabled.")

        return value

    return click.option('-v', '--verbose', count=True, default=0,
                     expose_value=False, help='Turn on verbose logging.',
                     callback=callback)(f)


# Quiet all output except for errors and output data.
def quiet_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.quiet = value

        if state.quiet:
            set_console_log_level(logging.ERROR)

        return value

    return click.option('-q', '--quiet', is_flag=True,
                     expose_value=False,
                     help='Only show errors or output data to terminal.',
                     callback=callback)(f)


# Shared CLI option(s)
# Disable singleton mutex to prevent multiple simulaneous script runs.
def force_run_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.force_run = value

        if not state.force_run:
            create_mutex_file()

        return value

    return click.option('-r', '--force-run', is_flag=True, default=False,
                     expose_value=False,
                     help='Allow multiple copies of script to run at once.',
                     callback=callback)(f)




def common_options(f):
    f = verbose_option(f)
    f = quiet_option(f)
    return f


@click.group()
@click.version_option(version=__version__)
def cli():
    pass


def get_credentials(client_secrets_file=''):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
    Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, settings.APPLICATION_NAME)

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        log.warn("Invalid (or non-existent) OAuth credentials for this app.  "
           "Please authorize this app via the webrowser page that will"
           "popup now.")
        flow = client.flow_from_clientsecrets(client_secrets_file, settings.SCOPES)
        flow.user_agent = settings.APPLICATION_NAME
        credentials = tools.run_flow(flow, store, settings.FLAGS)
        log.warn('Storing credentials to {}'.format(credential_path))
    else:
        log.info("Credentials: {} exist.  Delete file to "
           "force reauthorization.".format(credential_path))
        return credentials


def get_service():
    """Get GMail service object.
    """

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    return service


@cli.command("setup-oauth")
@click.argument("client-secrets-file")
def setup_oauth(client_secrets_file):
    """Setup OAuth credential cache for app.  Will open a web browser to take
    you through OAuth setup.  """

    get_credentials(client_secrets_file)


@cli.command("filter-email")
@click.argument("user_id")
@click.option("--query", type=str, default=settings.DEFAULT_QUERY,  help='Default filter parameters.')
@click.option('--just-ids', is_flag=True, default=False, help='Only output msg ids')
def filter_email(user_id, query, just_ids):
    """Get list of message ids that meet filter criteria.
    """

    log.info("Query: {}".format(query))
    service = get_service()
    response = service.users().messages().list(userId=user_id,
                                            q=query).execute()

    log.warn("Response:")
    if just_ids:
        for id in [x['id'] for x in response['messages']]:
            print(id)
    else:
        print(response)


@cli.command("get-email")
@click.argument("user-id")
@click.argument("msg-id")
def get_email(user_id, msg_id):
    """Print out the body of an email.  Indicate if it has attachements.
    """
    try:
        service = get_service()
        response = service.users().messages().get(userId=user_id,
                                            id=msg_id).execute()

        log.warn("Response:")
        print(json.dumps(response, indent=4, sort_keys=True))

    except Exception as e:
        log.exception(e)
        sys.exit(-1)

@cli.command("get-attachments")
@click.argument("user-id")
@click.argument("msg-id")
@click.argument("store-dir")
def get_attachments(user_id, msg_id, store_dir):
    """Get and store attachment for message
    """

    try:
        service = get_service()
        response = service.users().messages().get(userId=user_id, id=msg_id).execute()
        for part in response['payload']['parts']:
            if part['filename']:
                if 'data' in part['body']:
                    data=part['body']['data']
                else:
                    att_id=part['body']['attachmentId']
                    att=service.users().messages().attachments().get(userId=user_id, messageId=msg_id,id=att_id).execute()
                    data=att['data']
                    file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                    path = store_dir + part['filename']

                with open(path, 'wb') as f:
                    log.warn('Wrote: {}'.format(path))
                    f.write(file_data)

    except Exception as e:
        log.exception(e)
        sys.exit(-1)


# Must be here for shell invocation to work
if '__main__' == __name__:

    try:

        # prevent script from hanging
        p = multiprocessing.Process(target=cli, name="machmail")
        p.start()

        # wait
        if os.environ.get('TIMEOUT'):
            log.warn("Timeout overridden.  Timeout: {} sec(s)."
            .format(os.environ.get('TIMEOUT')))
        else:
            log.info("Default timeout: {} sec(s).".format(settings.TIMEOUT))

        timeout = int(os.environ.get('TIMEOUT', settings.TIMEOUT))
        p.join(timeout)

        # still running?  possibly hung.  kill.
        if p.is_alive():
            log.error("Watchdog timer triggered: {} seconds.  Process "
             "appears to be hung.  Terminating process."
             .format(timeout))
            p.terminate()
            p.join()
            sys.exit(-1)
        else:
            sys.exit(p.exitcode)

    except Exception as e:
        log.exception(e)
        sys.exit(-1)
