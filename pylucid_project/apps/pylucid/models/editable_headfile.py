# coding: utf-8

"""
    PyLucid models
    ~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import errno
import codecs
import mimetypes

from django.conf import settings
from django.db.models import signals
from django.contrib.sites.models import Site
from django.db import models, IntegrityError
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.translation import ugettext_lazy as _

# http://code.google.com/p/django-tools/
from django_tools.template import render

from pylucid_project.apps.pylucid.models.base_models import UpdateInfoBaseModel, AutoSiteM2M
from pylucid_project.apps.pylucid.shortcuts import failsafe_message
from pylucid_project.apps.pylucid.system import headfile

from pylucid_project.pylucid_plugins import update_journal

# other PyLucid models
from colorscheme import ColorScheme, Color
from design import Design
from pylucid_project.apps.pylucid.system.css_color_utils import extract_colors


TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"



class EditableHtmlHeadFileManager(models.Manager):
    def get_HeadfileLink(self, filename):
        """
        returns a pylucid.system.headfile.Headfile instance
        """
        db_instance = self.get(filename=filename)
        return headfile.HeadfileLink(filename=db_instance.filename)#, content=db_instance.content)


class EditableHtmlHeadFile(AutoSiteM2M, UpdateInfoBaseModel):
    """
    Storage for editable static text files, e.g.: stylesheet / javascript.

    inherited attributes from AutoSiteM2M:
        sites   -> ManyToManyField to Site
        on_site -> sites.managers.CurrentSiteManager instance

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    objects = EditableHtmlHeadFileManager()

    filepath = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=64,
        help_text=_("MIME type for this file. (Leave empty for guess by filename)")
    )
    html_attributes = models.CharField(max_length=256, null=False, blank=True,
        # TODO: Use this!
        help_text=_('Additional html tag attributes (CSS example: media="screen")')
    )
    render = models.BooleanField(default=False,
        help_text=_("Are there CSS ColorScheme entries in the content?")
    )
    description = models.TextField(null=True, blank=True)
    content = models.TextField()

    def get_filename(self):
        """ returns only the filename """
        return os.path.split(self.filepath)[1]

    def get_color_filepath(self, colorscheme=None):
        """ Colorscheme + filepath """
        if colorscheme:
            assert isinstance(colorscheme, ColorScheme)
            return os.path.join("ColorScheme_%s" % colorscheme.pk, self.filepath)
        else:
            # The Design used no colorscheme
            return self.filepath

    def get_path(self, colorscheme):
        """ Path for filesystem cache path and link url. """
        return os.path.join(
            settings.PYLUCID.PYLUCID_MEDIA_DIR, settings.PYLUCID.CACHE_DIR,
            self.get_color_filepath(colorscheme)
        )

    def get_cachepath(self, colorscheme):
        """
        filesystem path with filename.
        TODO: Install section sould create the directories!
        """
        return os.path.join(settings.MEDIA_ROOT, self.get_path(colorscheme))

    def get_rendered(self, colorscheme):
        color_dict = colorscheme.get_color_dict()

        for name, value in color_dict.iteritems():
            color_dict[name] = "#%s" % value

        return render.render_string_template(self.content, color_dict)

    def save_cache_file(self, colorscheme):
        """
        Try to cache the head file into filesystem (Only worked, if python process has write rights)
        Try to create the out path, if it's not exist.
        """
        cachepath = self.get_cachepath(colorscheme)

        def _save_cache_file(auto_create_dir=True):
            rendered_content = self.get_rendered(colorscheme)
            try:
                f = codecs.open(cachepath, "w", "utf8")
                f.write(rendered_content)
                f.close()
            except IOError, err:
                if auto_create_dir and err.errno == errno.ENOENT: # No 2: No such file or directory
                    # Try to create the out dir and save the cache file
                    path = os.path.dirname(cachepath)
                    if not os.path.isdir(path):
                        # Try to create cache path and save file
                        os.makedirs(path)
                        failsafe_message("Cache path %s created" % path)
                        _save_cache_file(auto_create_dir=False)
                        return
                raise

        try:
            _save_cache_file()
        except (IOError, OSError), err:
            failsafe_message("Can't cache EditableHtmlHeadFile into %r: %s" % (cachepath, err))
        else:
            if settings.DEBUG:
                failsafe_message("EditableHtmlHeadFile cached successful into: %r" % cachepath)

    def save_all_color_cachefiles(self):
        """
        this headfile was changed: resave all cache files in every existing colors
        TODO: Update Queyset lookup
        """
        designs = Design.objects.all()
        for design in designs:
            headfiles = design.headfiles.all()
            for headfile in headfiles:
                if headfile == self:
                    colorscheme = design.colorscheme
                    self.save_cache_file(colorscheme)

    def get_absolute_url(self, colorscheme):
        cachepath = self.get_cachepath(colorscheme)
        if os.path.isfile(cachepath):
            # The file exist in media path -> Let the webserver send this file ;)
            return os.path.join(settings.MEDIA_URL, self.get_path(colorscheme))
        else:
            # not cached into filesystem -> use pylucid.views.send_head_file for it
            url = reverse('PyLucid-send_head_file', kwargs={"filepath":self.filepath})
            if colorscheme:
                return url + "?ColorScheme=%s" % colorscheme.pk
            else:
                # Design used no colorscheme
                return url

    def get_headfilelink(self, colorscheme):
        """ Get the link url to this head file. """
        url = self.get_absolute_url(colorscheme)
        return headfile.HeadfileLink(url)

    def clean_fields(self, exclude):
        message_dict = {}

        if "mimetype" not in exclude:
            all_mimetypes = set(mimetypes.types_map.values())
            if self.mimetype not in all_mimetypes:
                failsafe_message(
                    "Warning: Mimetype %(mimetype)r for headfile %(headfile)r unknown!" % {
                        "mimetype": self.mimetype, "headfile": self.filepath
                    }
                )

        if "filepath" not in exclude:
            try:
                # "validate" the filepath with the url re. 
                reverse('PyLucid-send_head_file', kwargs={"filepath": self.filepath})
            except NoReverseMatch, err:
                message_dict["filepath"] = [_(
                    "filepath %(filepath)r contains invalid characters!"
                    " (Original error: %(err)s)" % {
                        "filepath": self.filepath,
                        "err": err,
                    }
                )]

        if message_dict:
            raise ValidationError(message_dict)

    def auto_mimetype(self):
        """ returns the mimetype for the current filename """
        fileext = os.path.splitext(self.filepath)[1].lower()
        if fileext == ".css":
            return u"text/css"
        elif fileext == ".js":
            return u"text/javascript"
        else:
            mimetypes.guess_type(self.filepath)[0] or u"application/octet-stream"

    def save(self, *args, **kwargs):
        """
        cache the head file into filesystem
        """
        # Try to cache the head file into filesystem (Only worked, if python process has write rights)
        self.save_all_color_cachefiles()

        return super(EditableHtmlHeadFile, self).save(*args, **kwargs)

    def __unicode__(self):
        sites = self.sites.values_list('name', flat=True)
        return u"'%s' (on sites: %r)" % (self.filepath, sites)

    class Meta:
        app_label = 'pylucid'
        #unique_together = ("filepath", "site")
        # unique_together doesn't work with ManyToMany: http://code.djangoproject.com/ticket/702
        ordering = ("filepath",)


