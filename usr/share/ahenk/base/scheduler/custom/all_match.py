#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Some utility classes / functions first
class AllMatch(set):
    """Universal set - match everything"""
    def __contains__(self, item): return True