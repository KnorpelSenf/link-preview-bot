import re


def get_links(msg, entities):
    urls = []
    for entity in entities:
        type = entity.type
        url = None

        if type == 'url':
            url = entity.url
        elif type == 'text_link':
            url = msg[entity.offset:entity.offset + entity.length]

        if url is not None:
            print(url)
            if not re.match('^[A-Za-z]+:\\/\\/', url): # ^[a-zA-Z]+:\/\/
                url = 'http://' + url
            url = remove_mobile(url)
            urls.append(url)
        else:
            print('url was None and type was', type)
    return urls


def remove_mobile(url):
    if url.startswith('http://m.'):
        url = 'http://' + url[len('http://m.'):]
    if url.startswith('https://m.'):
        url = 'https://' + url[len('https://m.'):]
    if '.m.' in url:
        m_index = url.index('.m.')
        if '/' not in url[len('https://')] or m_index < url.index('/', len('https://')):
            url = url[: m_index] + url[m_index + 2:]  # carve out the ".m"
    return url
