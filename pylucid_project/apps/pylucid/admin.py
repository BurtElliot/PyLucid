# coding: utf-8

"""
    PyLucid.admin
    ~~~~~~~~~~~~~~

    Register all PyLucid model in django admin interface.

    TODO:
        * if http://code.djangoproject.com/ticket/3400 is implement:
            Add site to list_filter for e.g. PageMeta, PageContent etc.      
    
    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from reversion.admin import VersionAdmin

from pylucid import models
from pylucid_project.apps.pylucid.base_admin import BaseAdmin


class PageTreeAdmin(BaseAdmin, VersionAdmin):
    #prepopulated_fields = {"slug": ("title",)}
    list_display = (
        "id", "parent", "slug", "showlinks", "site", "view_on_site_link", "lastupdatetime", "lastupdateby"
    )
    list_display_links = ("id", "slug")
    list_filter = (
        "site", "page_type", "permitViewGroup", "showlinks", "createby", "lastupdateby", "design",
    )
    date_hierarchy = 'lastupdatetime'
    search_fields = ("slug",)

admin.site.register(models.PageTree, PageTreeAdmin)


class BanEntryAdmin(admin.ModelAdmin):
    list_display = list_display_links = ("ip_address", "createtime",)
    search_fields = ("ip_address",)
admin.site.register(models.BanEntry, BanEntryAdmin)


class LanguageAdmin(VersionAdmin):
    list_display = ("code", "description", "site_info", "permitViewGroup")
    list_display_links = ("code", "description")
    list_filter = ("permitViewGroup",)
admin.site.register(models.Language, LanguageAdmin)


class LogEntryAdmin(BaseAdmin):
    list_display = ("createtime", "createby", "view_on_site_link", "app_label", "action", "message")
    list_filter = (
        "site", "app_label", "action", "createby"
    )
    search_fields = ("app_label", "action", "message", "long_message", "data")
admin.site.register(models.LogEntry, LogEntryAdmin)


#class OnSitePageMeta(models.PageMeta):
#    def get_site(self):
#        return self.page.site
#    site = property(get_site)
#    class Meta:
#        proxy = True



class PageMetaAdmin(BaseAdmin, VersionAdmin):
    list_display = ("id", "get_title", "get_site", "view_on_site_link", "lastupdatetime", "lastupdateby",)
    list_display_links = ("id", "get_title")
    list_filter = ("language", "createby", "lastupdateby", "tags")#"keywords"
    date_hierarchy = 'lastupdatetime'
    search_fields = ("description", "keywords")

admin.site.register(models.PageMeta, PageMetaAdmin)


class PageContentInline(admin.StackedInline):
    model = models.PageContent

class PageContentAdmin(BaseAdmin, VersionAdmin):
    list_display = ("id", "get_title", "get_site", "view_on_site_link", "lastupdatetime", "lastupdateby",)
    list_display_links = ("id", "get_title")
    list_filter = ("markup", "createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("content",) # it would be great if we can add "get_title"

admin.site.register(models.PageContent, PageContentAdmin)


class PluginPageAdmin(BaseAdmin, VersionAdmin):
    list_display = (
        "id", "get_plugin_name", "app_label",
        "get_site", "view_on_site_link", "lastupdatetime", "lastupdateby",
    )
    list_display_links = ("get_plugin_name", "app_label")
    list_filter = ("createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("app_label",)

admin.site.register(models.PluginPage, PluginPageAdmin)


#------------------------------------------------------------------------------


class ColorSchemeAdminForm(forms.ModelForm):
    class Meta:
        model = models.ColorScheme

    def clean_sites(self):
        """
        Check if headfile sites contain the site from all design entries.
        """
        sites = self.cleaned_data["sites"]
        designs = models.Design.objects.all().filter(headfiles=self.instance)
        for design in designs:
            for design_site in design.sites.all():
                if design_site in sites:
                    continue
                raise forms.ValidationError(_(
                    "ColorScheme must exist on site %(site)r!"
                    " Because it's used by design %(design)r." % {
                        "site": design_site,
                        "design": design
                    }
                ))

        return sites

#class ColorAdmin(VersionAdmin):
#    list_display = ("id", "name","value")
#admin.site.register(models.Color, ColorAdmin)

class ColorInline(admin.TabularInline):
    model = models.Color
    extra = 0


class ColorSchemeAdmin(VersionAdmin):
    form = ColorSchemeAdminForm
    list_display = ("id", "name", "preview", "site_info", "lastupdatetime", "lastupdateby")
    list_display_links = ("name",)
    search_fields = ("name",)
    list_filter = ("sites",)
    inlines = [ColorInline, ]

    def preview(self, obj):
        colors = models.Color.objects.all().filter(colorscheme=obj)
        result = ""
        for color in colors:
            result += '<span style="background-color:#%s;" title="%s">&nbsp;&nbsp;&nbsp;</span>' % (
                color.value, color.name
            )
        return result
    preview.short_description = 'color preview'
    preview.allow_tags = True

admin.site.register(models.ColorScheme, ColorSchemeAdmin)


#------------------------------------------------------------------------------


class DesignAdminForm(forms.ModelForm):
    class Meta:
        model = models.Design

    def clean(self):
        """
        check if all headfiles exist on the same site than the design exist.
        """
        cleaned_data = self.cleaned_data

        sites = cleaned_data["sites"]
        headfiles = cleaned_data["headfiles"]

        for headfile in headfiles:
            for design_site in sites:
                if design_site in headfile.sites.all():
                    continue
                raise forms.ValidationError(_(
                    "Headfile %(headfile)r doesn't exist on site %(site)r!" % {
                        "headfile": headfile, "site": design_site
                    }
                ))

        colorscheme = cleaned_data["colorscheme"]
        for design_site in sites:
            if design_site in colorscheme.sites.all():
                continue
            msg = _(
                "Colorscheme %(colorscheme)r doesn't exist on site %(site)r!" % {
                    "colorscheme": colorscheme, "site": design_site
                }
            )
            self._errors["colorscheme"] = self.error_class([msg])

            # These fields are no longer valid. Remove them from the
            # cleaned data.
            del cleaned_data["colorscheme"]



        return cleaned_data


class DesignAdmin(VersionAdmin):
    form = DesignAdminForm
    list_display = ("id", "name", "template", "colorscheme", "site_info", "lastupdatetime", "lastupdateby")
    list_display_links = ("name",)
    list_filter = ("sites", "template", "colorscheme", "createby", "lastupdateby")
    search_fields = ("name", "template", "colorscheme")

admin.site.register(models.Design, DesignAdmin)


#------------------------------------------------------------------------------


class EditableHtmlHeadFileAdminForm(forms.ModelForm):
    class Meta:
        model = models.EditableHtmlHeadFile

    def clean_sites(self):
        """
        Check if headfile sites contain the site from all design entries.
        """
        sites = self.cleaned_data["sites"]
        designs = models.Design.objects.all().filter(headfiles=self.instance)
        for design in designs:
            for design_site in design.sites.all():
                if design_site in sites:
                    continue
                raise forms.ValidationError(_(
                    "Headfile must exist on site %(site)r!"
                    " Because it's used by design %(design)r." % {
                        "site": design_site,
                        "design": design
                    }
                ))

        return sites


class EditableHtmlHeadFileAdmin(VersionAdmin):
    form = EditableHtmlHeadFileAdminForm
    list_display = ("id", "filepath", "site_info", "render", "description", "lastupdatetime", "lastupdateby")
    list_display_links = ("filepath", "description")
    list_filter = ("sites", "render")

admin.site.register(models.EditableHtmlHeadFile, EditableHtmlHeadFileAdmin)


#-----------------------------------------------------------------------------


class UserProfileAdmin(VersionAdmin):
    list_display = ("id", "user", "site_info", "lastupdatetime", "lastupdateby")
    list_display_links = ("user",)
    list_filter = ("sites",)

admin.site.register(models.UserProfile, UserProfileAdmin)
