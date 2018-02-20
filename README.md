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

### Checkout `machmail` Utility
Checkout the `machmail` utility from GitHub and install the required Python libraries.  `machmail` is intended to run inside a `pyenv` Python environment.  
```
git clone https://github.com/predicate-logic/machmail
cd machmail
pip install -r machmail/requirements.txt
```

Check that requirements were installed inside the `pyenv` for `machmail`. 
```
pyenv local
```
This should show `machmail` as the current environment.  Running `ipython` from the command-line at this point should show you are running Python 3.6.4.  

If it doesn't then try the setup again and note any errors the previous setup steps show (or call Mike).

### Setup Google OAuth 
`machmail` requires OAuth configured.  Follow instructions at [Gmail API Quickstart](https://developers.google.com/gmail/api/quickstart/python) for the GMail account that will be accessed by `machmail`.

Save `client_secret.json` somewhere safe on the system.  Absolute path to this file will be given as the during initial setup of utility.


### Setup `machmail` OAuth
On first run Googles OAuth setup must be configured.  You will need to run this code on a computer with a web-browser configured.  You will also need the fully-qualified path name to the `client_secret` file downloaded as part of the Google OAuth setup.

```
cd machmail/machmail
python -m setup-oauth /path/to/client_secrets.json
<browser will open now>
```
When the browser opens you will be asked to approve the `machmail` app scopes.  You must grant this requests or the script will not work.


Once you are complete a new directory (`~/.credentials`) will store the Google OAuth credentials required for access to this users GMail account.  If for some reason you need to re-authorize this account you can delete the `~/.credentials` directory and re-run the `setup-oauth` steps above.

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

### Filter Messages
For example:

   * Sent-to `mfwilson@gmail.com`
   * Find all messages that have an attachement that were created in the past 2 days and are unread.
   * Only output the message id's.

```
cd machmail/machmail
python -m machmail.cli filter-email mfwilson@gmail.com --just-ids \
--query "has:attachment newer_than:2d label:UNREAD"
```

If the command throws an error message check that the `--query` parameters are valid.  You can test them online [GMail API Reference](https://developers.google.com/gmail/api/v1/reference/).

### Retrieve Attachments

For example:

   * Find all attachements and store them in `/tmp/`
   * From `mfwilson@gmail.com`
   * Subject: Test Filter Text


First find all of the `msg_id`s that match this query using `filter-email`:

```
python -m machmail.cli filter-email mfwilson@gmail.com --just-ids \
--query "has:attachment newer_than:2d subject:Test Filter Text label:UNREAD"

2018-02-19 17:46:58,281 WARNING Response:
161afe491f18b00c
```
Note the returned `msg_id: 161afe491f18b00c`.

Now use this information to retrieve the messages attachement(s) and store them.

```
python -m machmail.cli get-attachments mfwilson@gmail.com 161afe491f18b00c /tmp/
 
2018-02-19 17:49:04,134 WARNING Wrote: /tmp/invoice_20180219.pdf
2018-02-19 17:49:04,678 WARNING Wrote: /tmp/timecard_20180219.pdf
```

Looks like there were two attachements on this message.  They have now ben stored in `/tmp/` and can be further processed.

**NOTE**: Reteiving a message's attachement(s) with `machmail` will mark it as "read", making it easier to filter it out with subsequent `filter-email` calls.


You could perform both searches together if you would like:

```
for msg_id in $(python -m machmail.cli filter-email mfwilson@gmail.com --just-ids --query "has:attachment newer_than:2d subject:Test Filter Text label:UNREAD"); do 
	python -m machmail.cli get-attachments mfwilson@gmail.com $msg_id /tmp/; 
done

```

### Examine Email
You can additionally examine the data for a particular email using this utility as well.  This is less common but could be useful for debugging.

**NOTE**: example below also sets the email message back to `UNREAD`.  This could be useful to backfill data that had been previously seen.

```
python -m machmail.cli get-email --mark-as-unread mfwilson@gmail.com 161afe491f18b00c

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
                "value": "<mfwilson@gmail.com>"
            },
            {
                "name": "Received",

...
```
