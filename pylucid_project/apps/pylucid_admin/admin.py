# coding: utf-8

from django.conf import settings
from django.contrib import admin
from django.shortcuts import render_to_response
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from reversion.admin import VersionAdmin

from pylucid_admin import models

from pylucid_admin.admin_site import pylucid_admin_site

#-----------------------------------------------------------------------------
# some django admin stuff is broken if TEMPLATE_STRING_IF_INVALID != ""
# http://code.djangoproject.com/ticket/3579

if settings.TEMPLATE_STRING_IF_INVALID != "":
    # Patch the render_to_response function ;)
    from django.contrib.auth import admin as auth_admin
    from django.contrib.admin import options

    def patched_render_to_response(*args, **kwargs):
        old = settings.TEMPLATE_STRING_IF_INVALID
        settings.TEMPLATE_STRING_IF_INVALID = ""
        result = render_to_response(*args, **kwargs)
        settings.TEMPLATE_STRING_IF_INVALID = old
        return result

    options.render_to_response = patched_render_to_response
    auth_admin.render_to_response = patched_render_to_response


#-----------------------------------------------------------------------------


if settings.DEBUG:
    class PermissionAdmin(admin.ModelAdmin):
        """ django auth Permission """
        list_display = ("id", "name", "content_type", "codename")
        list_display_links = ("name", "codename")
        list_filter = ("content_type",)
    pylucid_admin_site.register(Permission, PermissionAdmin)

    class ContentTypeAdmin(admin.ModelAdmin):
        """ django ContentType """
        list_display = list_display_links = ("id", "app_label", "name", "model")
        list_filter = ("app_label",)
    pylucid_admin_site.register(ContentType, ContentTypeAdmin)


#-----------------------------------------------------------------------------


class PyLucidAdminPageAdmin(VersionAdmin):
    list_display = (
        "id", "name", "title", "url_name",
        "get_pagetree", "get_pagemeta", "get_page",
        "superuser_only", "access_permissions"
    )
    list_display_links = ("name",)
    list_filter = ("createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("name", "title", "url_name")

    def superuser_only(self, obj):
        superuser_only, access_permissions = obj.get_permissions()
        return superuser_only
    superuser_only.boolean = True

    def access_permissions(self, obj):
        superuser_only, access_permissions = obj.get_permissions()
        return " | ".join(access_permissions)

pylucid_admin_site.register(models.PyLucidAdminPage, PyLucidAdminPageAdmin)