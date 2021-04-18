# imaprelay

``imaprelay`` is a [Home Assistant](https://www.home-assistant.io/) plug-in to distribute e-mails from one mail box to different recipients.

``imaprelay``, logs into an IMAP account and uses IMAP filters to relay emails from the Inbox to different email addresses via an SMTP server. 
Once relayed, emails are "archived" -- moved out of the inbox into a different folder. 

My use case for this is to provide an unlimited number of e-mail addresses for several users using a single catch-all mailbox of a domain. This way, the users can have throw-away e-mail addresses or different addresses for each account they need to register anywhere.  

It is packaged as Home Assistant plug-in, but you can also just use the  ``imaprelay`` command-line tool that this package provides.

For usage documentation see DOCS.md.

## Bug reporting

Please report bugs [on Github](https://github.com/asoehlke/imaprelay).
