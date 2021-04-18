"""Helper functions for imap/smtp connections"""
import imaplib
import logging
import smtplib

log = logging.getLogger(__name__)


def make_imap_connection(config):
    # Connect to the server
    hostname = config["hostname"]
    log.debug("Connecting to IMAP server {0}".format(hostname))
    connection = imaplib.IMAP4_SSL(hostname)

    # Login to our account
    username = config["username"]
    password = config["password"]
    log.debug("Logging in to IMAP as {0}".format(username))
    connection.login(username, password)

    return connection


def make_smtp_connection(config):
    # Connect to the server
    hostname = config["hostname"]
    log.debug("Connecting to SMTP server {0}".format(hostname))
    connection = smtplib.SMTP_SSL(hostname)

    # Login to our account
    username = config["username"]
    password = config["password"]
    log.debug("Logging in to SMTP as {0}".format(username))
    connection.login(username, password)

    return connection
