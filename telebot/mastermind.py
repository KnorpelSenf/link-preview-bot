import re

def get_links(msg):
    # see https://stackoverflow.com/q/6883049
    return re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', msg)
