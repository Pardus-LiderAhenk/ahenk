#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
from enum import Enum


class ContentType(Enum):
    APPLICATION_JSON = 'APPLICATION_JSON'
    APPLICATION_PDF = 'APPLICATION_PDF'
    APPLICATION_VND_MS_EXCEL = 'APPLICATION_VND_MS_EXCEL'
    APPLICATION_MS_WORD = 'APPLICATION_MS_WORD'
    TEXT_PLAIN = 'TEXT_PLAIN'
    TEXT_HTML = 'TEXT_HTML'
    IMAGE_PNG = 'IMAGE_PNG'
    IMAGE_JPEG = 'IMAGE_JPEG'