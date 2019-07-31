from urlextract import URLExtract

extractor = URLExtract()

def get_links(msg):
    return extractor.find_urls(msg)
