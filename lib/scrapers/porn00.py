from kodi_six import xbmc
import os, six, re
from packlib import kodi, dom_parser2, log_utils
from packlib import cfscrape

from resources.lib.modules import local_utils
from resources.lib.modules import helper

buildDirectory = local_utils.buildDir
urljoin = six.moves.urllib.parse.urljoin

filename = os.path.basename(__file__).split('.')[0]
base_domain = 'http://www.porn00.org'
base_name = base_domain.replace('www.', '');
base_name = re.findall('(?:\/\/|\.)([^.]+)\.', base_name)[0].title()
type = 'scenes'
menu_mode = 218
content_mode = 219
player_mode = 801

search_tag = 1
search_base = urljoin(base_domain, '?s=%s')


@local_utils.url_dispatcher.register('%s' % menu_mode)
def menu():
    try:
        url = base_domain
        scraper = cfscrape.create_scraper()
        c = scraper.get(url).content
        r = dom_parser2.parse_dom(c, 'ul', {'id': 'categorias'})
        r = dom_parser2.parse_dom(r, 'a')
        r = [(i.attrs['href'], i.content) for i in r if i]
        if not r:
            log_utils.log('Scraping Error in %s:: Content of request: %s' % (base_name.title(), str(c)), xbmc.LOGERROR)
            kodi.notify(msg='Scraping Error: Info Added To Log File', duration=6000, sound=True)
            quit()
    except Exception as e:
        log_utils.log('Fatal Error in %s:: Error: %s' % (base_name.title(), str(e)), xbmc.LOGERROR)
        kodi.notify(msg='Fatal Error', duration=4000, sound=True)
        quit()

    dirlst = []

    for i in r:
        try:
            name = kodi.sortX(i[1].encode('utf-8')).title()
            icon = xbmc.translatePath(
                os.path.join('special://home/addons/script.adultflix.artwork', 'resources/art/%s/icon.png' % filename))
            fanarts = xbmc.translatePath(
                os.path.join('special://home/addons/script.adultflix.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append(
                {'name': name, 'url': i[0], 'mode': content_mode, 'icon': icon, 'fanart': fanarts, 'folder': True})
        except Exception as e:
            log_utils.log('Error adding menu item %s in %s:: Error: %s' % (i[1].title(), base_name.title(), str(e)),
                          xbmc.LOGERROR)

    if dirlst:
        buildDirectory(dirlst)
    else:
        kodi.notify(msg='No Menu Items Found')
        quit()


@local_utils.url_dispatcher.register('%s' % content_mode, ['url'], ['searched'])
def content(url, searched=False):
    try:
        scraper = cfscrape.create_scraper()
        c = scraper.get(url).content
        r = dom_parser2.parse_dom(c, 'div', {'class': 'video'})
        r = [(dom_parser2.parse_dom(i, 'a'), \
              dom_parser2.parse_dom(i, 'img', req=['src', 'width', 'height'])) \
             for i in r if i]
        r = [(i[0][0].attrs['href'], i[0][0].attrs['title'], i[1][0].attrs['src']) for i in r if i]
        if (not r) and (not searched):
            log_utils.log('Scraping Error in %s:: Content of request: %s' % (base_name.title(), str(c)), xbmc.LOGERROR)
            kodi.notify(msg='Scraping Error: Info Added To Log File', duration=6000, sound=True)
    except Exception as e:
        if (not searched):
            log_utils.log('Fatal Error in %s:: Error: %s' % (base_name.title(), str(e)), xbmc.LOGERROR)
            kodi.notify(msg='Fatal Error', duration=4000, sound=True)
            quit()
        else:
            pass

    dirlst = []

    for i in r:
        try:
            name = i[1].title()
            if searched:
                description = 'Result provided by %s' % base_name.title()
            else:
                description = name
            content_url = i[0] + '|SPLIT|%s' % base_name
            fanarts = xbmc.translatePath(
                os.path.join('special://home/addons/script.adultflix.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append({'name': name, 'url': content_url, 'mode': player_mode, 'icon': i[2], 'fanart': i[2],
                           'description': description, 'folder': False})
        except Exception as e:
            log_utils.log('Error adding menu item %s in %s:: Error: %s' % (i[1].title(), base_name.title(), str(e)),
                          xbmc.LOGERROR)

    if dirlst:
        buildDirectory(dirlst, stopend=True, isVideo=True, isDownloadable=True)
    else:
        if (not searched):
            kodi.notify(msg='No Content Found')
            quit()

    if searched: return str(len(r))

    if not searched:
        search_pattern = '''rel\=['"]next['"]\s*href=['"]([^'"]+)\s*'''

        helper.scraper().get_next_page(content_mode, url, search_pattern, filename)
