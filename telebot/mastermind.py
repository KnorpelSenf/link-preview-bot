from urlextract import URLExtract

extractor = URLExtract()


def get_links(msg):
    return [remove_mobile(url)
            if url.startswith('http://') or url.startswith('https://')
            else remove_mobile('http://' + url)
            for url in extractor.gen_urls(msg)]


def remove_mobile(url):
    if url.startswith('http://m.'):
        url = 'http://' + url[len('http://m.'):]
    if url.startswith('https://m.'):
        url = 'https://' + url[len('https://m.'):]
    if '.m.' in url:
        m_index = url.index('.m.')
        if '/' not in url[len('https://')] or m_index < url.index('/', len('https://')):
            url = url[:m_index] + url[m_index + 2:]
    return url
