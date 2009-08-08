# coding: utf-8

"""
    PyLucid blog plugin
    ~~~~~~~~~~~~~~~~~~~

    A simple blog system.

    http://feedvalidator.org/
    
    TODO:
        * Detail view, use BlogEntry.get_absolute_url()
    

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__ = "$Rev$ Alpha"

# from python core
import os, datetime, posixpath

# from django
from django.conf import settings
from django.http import HttpResponse
from django.core.mail import send_mail
from django.utils.translation import ugettext as _
from django import http
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.contrib.comments.views.comments import post_comment

from pylucid.decorators import render_to

from blog.models import BlogEntry

# from django-tagging
from tagging.models import Tag, TaggedItem

def _add_breadcrumb(request, title, url):
    """ shortcut for add breadcrumb link """
    context = request.PYLUCID.context
    breadcrumb_context_middlewares = context["context_middlewares"]["breadcrumb"]
    breadcrumb_context_middlewares.add_link(title, url)


@render_to("blog/summary.html")
def _render_summary(request, context):
    tag_cloud = Tag.objects.cloud_for_model(BlogEntry, steps=2)
    context.update({
        "tag_cloud": tag_cloud,
    })
    return context


def summary(request):
    context = {
        "entries": BlogEntry.objects.all()
    }
    return _render_summary(request, context)


def tag_view(request, tag):
    tags = tag.strip("/").split("/")
    entries = TaggedItem.objects.get_by_model(BlogEntry, tags)

    # Add link to the breadcrumbs ;)
    _add_breadcrumb(request, title=_("All '%s' tagged items" % ",".join(tags)), url=request.path)

    context = {
        "entries": entries
    }
    return _render_summary(request, context)


@render_to("blog/detail_view.html")
def detail_view(request, id, title):
    entry = BlogEntry.objects.get(pk=id)

    # Add link to the breadcrumbs ;)
    _add_breadcrumb(request, title=entry.headline, url=entry.get_absolute_url())

    if request.POST:
        # Use django.contrib.comments.views.comments.post_comment to handle a comment
        # post.
        return post_comment(request, next=entry.get_absolute_url())

    context = {
        "page_title": entry.headline, # Change the global title with blog headline
        "entry": entry,
        "tag_cloud": Tag.objects.cloud_for_model(BlogEntry, steps=2),
    }
    return context


def lucidTag(request):
    """
    TODO: Update the page automaticly???
    """
    return u"[Update Info: You must delete this PageTree entry and create a new blog plugin page here!]"