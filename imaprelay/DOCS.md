# imaprelay

This program will look for a configuration file in ~/.secret/imaprelay.json -- its location 
should indicate that it needs to contain plain-text passwords for IMAP and SMTP servers, 
and thus the program will exit immediately if the file is group- or world-readable.

The recipient filter can use the criteria listed here: https://pypi.org/project/imap-tools/#search-criteria
Only single key searches are supported.

Forwarding mails can cause some spam related issues. *imaprelay* uses three approaches: 
1. forward using the original sender 
2. replace the sender email address with the "from" address in the configuration
3. if the previous approaches fail, move the mail to the "error" folder and just send a notification email to the recipient. 

The available configuration options are listed below:
```
{
    "imap": {
        "hostname": "imap.myserver.de",
        "username": "...",
        "password": "..."
    },
    "smtp": {
        "hostname": "smtp.myserver.de",
        "username": "...",
        "password": "..."
    },
    "relay": {
        "interval": 10,
        "inbox": "INBOX",
        "archive": "Archive",
        "error": "Error",
        "from": "forwarder@myserver.de",
        "sender": "catchall@myserver.de",
        "recipients" : [
            {
                "name": "Andreas",
                "filter": "TO andreas",
                "to": "andreas@myserver.de"
            },
            {
                "name": "all",
                "filter": "ALL",
                "to": "all-the-rest@myserver.de"
            }
        ]
    }
}
```

