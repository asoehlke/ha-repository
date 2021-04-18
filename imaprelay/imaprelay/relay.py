"""Provides email forwarder Relay class """
import email
import imaplib
import logging
import re
import smtplib
import socket
import time
from email import policy

from connection import make_imap_connection, make_smtp_connection
from util import parse_folder_line

log = logging.getLogger(__name__)

BATCH_SIZE = 10


class RelayError(Exception):
    pass


class IMAPError(RelayError):
    pass


class Relay(object):
    def __init__(self, config):
        self.config = config
        self.inbox = config["relay"]["inbox"]
        self.archive = config["relay"]["archive"]
        self.errorfolder = config["relay"]["error"]
        self.sender = config["relay"]["sender"]
        self.from_ = config["relay"]["from"]

    def relay(self):
        try:
            return self._relay()
        finally:
            self._close_connections()

    def get_next_slice(self, filter):
        data = self._chk(self.imap.search(None, filter))
        msg_ids = [x for x in data[0].split() if x != ""]
        msg_slice, msg_ids = msg_ids[:BATCH_SIZE], msg_ids[BATCH_SIZE:]
        return msg_slice

    def _relay(self):
        if not self._open_connections():
            log.warn("Aborting relay attempt")
            return False

        data = self._chk(self.imap.list())
        folders = [parse_folder_line(line)[2] for line in data]

        if self.inbox not in folders:
            raise RelayError(
                'No "{0}" folder found! Where should I relay messages from?'.format(
                    self.inbox
                )
            )

        if self.archive not in folders:
            raise RelayError(
                'No "{0}" folder found! Where should I archive messages to?'.format(
                    self.archive
                )
            )

        data = self._chk(self.imap.select(self.inbox))
        if data[0] != b"0":
            log.info(
                "Relaying {num} messages from {inbox}".format(
                    num=data[0].decode("utf-8"), inbox=self.inbox
                )
            )

            # Take max BATCH_SIZE messages for each recipient and relay them
            for recipient in self.config["recipients"]:
                msg_slice = self.get_next_slice(recipient["filter"])
                while msg_slice:
                    log.info(
                        "Relaying {num} messages for {recipient}".format(
                            num=len(msg_slice), recipient=recipient["name"]
                        )
                    )
                    self._relay_messages(msg_slice, recipient["to"])
                    msg_slice = self.get_next_slice(recipient["filter"])

        return True

    def _relay_messages(self, message_ids, recipient):
        log.debug("Relaying messages {0}".format(message_ids))

        # Get messages and relay them
        message_ids = b",".join(message_ids)
        msg_data = self._chk(self.imap.fetch(message_ids, "(RFC822)"))

        send_success = False
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                eml = email.message_from_bytes(response_part[1], policy=policy.default)
                originalFrom = eml["from"]

                # make sure there is a reply-to
                try:
                    eml.replace_header("reply-to", eml["reply-to"])
                except KeyError:
                    eml["reply-to"] = eml["from"]

                # replace sender address to avoid DMARC bounce, keep original name
                fromAddress = re.sub(
                    "<.*>", "<{sender}>".format(sender=self.from_), originalFrom
                )
                eml.replace_header("from", fromAddress)

                try:
                    eml.replace_header("sender", self.from_)
                except KeyError:
                    eml["sender"] = self.from_

                try:
                    self.smtp.sendmail(self.sender, recipient, eml.as_bytes())
                    send_success = True
                    log.debug(
                        "Sent message '{subj}' from {from_} to {to}".format(
                            from_=eml["from"], to=recipient, subj=eml["subject"]
                        )
                    )

                except Exception as err:
                    log.error(
                        "Sent message '{subj}' from {from_} to {to} failed: {err}".format(
                            from_=eml["from"],
                            to=recipient,
                            subj=eml["subject"],
                            err=err,
                        )
                    )
                if not send_success:
                    # might have been identified as spam, try with simple from
                    eml.replace_header("from", self.sender)
                    try:
                        self.smtp.sendmail(self.sender, recipient, eml.as_bytes())
                        send_success = True
                        log.debug(
                            "Sent message '{subj}' from {from_} to {to}".format(
                                from_=eml["from"], to=recipient, subj=eml["subject"]
                            )
                        )
                    except Exception as err:
                        log.error(
                            "Sent message '{subj}' from {from_} to {to} failed: {err}".format(
                                from_=eml["from"],
                                to=recipient,
                                subj=eml["subject"],
                                err=err,
                            )
                        )

                if not send_success:
                    try:
                        msg = email.message.EmailMessage()
                        msg["from"] = self.sender
                        msg["to"] = recipient
                        msg[
                            "subject"
                        ] = "forward failed from {from_}: {subject}".format(
                            from_=originalFrom, subject=eml["subject"]
                        )
                        self.smtp.sendmail(self.sender, recipient, msg.as_bytes())
                        log.debug(
                            "Sent error message from {from_} to {to} for {subj}".format(
                                from_=originalFrom, to=recipient, subj=msg["subject"]
                            )
                        )
                    except Exception as err:
                        log.error(
                            "Sent error message from {from_} to {to} for {subj} failed: {err}".format(
                                from_=originalFrom,
                                to=recipient,
                                subj=eml["subject"],
                                err=err,
                            )
                        )

        if send_success:
            # Copy messages to archive folder
            self._chk(self.imap.copy(message_ids, self.archive))
        else:
            # Copy messages to error folder
            self._chk(self.imap.copy(message_ids, self.errorfolder))
            pass

        # Mark messages as deleted on server
        self._chk(self.imap.store(message_ids, "+FLAGS", r"(\Deleted)"))

        # Expunge
        self._chk(self.imap.expunge())

    def loop(self):
        interval = self.config["relay"]["interval"]
        log.info("Start relaying from {0}".format(self.config["imap"]["username"]))

        try:
            while 1:
                r = self.relay()
                t = interval if r else interval * 10
                log.debug("Sleeping for %d seconds", t)
                time.sleep(t)
        except KeyboardInterrupt:
            log.warn("Caught interrupt, quitting!")

    def _open_connections(self):
        try:
            self.imap = make_imap_connection(self.config["imap"])
        except (socket.error, imaplib.IMAP4.error):
            log.exception("Got IMAP connection error!")
            return False

        try:
            self.smtp = make_smtp_connection(self.config["smtp"])
        except (socket.error, smtplib.SMTPException):
            log.exception("Got SMTP connection error!")
            return False

        return True

    def _close_connections(self):
        log.debug("Closing connections")

        try:
            self.imap.close()
        except (imaplib.IMAP4.error, AttributeError):
            pass

        try:
            self.imap.logout()
        except (imaplib.IMAP4.error, AttributeError):
            pass

        try:
            self.smtp.quit()
        except (smtplib.SMTPServerDisconnected, AttributeError):
            pass

    def _chk(self, res):
        typ, data = res
        if typ != "OK":
            raise IMAPError("typ '{0}' was not 'OK!".format(typ))
        return data
