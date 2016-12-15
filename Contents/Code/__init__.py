NAME = 'Daz Doco Channel'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
SEARCH_ICON = 'icon-search.png'
BASE_URL = 'http://www.reddit.com/r/documentaries.json'
SEARCH_URL = 'http://www.reddit.com/r/documentaries/search.json?q=%s&restrict_sr=on'

def Start():
    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = NAME
    DirectoryObject.thumb = R(ICON)
    NextPageObject.thumb = R(ICON)
    VideoClipObject.thumb = R(ICON)


@handler('/video/PlexDocumentariesChannel', NAME, thumb=ICON, art=ART)
def MainMenu():
    oc = ObjectContainer(title2=NAME)
    oc.add(DirectoryObject(key=Callback(GetVideos), title='Docos'))
    oc.add(InputDirectoryObject(key=Callback(Search), title='Search', prompt='Search for', thumb=R(SEARCH_ICON)))
    return oc

@route('/video/PlexDocumentariesChannel/search')
def Search(query):
    return GetVideos(url=SEARCH_URL % (String.Quote(query, usePlus=True)))

@route('/video/PlexDocumentariesChannel/getvideos')
def GetVideos(url=BASE_URL, count=0, limit=25):
    oc = ObjectContainer(title2=NAME)
    data = JSON.ObjectFromURL(url, cacheTime=0)
    after = data['data'].get('after')
    before = data['data'].get('before')
    count = int(count) + 25

    if before:
        prev_count = count - 24
        prev_link = url + '?count=' + str(prev_count) + '&before=' + before
        oc.add(DirectoryObject(
            key=Callback(GetVideos, url=prev_link, count=count),
            title='<< previous'
        ))

    children = data['data']['children']
    if children:
        for child in children:
            data = child['data']
            if 'media' in data:
                if data['media'] != None:
                    video = data['media']['oembed']
                else:
                    video = data

                if 'url' not in video:
                    video['url'] = data['url']

                if 'description' not in video:
                    video['description'] = ''

                if 'thumbnail_url' not in video:
                    video['thumbnail_url'] = ''

                if 'title' in data:
                    video['title'] = data['title']


                if URLService.ServiceIdentifierForURL(video['url']) is not None:
                    oc.add(VideoClipObject(
                        url = video['url'],
                        title = video['title'],
                        summary = video['description'],
                        thumb = video['thumbnail_url']
                    ))
    else:
        return ObjectContainer(header='Results', message='No Results Found')

    if after:
        next_link = url + '?count=' + str(count) + '&after=' + after
        oc.add(DirectoryObject(
            key=Callback(GetVideos, url=next_link, count=count),
            title='next >>'
        ))

    return oc
