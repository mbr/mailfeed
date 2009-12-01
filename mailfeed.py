#!/usr/bin/env python
# coding=utf8
#
# Copyright (c) 2009 Marc Brinkmann
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

from werkzeug import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException

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

def show_mailbox(mailbox_name):
	mb = mailboxes[mailbox_name]

	# login
	con = IMAP4_SSL(mb['host'])
	con.login(mb['user'], mb['password'])

	code, data = con.select(mb['folder'])
	code, data = con.search(None, 'ALL')
	msgids = data[0].split(' ')

	s = ''

	# get most recent (by id)
	r, msgs = con.fetch(','.join(msgids[mb['limit']*-1:]),'(RFC822)')
	for m in msgs:
		if 1 == len(m): continue # what the hell is this?
		rfc_message = StringIO(m[1])
		m = rfc822.Message(rfc_message)
		s += m.getheader('Subject')
		s += rfc_message.read()
	return Response(s, mimetype='text/plain')

def index():
	return Response('hello', mimetype='text/plain')

url_map = Map([
	Rule('/', endpoint=index),
	Rule('/mailbox/<mailbox_name>', endpoint=show_mailbox)
])

@Request.application
def app(request):
	urls = url_map.bind_to_environ(request.environ)
	try:
		endpoint, args = urls.match()
		return endpoint(**args)
	except HTTPException, e:
		print "caught:",repr(e)
		return e
	
if __name__ == '__main__':
	from werkzeug import run_simple
	run_simple('localhost', 4000, app, use_reloader = True)

#for mb in mailboxes:
#	print "Processing mailbox",mb['name']
#
#	# login
#	con = IMAP4_SSL(mb['host'])
#	con.login(mb['user'], mb['password'])
#
#	code, data = con.select(mb['folder'])
#
#	code, data = con.search(None, 'ALL')
#
#	i = 0
#
#	# get most recent (by id)
#	r, msgs = con.fetch('1:%d' % mb['limit'],'(RFC822)')
#	for m in msgs:
#		if 1 == len(m): continue # what the hell is this?
#		rfc_message = StringIO(m[1])
#		m = rfc822.Message(rfc_message)
#		print m.getheader('Subject')
#		print rfc_message.read()
