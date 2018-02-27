# machmail
Python attachment client for Machinima 

## Setup
On the system where you would like run/test the code you will need to perform the following steps to install the `machmail` command-line script:
   
* Install Python 3.6.4.
* Install `pyenv`.
* Install a Python virtual environment called `machmail` for the user that will run the utility.
* Checkout the `machmail` source from GitHub into `~/build/machmail`
* Build and install the `machmail` utility with the `python setup.py install` command.
* Setup Google OAuth credentials.
* Setup `machmail` OAuth Credentials.
   

### Install `pyenv`
Follow instructions [here](https://github.com/pyenv/pyenv-installer)


### Setup Python 3
```
pyenv install 3.6.4
pyenv virtualenv 3.6.4 machmail
```

### Checkout and Build
Checkout the `machmail` utility from GitHub and install the required Python libraries.  `machmail` is intended to run inside a `pyenv` Python environment. 

```
# login as user that will run machmail

# checkout machmail
cd ~/build
git clone https://github.com/predicate-logic/machmail.git

# install machmail
cd ~/build/machmail/machmail
python setup.py build && python setup.py install

# test
cd ~
pyenv activate machmail
machmail
```

Sucessful Output:

```
Usage: machmail [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  filter-email     Get list of message ids that meet filter...
  get-attachments  Get and store attachment for message
  get-email        Print out the body of an email.
  setup-oauth      Setup OAuth credential cache for app.
``` 
**NOTE**: Although you could append `${HOME}/.pyenv/versions/machmail/bin/` to the `PATH` setup in `.bash_profile` and `.bashrc` for the user so you won't have to specify the full path to the `machmail` binary each time you wish to run it you should consider the following:  

It will still be required to set the Python environment to `machmail` though before the binary can be run (e.g. `pyenv activate machmail`) as it needs access to it's dependencies.  

Although it is possible to install the `machmail` utility into the system Python that Python would need to be 3.5+ and it is not considered "best practice" to install libraries into the system Python with a virtual environment such as `pyenv` provides.

### Setup Google OAuth Credentials
`machmail` requires OAuth configured.  Follow instructions at [Gmail API Quickstart](https://developers.google.com/gmail/api/quickstart/python) for the GMail account that will be accessed by `machmail`.

Save `client_secret.json` somewhere safe on the system.  Absolute path to this file will be given as the during initial setup of utility.


### Setup `machmail` OAuth Credentials
A seperate Python script: `machmail/oauth/generate_credentials.py` is used to generate the OAuth credentials for the `machmail` app.  This script will need access to the `client_secret.json` file (see LastPass) for this app.

From the root of the `machmail` GitHub checkout directory you can find the script in `machmail/machmail/oauth/`

Usage:
```
cd machmail/machmail/machmail
cp /path/to/client_secret.json ./client_secret.json
python generate_credentials.py
<follow on screen instructions>
```

Once the script launches it will print out a URL that you will need to access from a browser.  The local browser on your workstation will do.

The script will also pause at a "Enter Verification code:" prompt.  After granting the necessary permissions via the browser a code will be printed out.  You will then need to copy and paste this code back into the prompt of the script.

Once finished be sure to remove the `client_secret.json` file from this directory for security reasons.  

Once the app has been authorized a new directory (`~/.credentials`) will store the Google OAuth credentials required for access to this users GMail account.  If for some reason you need to re-authorize this account you can delete the `~/.credentials` directory and re-run the `setup-oauth` steps above.

Once the `~/.credentials` directory is in place in the home directory of the user that will run `machmail` you can then use the tool and you will not need to run the OAuth validation procedure again.


## Usage

Google's tools use a query format that is detailed [here](https://support.google.com/mail/answer/7190?hl=en).  Using this syntax you can use the `machmail` utility to find emails (with attachements) of interest and then use the utility to download the attachements for a specific email to a path.


### Help
In general you can get help on the `machmail` utility with:

```
machmail --help
```

NOTE: if the `machmail` tool is being run directly from the Github checkout directory you could also invoke it without installing it:

```
cd ~/build/machmail/machmail/
python -m machmail.cli --help
```

For the rest of the documentation it is assumed that the `machmail` utility has been installed inside of a `pyenv` environment called `machmail` using the `python setup.py install` command.  See instructions above if you haven't peformed this step yet.

For specific `machmail` commands you can get help per command:

```
machmail filter-email --help
```

-

### Filter Messages
For example:

   * From: `foobar@gmail.com`
   * Find all messages that have an attachement that were created in the past 2 days and are UNREAD.
   * Only output the message id's.

```
machmail filter-email --id-only \
--query "from:foobar@gmail.com has:attachment newer_than:2d label:UNREAD"
```

If the command throws an error message check that the `--query` parameters are valid.  You can test them online [GMail API Reference](https://developers.google.com/gmail/api/v1/reference/).

For full syntax for the `--query` parameter see the [GMail Search Syntax Reference](https://support.google.com/mail/answer/7190?hl=en) for more information

-
### Retrieve Attachments

For example:

   * Find all attachements and store them in `/tmp/`
   * From `foobar@gmail.com`
   * Subject: Test Filter Text


First find all of the `msg_id`s that match this query using `filter-email`:

```
machmail filter-email --id-only \
--query "from:foobar@gmail.com has:attachment newer_than:2d subject:Test Filter Text label:UNREAD"

2018-02-19 17:46:58,281 WARNING Response:
161afe491f18b00c
```
Note the returned `msg_id: 161afe491f18b00c`.

Now use this information to retrieve the messages attachement(s) and store them.

```
machmail get-attachments 161afe491f18b00c /tmp/
 
2018-02-19 17:49:04,134 WARNING Wrote: /tmp/invoice_20180219.pdf
2018-02-19 17:49:04,678 WARNING Wrote: /tmp/timecard_20180219.pdf
```

Looks like there were two attachements on this message.  They have now ben stored in `/tmp/` and can be further processed.

**NOTE**: Reteiving a message's attachement(s) with `machmail` will mark it as "read", making it easier to filter it out with subsequent `filter-email` calls.


#### Optional: All-In-One
You could perform both searches together if you would like:

```
for msg_id in $(machmail filter-email --id-only --query "from:foobar@gmail.com has:attachment newer_than:2d subject:Test Filter Text label:UNREAD"); do 
	machmail get-attachments $msg_id /tmp/; 
done

```
-
### Examine Email
You can additionally examine the data for a particular email using this utility as well.  This is less common but could be useful for debugging.

**NOTE**: the example below also sets the email message back to `UNREAD`.  This could be useful to backfill email attachements that had been previously processed with `machmail` and marked as read.

```
machmail get-email --mark-as-unread 161afe491f18b00c

2018-02-19 17:56:10,951 WARNING Response:
{
    "historyId": "11212622",
    "id": "161afe491f18b00c",
    "internalDate": "1519074438000",
    "labelIds": [
        "IMPORTANT",
        "SENT",
        "INBOX"
    ],
    "payload": {
        "body": {
            "size": 0
        },
        "filename": "",
        "headers": [
            {
                "name": "Return-Path",
                "value": "<foobar@gmail.com>"
            },
            {
                "name": "Received",

...
```
-
### Other Resources

   * [GMail API Docs](https://developers.google.com/apis-explorer/#p/gmail/v1/)
   * [GMail API Reference](https://developers.google.com/gmail/api/v1/reference/)
   * [GMail Search Syntax](https://support.google.com/mail/answer/7190?hl=en)
   * [Gmail API Quickstart](https://developers.google.com/gmail/api/quickstart/python)

