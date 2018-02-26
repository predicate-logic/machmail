# machmail
Python attachment client for Machinima 

## Setup
On the system where you would like run/test the code.

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
${HOME}/.pyenv/versions/machmail/bin/machmail
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

### Setup Google OAuth 
`machmail` requires OAuth configured.  Follow instructions at [Gmail API Quickstart](https://developers.google.com/gmail/api/quickstart/python) for the GMail account that will be accessed by `machmail`.

Save `client_secret.json` somewhere safe on the system.  Absolute path to this file will be given as the during initial setup of utility.


### Setup `machmail` OAuth
On first run Googles OAuth setup must be configured.  You will need to run this code on a computer with a web-browser configured.  You will also need the fully-qualified path name to the `client_secret` file downloaded as part of the Google OAuth setup.

```
pyenv activate machmail
export PATH="$PATH:${HOME}/.pyenv/versions/machmail/bin/"
machmail setup-oauth /path/to/client_secrets.json
<browser will open on a graphical shell if available>
```
When the browser opens you will be asked to approve the `machmail` app scopes.  You must grant this requests or the script will not work.

In the event that you are authorizing on a computer without a browser you can open a browser on your local computer and point it at the install URL that is printed out during the `machmail setup-oauth ...` process.

Once the app has been authorized a new directory (`~/.credentials`) will store the Google OAuth credentials required for access to this users GMail account.  If for some reason you need to re-authorize this account you can delete the `~/.credentials` directory and re-run the `setup-oauth` steps above.


## Usage

Google's tools use a query format that is detailed [here](https://support.google.com/mail/answer/7190?hl=en).  Using this syntax you can use the `machmail` utility to find emails (with attachements) of interest and then use the utility to download the attachements for a specific email to a path.

### Help
In general you can get help on the `machmail` utility with:

```
cd machmail/machmail
python -m machmail.cli --help
```

Going forward it assumed you are in the `machmail/machmail` sub-directory when you run `python -m machmail.cli`.

For specific `machmail` commands you can get help per command:

```
python -m machmail.cli filter-email --help
```
-
### Filter Messages
For example:

   * From: `foobar@gmail.com`
   * Find all messages that have an attachement that were created in the past 2 days and are UNREAD.
   * Only output the message id's.

```
cd machmail/machmail
python -m machmail.cli filter-email --id-only \
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
python -m machmail.cli filter-email --id-only \
--query "from:foobar@gmail.com has:attachment newer_than:2d subject:Test Filter Text label:UNREAD"

2018-02-19 17:46:58,281 WARNING Response:
161afe491f18b00c
```
Note the returned `msg_id: 161afe491f18b00c`.

Now use this information to retrieve the messages attachement(s) and store them.

```
python -m machmail.cli get-attachments 161afe491f18b00c /tmp/
 
2018-02-19 17:49:04,134 WARNING Wrote: /tmp/invoice_20180219.pdf
2018-02-19 17:49:04,678 WARNING Wrote: /tmp/timecard_20180219.pdf
```

Looks like there were two attachements on this message.  They have now ben stored in `/tmp/` and can be further processed.

**NOTE**: Reteiving a message's attachement(s) with `machmail` will mark it as "read", making it easier to filter it out with subsequent `filter-email` calls.


#### Optional: All-In-One
You could perform both searches together if you would like:

```
for msg_id in $(python -m machmail.cli filter-email --id-only --query "from:foobar@gmail.com has:attachment newer_than:2d subject:Test Filter Text label:UNREAD"); do 
	python -m machmail.cli get-attachments $msg_id /tmp/; 
done

```
-
### Examine Email
You can additionally examine the data for a particular email using this utility as well.  This is less common but could be useful for debugging.

**NOTE**: the example below also sets the email message back to `UNREAD`.  This could be useful to backfill email attachements that had been previously processed with `machmail` and marked as read.

```
python -m machmail.cli get-email --mark-as-unread 161afe491f18b00c

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

