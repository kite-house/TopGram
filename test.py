import requests
import json
from bs4 import BeautifulSoup as bs

link = 'https://readbeyondnews.com/wp-content/uploads/2021/08/Google.png'


def is_image(url):
    response = requests.head(url)
    content_type = response.headers.get('content-type')
    try:
        if 'image' in content_type:
            return True
        else:
            return False
    except Exception:
        return 'err'

# Test the function with a sample URL
result = is_image(link)
print(result)