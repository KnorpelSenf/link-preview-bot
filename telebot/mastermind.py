def get_links(msg, entities):
    urls = [entity.url for entity in entities if entity.type == 'url']
    text_links = [msg[entity.offset:entity.offset + entity.length]
                  for entity in entities if entity.type == 'text_link']
    links = urls + text_links

    # Prepend protocol if it is missing and remove "m." from URL if present. In some
    # cases this prevents a link preview from being generated.
    return [remove_mobile(url)
            if '://' in url
            else remove_mobile('http://' + url)
            for url in links]


def remove_mobile(url):
    if url.startswith('http://m.'):
        url = 'http://' + url[len('http://m.'):]
    if url.startswith('https://m.'):
        url = 'https://' + url[len('https://m.'):]
    if '.m.' in url:
        m_index = url.index('.m.')
        if '/' not in url[len('https://')] or m_index < url.index('/', len('https://')):
            url = url[:m_index] + url[m_index + 2:]  # carve out the ".m"
    return url
