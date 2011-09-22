#!/usr/bin/env python
import os, sys, datetime, time
import sqlite3
import tvnamer.utils
from appscript import *
import ConfigParser

class iTunesError(Exception):
    """iTunes Error"""
    pass

def mark_watched(show, season, episode):
    playlists = app('iTunes').sources['Library'].playlists()
    for p in playlists:
        if p.name() == 'TV Shows':
            tv = p

    if not tv:
        print "Can't locate TV Shows playlist, exiting"
        raise iTunesError

    found = False

    for t in tv.tracks():
        if (t.show().lower() == show.lower() and
            int(t.season_number()) == int(season) and
            int(t.episode_number()) == int(episode)):
            ep = "%s.s%02ds%02d" % (t.show(), t.season_number(), t.episode_number())
            print 'Marking ep watched: ' + ep
            found = True
            t.unplayed.set(False)
            if(t.played_count() < 1):
                t.played_count.set(1)
    if not found:
        print "Failed to find %s s%02de%02d" % (show, season, episode)
    return found

def mark_file_watched(ep):
    print "Parsing " + ep
    parser = tvnamer.utils.FileParser(ep)
    try:
        episode = parser.parse()
    except tvnamer.tvnamer_exceptions.InvalidFilename:
        print "Invalid filename esception from tvnamer for " + ep
        return

    if episode is not None:
        print "Marking %s s%02de%02d as watched in iTunes" % (episode.seriesname, episode.seasonnumber, episode.episodenumbers[0])
        mark_watched(episode.seriesname, episode.seasonnumber, episode.episodenumbers[0])

def mark_boxee_watched(loc, filename, since):
    conn = sqlite3.connect('/tmp/' + filename)
    cursor = conn.cursor()
    cursor.execute('select strPath, iPlayCount from watched where iLastPlayed > ?', (since, ))
    for r in cursor:
        ep = r[0].rpartition('/')[2]
        mark_file_watched(ep)

def mark_xbmc_watched(loc, filename, since):
    conn = sqlite3.connect('/tmp/' + filename)
    cursor = conn.cursor()
    cursor.execute('select strFilename, playCount from files where lastPlayed > ?', (since, ))
    for r in cursor:
        mark_file_watched(r[0])
            
def main():
    c = ConfigParser.ConfigParser()
    os.system('mkdir -p ' + os.path.expanduser('~/.tvsync.d/'))
    c.read(os.path.expanduser('~/.tvsync.d/players'))

    period = datetime.datetime.now() - datetime.timedelta(days = 30)
    since = time.mktime(period.timetuple())

    for source in c.sections():
        f = c.get(source, 'db')
        print "grabbing " + f
        os.system('rsync "' + f + '" /tmp')

        filename = f[f.rfind('/')+1:]
        dbtype = c.get(source, 'type')

        if dbtype == 'boxee':
            mark_boxee_watched(f, filename, since)
        elif dbtype == 'xbmc':
            mark_xbmc_watched(f, filename, since)

if __name__ == "__main__":
    main()
