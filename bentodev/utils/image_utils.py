from bentodev.config.settings import (
    AWS_BUCKET_URL,
    IMGIX_URL,
    AWS_S3_CUSTOM_DOMAIN
)

from collections import OrderedDict


class Bunch:

    def __init__(self, **kwds):
        self.__dict__.update(kwds)


SIZES = {
    'thumbnail': 100,
    'small': 300,
    'medium': 600,
    'large': 1000,
    'xlarge': 1800,
}


def get_resized_image_class(source, size):
    edge_size = SIZES[size]

    return generate_resized_image_class(source, edge_size, edge_size)


def generate_resized_image_class(source, width=1200, height=None, fit='max'):
    url = generate_resize_url(source, width, height, fit)

    image = Bunch(url=url)

    return image


def get_base_source(source):
    if type(source) is dict or type(source) is OrderedDict:
        source = source.get('image_path', source.get('url'))

    if not source:
        return ''

    if source.startswith(AWS_BUCKET_URL):
        source = source[len(AWS_BUCKET_URL):]

    if source.startswith(IMGIX_URL):
        source = source[len(IMGIX_URL):]

    # Splitting the IMGIX_URL was added to handle legacy URLs that did not
    # contain https
    if source.startswith(IMGIX_URL.split('https:')[1]):
        source = source[len(IMGIX_URL.split('https:')[1]):]

    cdn_domain = 'https://%s/' % AWS_S3_CUSTOM_DOMAIN

    if source.startswith(cdn_domain):
        source = source[len(cdn_domain):]

    if '?' in source:
        source = source[:source.rfind('?')]

    return source


def generate_resize_url(source, width=1200, height=None, fit='max'):
    source = get_base_source(source)

    params = 'w=%i&fit=%s&auto=compress,format' % (int(width), fit)

    if height:
        params += "&h=%i" % int(height)

    url = '%s%s?%s' % (IMGIX_URL, source, params)

    return url


def get_raw_image_url(source):
    source = get_base_source(source)

    url = '%s%s' % (IMGIX_URL, source)
    return url
