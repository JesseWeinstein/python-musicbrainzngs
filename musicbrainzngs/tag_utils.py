# This file is part of the musicbrainzngs library
# Copyright (C) Jesse Weinstein
# This file is distributed under a BSD-2-Clause type license.
# See the COPYING file for more information.

import itertools
import logging

import musicbrainzngs

def has_tag(thing,tag):
    return thing.has_key('tag-list') and next((True for z in thing['tag-list'] if z['name']==tag), False)

def make_add_tag_dict(entityType, entities, tag):
    return {entityType: dict([(x['id'],[tag]+[y['name'] for y in x.get('tag-list',[])]) for x in entities])}

def make_remove_tag_dict(entityType, entities, tag):
    return {entityType: dict([(x['id'],[y['name'] for y in x.get('tag-list',[]) if y['name']!=tag]) for x in entities])}

def _untagged(func, tag, **kargs):
    kargs['includes']=['tags']
    for x in _load_all(func,**kargs):
        if not has_tag(x,tag):
            yield x

def _untagged_entities_of_tagged_artists(entityBrowseFunc, tag):
    return itertools.chain.from_iterable(
        ( _untagged(entityBrowseFunc, tag, artist=x['id']) 
          for x in _load_all(musicbrainzngs.search_artists, tag=tag)))

def untagged_recordings_of_tagged_artists(tag):
    return _untagged_entities_of_tagged_artists(
        musicbrainzngs.browse_recordings, tag)

def untagged_release_groups_of_tagged_artists(tag):
    return _untagged_entities_of_tagged_artists(
        musicbrainzngs.browse_release_groups, tag)

def untagged_works_of_tagged_artists(tag):
    tagged=set((x['id'] for x in _load_all(musicbrainzngs.search_works, tag=tag)))
    for x in _load_all(musicbrainzngs.search_artists, tag=tag):
        a=musicbrainzngs.get_artist_by_id(x['id'], includes=['works'])
        for w in a['artist']['work-list']:
            if w['id'] not in tagged:
                w2=musicbrainzngs.get_work_by_id(w['id'], includes=['tags'])['work']
                if not has_tag(w2, tag):
                    yield w2


def untagged_releases_of_tagged_release_groups(tag):
    tagged=set((x['id'] for x in _load_all(musicbrainzngs.search_releases, tag=tag)))
    for rg in _load_all(musicbrainzngs.search_release_groups, tag=tag):
        for r in rg['release-list']:
            if r['id'] not in tagged:
                r2=musicbrainzngs.get_release_by_id(r['id'], includes=['tags'])['release']
                if not has_tag(r2,tag):
                    yield r2

def _load_all(func, **kargs):
    kargs.setdefault('limit',100)
    kargs.setdefault('offset',0)
    while True:
        print 'Running', func.__name__, 'with', kargs
        x=func(**kargs).itervalues().next()
        for y in x:
            yield y
        if len(x)<kargs['limit']:
            break
        kargs['offset']+=kargs['limit']

