# coding: utf-8

import os
import posixpath
from fnmatch import fnmatch
from glob import glob

if __name__ == "__main__":
    # For doctest only
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"
    from django.conf import global_settings
    global_settings.SITE_ID = 1

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.template.context import RequestContext
from django.http import Http404, HttpResponseRedirect, HttpResponseBadRequest

from pylucid_project.apps.pylucid.models import LogEntry
from pylucid_project.apps.pylucid.shortcuts import render_pylucid_response

from gallery.models import GalleryModel
from gallery.preference_forms import GalleryPrefForm


#------------------------------------------------------------------------------


def _fnmatch_list(item, filter_list):
    """
    >>> _fnmatch_list("foo.jpg", ["*.bar", "*.jpg"])
    True
    
    >>> _fnmatch_list("foo.jpg", ["*.bar"])
    False
    """
    for filter in filter_list:
        if fnmatch(item, filter):
            return True
    return False


def _split_suffix(filename, suffix_list):
    """
    >>> _split_suffix("picture_no.jpg", ["_foo","_bar"])
    False
    
    >>> _split_suffix("picture_web.jpg", ["_web"])
    'picture'
    """
    name = os.path.splitext(filename)[0]
    for suffix in suffix_list:
        if name.endswith(suffix):
            cut_pos = len(suffix)
            cut_filename = name[:-cut_pos]
            return cut_filename
    return False


#------------------------------------------------------------------------------


class Gallery(object):
    def __init__(self, request, rest_url):
        self.request = request
        self.pagetree = self.request.PYLUCID.pagetree
        self.gallery_base_url = self.request.PYLUCID.pagemeta.get_absolute_url()

        self.rel_path, self.rel_url = self.check_rest_url(rest_url)

        try:
            self.config = GalleryModel.objects.get(pagetree=self.pagetree)
        except GalleryModel.DoesNotExist, err:
            # TODO: Don't redirect to admin panel -> Display a own create view!
            request.page_msg(
                 _("Gallery entry for page: %s doesn't exist, please create it.") % self.pagetree.get_absolute_url()
            )
            return HttpResponseRedirect(reverse("admin:gallery_gallerymodel_add"))

        self.rel_base_path = self.config.path
        self.abs_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, self.rel_base_path, self.rel_path))
        if not os.path.isdir(self.abs_path) or not self.abs_path.startswith(settings.MEDIA_ROOT):
            raise Http404("wrong path")

        self.abs_base_url = posixpath.normpath(posixpath.join(settings.MEDIA_URL, self.rel_base_path, self.rel_path))

        self.filename_whitelist = self.config.get_filename_whitelist()
        self.diritem_blacklist = self.config.get_diritem_blacklist()
        self.thumb_suffix_marker = self.config.get_thumb_suffix_marker()
        self.filename_suffix_filter = self.config.get_filename_suffix_filter()

        dirs, pictures, thumbs = self.read_dir(self.abs_path)

        self.dir_info = self.build_dir_info(dirs)
        self.picture_info = self.build_picture_info(pictures, thumbs)

        self.breadcrumbs = self.build_breadcrumbs()

    def build_breadcrumbs(self):
        parts = ""
        url = self.gallery_base_url
        breadcrumbs = [{
            "name": _("index"),
            "title": _("goto 'index'"),
            "url": url
        }]
        rel_url = self.rel_url.strip("/")
        if not rel_url:
            return breadcrumbs

        for url_part in rel_url.split("/"):
            url += "%s/" % url_part
            parts += "%s/" % url_part
            breadcrumbs.append({
                "name": url_part,
                "title": _("goto '%s'") % parts,
                "url": url
            })
        return breadcrumbs

    def make_url(self, part):
        return posixpath.normpath(posixpath.join(self.abs_base_url, part))

    def check_rest_url(self, rest_url):
        if rest_url == "":
            return ("", "")

        pref_form = GalleryPrefForm()
        preferences = pref_form.get_preferences()
        raw_unauthorized_signs = preferences["unauthorized_signs"]

        for sign in raw_unauthorized_signs.split():
            sign = sign.strip()
            if sign and sign in rest_url:
                LogEntry.objects.log_action(
                    app_label="pylucid_plugin.gallery", action="unauthorized sign",
                    message="%r in %r" % (sign, rest_url),
                )
                raise Http404("bad path")

        rel_path = os.path.normpath(rest_url)
        rel_url = posixpath.normpath(rel_path)
        return rel_path, rel_url

    def read_dir(self, path):
        pictures = []
        thumbs = {}
        dirs = []
        for item in os.listdir(path):
            if _fnmatch_list(item, self.diritem_blacklist):
                # Skip file/direcotry
                continue

            abs_item_path = os.path.join(path, item)
            if os.path.isdir(abs_item_path):
                dirs.append(item)
            elif os.path.isfile(abs_item_path):
                if not _fnmatch_list(item, self.filename_whitelist):
                    # Skip files witch are not in whitelist
                    continue

                cut_filename = _split_suffix(item, self.thumb_suffix_marker)
                if cut_filename:
                    thumbs[cut_filename] = item
                else:
                    pictures.append(item)

        pictures.sort()
        dirs.sort()

        return dirs, pictures, thumbs

    def build_dir_info(self, dirs):
        if self.rel_path != "":
            dirs.insert(0, "..")

        dir_info = []
        for dir in dirs:
            abs_sub_dir = os.path.join(self.abs_path, dir)
            sub_pictures = self.read_dir(abs_sub_dir)[1]

            dir_info.append({
                "verbose_name": dir.replace("_", " "),
                "href": "%s/" % posixpath.join(self.request.path, dir),
                "pic_count": len(sub_pictures),
            })

        return dir_info

    def build_picture_info(self, pictures, thumbs):
        picture_info = []
        for picture in pictures:
            cut_filename = _split_suffix(picture, self.filename_suffix_filter)
            if not cut_filename:
                cut_filename = os.path.splitext(picture)[0]

            info = {
                "href": self.make_url(picture),
                "verbose_name": cut_filename.replace("_", " "),
            }

            if cut_filename in thumbs:
                info["thumb_href"] = self.make_url(thumbs[cut_filename])
            else:
                info["thumb_href"] = self.make_url(picture)
                info["thumb_width"] = self.config.default_thumb_width
                info["thumb_height"] = self.config.default_thumb_height

            picture_info.append(info)
        return picture_info

    def render(self):
        context = {
            "rel_path": self.rel_path,
            "dir_info": self.dir_info,
            "picture_info": self.picture_info,
            "breadcrumbs": self.breadcrumbs,
        }

        # ajax and non ajax response
        return render_pylucid_response(self.request, self.config.template, context,
            context_instance=RequestContext(self.request)
        )


def gallery(request, rest_url=""):
    g = Gallery(request, rest_url)

    if not request.is_ajax():
        # FIXME: In Ajax request, only the page_content would be replaced, not the
        # breadcrumb links :(
        context = request.PYLUCID.context
        breadcrumb_context_middlewares = context["context_middlewares"]["breadcrumb"]
        for breadcrumb_info in g.breadcrumbs[1:]:
            breadcrumb_context_middlewares.add_link(**breadcrumb_info)

    return g.render()





if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