def unique_check_callback(sender, **kwargs):
    """
    manually check a unique together, because django can't do this with 
    Meta.unique_together and a M2M field. It's also unpossible to do this 
    in model validation.
    
    Obsolete if unique_together work with ManyToMany: http://code.djangoproject.com/ticket/702
    
    Note: this was done in model admin class, too.
    """
    headfile = kwargs["instance"]

    headfiles = EditableHtmlHeadFile.objects.filter(filepath=headfile.filepath)
    headfiles = headfiles.exclude(id=headfile.id)

    for headfile in headfiles:
        for site in headfile.sites.all():
            if site not in headfile.sites.all():
                continue

            raise IntegrityError(
                _("EditableHtmlHeadFile with filepath %(filepath)r exist on site %(site)r") % {
                    "filepath": headfile.filepath,
                    "site": site,
                }
            )

signals.post_save.connect(unique_check_callback, sender=EditableHtmlHeadFile)


def update_colorscheme_callback(sender, **kwargs):
    headfile_instance = kwargs["instance"]
    if not headfile_instance.render:
        # No CSS ColorScheme entries in the content -> do nothing
        return

    print "Update colorscheme for %r" % headfile_instance

    content = headfile_instance.content

    designs = Design.objects.all()
    for design in designs:
        headfiles = design.headfiles.all()
        for headfile in headfiles:
            if headfile == headfile_instance:
                colorscheme = design.colorscheme
                print "Update colorscheme: %r" % colorscheme

                from pprint import pformat
                existing_color_dict = colorscheme.get_color_dict()

                print "_" * 79
                print "*** old content:"
                print content
                content, color_dict = extract_colors(content, existing_color_dict)
                print "_" * 79
                print "*** new content:"
                print content
                print "-" * 79
                print "*** extract_colors() - color dict:"
                print pformat(color_dict)

                try:
                    created, updated, exists = colorscheme.update(color_dict)
                except ValidationError, err:
                    print("Error updating colorscheme: %s" % err)
                    return

                created_count = len(created)
                updated_count = len(updated)

                print("created %s colors: %r" % (created_count, created))
                print("updated %s colors: %r" % (updated_count, updated))
                print("exists %s colors: %r" % (len(exists), exists))

                if created_count > 0 or updated_count > 0:
                    colorscheme.save()

    headfile_instance.content = content

signals.pre_save.connect(update_colorscheme_callback, sender=EditableHtmlHeadFile)
