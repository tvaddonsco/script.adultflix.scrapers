from kodi_six import xbmc
import os, six, re
from packlib import client, kodi, dom_parser2, log_utils

from resources.lib.modules import local_utils
from resources.lib.modules import helper

buildDirectory = local_utils.buildDir
urljoin = six.moves.urllib.parse.urljoin

filename = 'pandamovie'
base_domain = 'https://pandamovie.biz'
base_name = base_domain.replace('www.', '');
base_name = re.findall('(?:\/\/|\.)([^.]+)\.', base_name)[0].title()
type = 'movies'
menu_mode = 297
content_mode = 298
player_mode = 810

search_tag = 0
search_base = urljoin(base_domain, 'search.fcgi?query=%s')


@local_utils.url_dispatcher.register('%s' % menu_mode)
def menu():
    url = urljoin(base_domain, 'adult/movies/')
    content(url)


# try:
# url = urljoin(base_domain,'xxx/movies/')
# c = client.request(url)
# r = re.findall('<div\s+class="mepo">(.*?)<div\s+class="rating">',c, flags=re.DOTALL)
# if ( not r ):
# log_utils.log('Scraping Error in %s:: Content of request: %s' % (base_name.title(),str(c)), xbmc.LOGERROR)
# kodi.notify(msg='Scraping Error: Info Added To Log File', duration=6000, sound=True)
# quit()
# except Exception as e:
# log_utils.log('Fatal Error in %s:: Error: %s' % (base_name.title(),str(e)), xbmc.LOGERROR)
# kodi.notify(msg='Fatal Error', duration=4000, sound=True)
# quit()

# dirlst = []

# for i in r:
# try:
# name = re.findall('<h3><a href=".+?">(.*?)</a>',i,flags=re.DOTALL)[0]
# url = re.findall('<h3><a href="(.*?)"',i,flags=re.DOTALL)[0]
# icon = re.findall('<img src="(.*?)"',i,flags=re.DOTALL)[0]
# desc = re.findall('<div class="texto">(.*?)</div>',i,flags=re.DOTALL)[0]
# fanarts = xbmc.translatePath(os.path.join('special://home/addons/script.adultflix.artwork', 'resources/art/%s/fanart.jpg' % filename))
# dirlst.append({'name': name, 'url': url, 'mode': content_mode, 'icon': icon, 'description': desc, 'fanart': fanarts ,'folder': True})
# except Exception as e:
# log_utils.log('Error adding menu item %s in %s:: Error: %s' % (i[1].title(),base_name.title(),str(e)), xbmc.LOGERROR)

# if dirlst: buildDirectory(dirlst)
# else:
# kodi.notify(msg='No Menu Items Found')
# quit()

@local_utils.url_dispatcher.register('%s' % content_mode, ['url'], ['searched'])
def content(url, searched=False):
    try:
        if url == '':
            url = urljoin(base_domain, 'xxx/movies/')
        c = client.request(url)
        r = re.findall('<div\s+class="mepo">(.*?)<div\s+class="rating">', c, flags=re.DOTALL)
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
            name = re.findall('<h3><a href=".+?">(.*?)</a>', i, flags=re.DOTALL)[0]
            url2 = re.findall('<h3><a href="(.*?)"', i, flags=re.DOTALL)[0]
            icon = re.findall('<img src="(.*?)"', i, flags=re.DOTALL)[0]
            desc = re.findall('<div class="texto">(.*?)</div>', i, flags=re.DOTALL)[0]
            fanarts = xbmc.translatePath(
                os.path.join('special://home/addons/script.adultflix.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append(
                {'name': name, 'url': url2, 'mode': player_mode, 'icon': icon, 'fanart': fanarts, 'description': desc,
                 'folder': False})
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

        try:
            search_pattern = '''<link rel=['"]next['"]\s*href=['"]([^'"]+)'''
            helper.scraper().get_next_page(content_mode, url, search_pattern, filename)
        except Exception as e:
            log_utils.log('Error getting next page for %s :: Error: %s' % (base_name.title(), str(e)), xbmc.LOGERROR)
