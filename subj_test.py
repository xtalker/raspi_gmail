# -*- coding: utf-8 -*-
import feedparser
import urllib2

# Create http basic auth handler
auth_handler = urllib2.HTTPBasicAuthHandler()
auth_handler.add_password('New mail feed', 'https://mail.google.com/',
                          'blurfl', 'b0b5c0de')

# Open url using the auth handler
opener = urllib2.build_opener(auth_handler)
feed_file = opener.open('https://mail.google.com/mail/feed/atom/')

# Parse feed using feedparser
d = feedparser.parse(feed_file)

# Print mail count and mails
print 'Mail count:', d.feed.fullcount

for entry in d.entries:
    print '----------------------------------------------'
    print 'Author: ', entry.author
    print 'Subject:', entry.title
    print 'Summary:', entry.summary
