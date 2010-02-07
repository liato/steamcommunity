#!/usr/bin/env python
import datetime
import re
import urllib2
from decimal import Decimal

from lxml import etree

__version__ = '0.1.0'



class User(object):
    def __init__(self, steamid):
        self.steamid = None
        self.steamid64 = None
        self.name = None
        self.customurl = None
        self.privacystate = None
        self.visibilitystate = None
        self.vacbanned = False
        self.ingame = False
        self.ingameinfo = {}
        self.membersince = None
        self.steamrating = 0
        self.hoursplayed2wk = 0
        self.headline = None
        self.realname = None
        self.summary = None
        self.avatar = None

        m = re.match(r'STEAM_[0-1]:[0-1]:[0-9]+$', steamid, re.I)
        if m:
            steamid = steamid[8:].split(':')
            steamid = str(int(steamid[0]) + int(steamid[1]) * 2 + 76561197960265728)
            self.steamid64 = steamid
        else:
            try:
                steamid = int(steamid)
            except ValueError:
                self.customurl = steamid.strip('/').split('/')[-1]
            else:
                self.steamid64 = steamid
        self._get()
    

    def _get(self):
        if self.steamid64:
            url = 'http://steamcommunity.com/profiles/%s?xml=1' % self.steamid64
        else:
            url = 'http://steamcommunity.com/id/%s?xml=1' % self.customurl
        
        try:
            data = urllib2.urlopen(url).read()
        except (urllib2.HTTPError, urllib2.URLError):
            raise SteamCommunityError('Unable to connect to steamcommunity.com')
        
        self._data = etree.fromstring(data)
        data = None
        
        self.steamid64 = int(self._extract('steamID64'))
        self.name = self._extract('steamID')
        self.customurl = self._extract('customURL')
        self.privacystate = self._extract('privacyState')
        self.visibilitystate = self._extract('vicibilityState')
        self.vacbanned = True if self._extract('vacBanned') == 1 else False
        ingameinfo = self._data.find('inGameInfo')
        if ingameinfo is not None:
            self.ingame = True
            self.ingameinfo['ip'] = self._extract('inGameServerIP')
            self.ingameinfo['game'] = self._extract('gameName', ingameinfo)
            self.ingameinfo['link'] = self._extract('gameLink', ingameinfo)
        self.membersince = datetime.datetime.strptime(self._extract('memberSince'), '%B %d, %Y') if self._data.find('memberSince') is not None else None
        self.steamrating = int(self._extract('steamRating')) if self._data.find('memberSince') is not None else 0
        self.hoursplayed2wk = Decimal(self._extract('hoursPlayed2Wk')) if self._data.find('hoursPlayed2Wk') is not None else 0
        self.headline = self._extract('headline')
        self.realname = self._extract('realname')
        self.summary = self._extract('summary')
        self.avatar = self._extract('avatarFull')
        if self.steamid is None:
            steamid = ['STEAM_0', '0', '0']
            steamid64 = self.steamid64 - 76561197960265728
            steamid[2] = steamid64/2
            steamid[1] = steamid64-steamid[2]*2
            self.steamid = ':'.join(str(s) for s in steamid)
        self._data = None
        del self._data

    
    def _extract(self, elem, data = None):
        e = data.find(elem) if data is not None else self._data.find(elem)
        if e is not None:
            return e.text
        return None
        
if __name__ == '__main__':
    from pprint import pprint
    pprint(User('stoff3').__dict__)
    pprint(User('STEAM_0:1:6906860').__dict__)