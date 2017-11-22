#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
from enum import Enum


class ContentType(Enum):
    APPLICATION_MS_WORD = 'APPLICATION_MS_WORD'
    APPLICATION_PDF = 'APPLICATION_PDF'
    APPLICATION_VND_MS_EXCEL = 'APPLICATION_VND_MS_EXCEL'
    IMAGE_JPEG = 'IMAGE_JPEG'
    IMAGE_PNG = 'IMAGE_PNG'
    TEXT_HTML = 'TEXT_HTML'
    TEXT_PLAIN = 'TEXT_PLAIN'
    APPLICATION_JSON = 'APPLICATION_JSON'
