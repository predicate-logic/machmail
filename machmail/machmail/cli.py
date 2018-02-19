#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Command line wrapper
"""

# stock libs
import os
import sys
import click
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
        self.force_run = False
        self.profile = None


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
    f = force_run_option(f)
    f = verbose_option(f)
    f = quiet_option(f)
    return f


@click.group()
@click.version_option(version=__version__)
def cli():
    pass


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
		  'https://mail.google.com/', 
		  'https://www.googleapis.com/auth/gmail.modify']
CLIENT_SECRET_FILE = '../../client_secret.json'
APPLICATION_NAME = 'machinima-gmail-utility'


def get_credentials():
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
    credential_path = os.path.join(credential_dir,
                                   settings.APPLICATION_NAME)

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        log.warn("Invalid (or non-existent) OAuth credentials for this app."
                 "Please authorize this app via the webrowser page that will"
                 "popup now.")
        flow = client.flow_from_clientsecrets(settings.CLIENT_SECRET_FILE, settings.SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, settings.FLAGS)
        log.warn('Storing credentials to {}'.format(credential_path))
    return credentials

@cli.command("setup-oauth")
def setup_oauth():
    get_credentials()

# @cli.command("get-sub-properties")
# @click.argument("property")
# def get_sub_properties(property):
#     """
#     Get sub properties for a property
#     """
#     properties = [k for k in settings.PROPERTY_MAP.keys()]
#     if property in properties:
#         print('\n'.join([item for item in settings.PROPERTY_MAP[property]]))
#     else:
#         print('Property: "{}" not found.'.format(property))
#         print('Current Properties: {}'.format(properties))
# 
# 
# @cli.command("get")
# @common_options
# @pass_state
# @click.argument("property")
# @click.argument("sub-property")
# @click.argument("start-time")
# @click.argument("end-time")
# @click.option('--format',
#               type=click.Choice(['csv', 'tsv', 'json', 'text', 'clipboard']),
#               default='text', help="output format")
# @click.option('--delimiter', type=click.STRING,
#               help='Field delimiter, defaults to tab delimited.', default='|')
# @click.option('--output', type=click.STRING,
#               help="path to output file, supports S3 uri as well.",
#               default='-')
# @click.option('--redshift-url', type=str, envvar='REDSHIFT_URL',
#               help='Of the form redshift+psycopg2://...')
# @click.option('--dry-run', is_flag=True, default=False,
#               help='Do not insert records into database.')
# @click.option('--batch', type=str, default=settings.BATCH_ID,
#               help='Batch id saved to data file if --output specified.')
# @click.option('--workers', type=int, default=settings.WORKERS,
#               help='# of processes to run in parallel.')
# @click.option('--tmpdir', type=str, help="Location of receiptlog files during processing.")
# def get(state, format, delimiter, output, batch, redshift_url, property, sub_property,
#         start_time, end_time, workers, tmpdir, dry_run):
#     """Get object from somewhere and put it into the db """
# 
#     try:
#         # outer try/except block, must wrap all function code to prevent leakage.
# 
#         tmpdir = '/tmp/' if not tmpdir else os.environ.get('TMPDIR') or tmpdir
# 
#         if not os.path.exists(tmpdir):
#             log.warn("Temp directory: {} doesn't exist.  Set --tmpdir flag to a directory that exists".format(tmpdir))
#             sys.exit(-1)
# 
#         log.warn("Temporary files will be written to: {}".format(tmpdir))
# 
#         try:
#             # need to write this bit to process the object/data from ETL
#             df = etl.get_object()
#             etl.output_dataframe(df, format, delimiter, output, state.profile, batch)
# 
#         except Exception as e:
#             log.exception(e)
#             sys.exit(-1)
# 
#     except Exception as e:
#         log.exception(e)
#         sys.exit(-1)


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
