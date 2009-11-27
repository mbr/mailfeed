#!/usr/bin/env python

from imaplib import IMAP4_SSL
import re
import yaml
import rfc822
from StringIO import StringIO

def parse_list_response(line):
	flags, delimiter, mailbox_name = list_response_pattern.match(line).groups()
	mailbox_name = mailbox_name.strip('"')
	return (flags, delimiter, mailbox_name)

config_file_name = 'mailboxes.yaml'

list_response_pattern = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')

mailboxes = yaml.load(file(config_file_name))

for mb in mailboxes:
	print "Processing mailbox",mb['name']

	# login
	con = IMAP4_SSL(mb['host'])
	con.login(mb['user'], mb['password'])

	code, data = con.select(mb['folder'])

	code, data = con.search(None, 'ALL')

	i = 0

	# get most recent (by id)
	r, msgs = con.fetch('1:%d' % mb['limit'],'(RFC822)')
	for m in msgs:
		if 1 == len(m): continue # what the hell is this?
		rfc_message = StringIO(m[1])
		m = rfc822.Message(rfc_message)
		print m.getheader('Subject')
		print rfc_message.read()
