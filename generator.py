#!/usr/bin/env python
# coding: utf-8
# Author:  Ulrich Dangel <mru@spamt.net>
# Modified by: Peter Hasse 
# License: BSD

import sys
import unittest
import datetime
import os

from optparse import OptionParser
import xml.etree.ElementTree as xml_parser
from jinja2 import Environment, FileSystemLoader
import urllib2
import httplib
from urlparse import urlparse


usage = "usage: %prog [options] schedule outputfile\nschedule can be either a URL or filename"
parser = OptionParser(usage=usage)
parser.add_option("-b", "--baseurl", dest="baseurl",
	help="baseurl to generate Links to pentabarf", metavar="URL")
parser.add_option("-v", "--videourl", dest="videourl", help="videourl to generate links to recordings", metavar="VIDEO")
parser.add_option("-i", "--icon", dest="iconurl", help="iconurl to iOS application icon", metavar="ICON")
parser.add_option("-e", "--eventurl", dest="eventurl", help="eventurl to generate links to the event", metavar="EVENT")
parser.add_option("-q", "--quiet", dest="verbose",
  action="store_false", default=True,
  help="dont print a message if data was generated" )
parser.add_option("-d", "--dir", dest="templatedir", default="./templates",
    help="directory to look for the templates", metavar="DIR")
parser.add_option("-t", "--template", dest="template", default="mobile.html",
    help="template to use to generate the data", metavar="FILE")
class Data(object):
    """Just some data object - do not use this in your own projects """
    pass


def parse_file(src):
    (options, args) = parser.parse_args()
    sx = xml_parser.parse(src)
    cx = sx.find('conference')
    conference = Data()
    conference.title = cx.findtext('title')
    day_change = cx.findtext('day_change')
    if not day_change:
      day_change = "0:0"
    day_change = datetime.datetime.strptime(day_change, "%H:%M")
    conference.icon = options.iconurl 
    conference.url = options.eventurl
    conference.start = cx.findtext('start')
    conference.end = cx.findtext('end')
    events = {}
    tracks = {}
    for dx in sx.findall('day'):
        date = datetime.datetime.strptime(dx.get('date'), "%Y-%m-%d")
        events[date] = []
        event_per_room = []
        for rx in dx.findall('room'):
            room = rx.get('name').replace('/', '-').replace(' ', '')

            events_in_room = []
            for ex in rx.findall('event'):
                start_time = datetime.datetime.strptime(ex.findtext('start'), "%H:%M")
                delta = datetime.timedelta()
                if start_time < day_change:
                    delta = datetime.timedelta(days=1)
                start = datetime.datetime.combine(date, start_time.time()) + delta
                e = Data()
                e.pentabarf_id = ex.get('id')
                e.title = ex.findtext('title')
                e.subtitle = ex.findtext('subtitle')
                e.abstract = ex.findtext('abstract')
                e.description = ex.findtext('description')
                e.start = ex.findtext('start')
                e.duration = ex.findtext('duration')

                e.track = ex.findtext('track')
		if not e.track in tracks:
		   tracks[e.track] = []
		tracks[e.track].append(e)
                e.type = ex.findtext('type')
                e.language = ex.findtext('language')
                e.room = room
		e.person = []
		for person in ex.findall('persons/person'):
                	e.person.append(person.text)
                e.slug = ex.findtext('slug')
		tmp_url = options.videourl+room.replace('-', '')+'/h264/'
		tmp_url_parsed = urlparse(tmp_url)
		tmp_file = e.slug+'.mp4'
		conn = httplib.HTTPConnection( tmp_url_parsed.netloc , 80 )
		conn.request( 'HEAD', tmp_url_parsed.path+e.slug+'.mp4' )
		r1 = conn.getresponse()
		conn.close()
		if r1.status == 200:
		    e.videourl = tmp_url+tmp_file
                (hour, minute) = e.duration.split(":")
                duration = datetime.timedelta(hours=int(hour), minutes=int(minute))

                e.duration = duration
                e.start = start
                e.end = e.start + duration
		e.link=[]
		for link in ex.findall('links/link'):
			tmp = '<a href="'+link.get('href')+'">'+link.text+'</a>'
			e.link.append(tmp)
                events_in_room.append(e)
            if events_in_room:
                event_per_room.append({room: events_in_room})
        events[date] = event_per_room
    conference.events = events
    conference.tracks = tracks
    return conference

def main():
    (options, args) = parser.parse_args()
    context = {}

    if not args:
        sys.stderr.write("Specify schedule\n")
        parser.print_help()
        sys.exit(1)
    if args[0].startswith("http"):
        data = urllib2.urlopen(args[0])
        options.baseurl = os.path.dirname(args[0])
    else:
        data = args[0]
    """ Determine output file  """
    if len(args) != 2:
        output = sys.stdout
    else:
        output = open(args[1], "w")

    context['baseurl'] = options.baseurl

    context['conference'] = parse_file(data)
    env = Environment(loader=FileSystemLoader(options.templatedir))
    template = env.get_template(options.template)

    output.write(template.render(context).encode("utf-8"))
    if options.verbose:
        sys.stderr.write("Finished generating file\n")

if __name__=='__main__':
    main()
