# coding:utf-8

"""
    translate a PageContent
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyleft: 2010-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django import http
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from pylucid_project.apps.i18n.utils.translate import translate
from pylucid_project.apps.i18n.views import select_language
from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid.models import PageTree, PageMeta, PageContent, Language

from page_admin.forms import PageMetaForm, PageContentForm


@check_permissions(superuser_only=False, permissions=(
    "pylucid.add_pagecontent", "pylucid.add_pagemeta",
    "pylucid.change_pagecontent", "pylucid.change_pagemeta",
))
@render_to()
def translate_page(request, pagemeta_id=None):
    if not pagemeta_id:
        raise

    source_pagemeta = PageMeta.objects.get(id=pagemeta_id)
    pagetree = source_pagemeta.pagetree
    source_language = source_pagemeta.language
    absolute_url = source_pagemeta.get_absolute_url()

    is_pluginpage = pagetree.page_type == PageTree.PLUGIN_TYPE
    if is_pluginpage:
        messages.error(request, "TODO: Translate a plugin page!")
        return http.HttpResponseRedirect(source_pagemeta.get_absolute_url())
    else:
        source_pagecontent = PageContent.objects.get(pagemeta=source_pagemeta)


    # select the destination language
    result = select_language(request, absolute_url, source_pagemeta.language, source_pagemeta.name)
    if isinstance(result, Language):
        # Language was selected or they exit only one other language
        dest_language = result
    elif isinstance(result, dict):
        # template context returned -> render language select form
        return result
    elif isinstance(result, http.HttpResponse):
        # e.g. error
        return result
    else:
        raise RuntimeError() # Should never happen


    context = {
        "title": _("Translate page '%(name)s' (%(source_lang)s) into %(dest_lang)s.") % {
            "name": source_pagemeta.name,
            "abort_url": absolute_url,
            "source_lang": source_pagemeta.language.description,
            "dest_lang": dest_language.description,
        },
        "template_name": "page_admin/translate_page.html",
    }

    try:
        dest_pagemeta = PageMeta.objects.get(pagetree=pagetree, language=dest_language)
    except PageMeta.DoesNotExist:
        dest_pagemeta = None
    else:
        dest_pagecontent = PageContent.objects.get(pagemeta=dest_pagemeta)

    if request.method == "POST":
        source_pagemeta_form = PageMetaForm(
            request.POST, prefix="source", instance=source_pagemeta
        )
        source_pagecontent_form = PageContentForm(
            request.POST, prefix="source", instance=source_pagecontent
        )
        if dest_pagemeta is None:
            dest_pagemeta_form = PageMetaForm(request.POST, prefix="dest")
            dest_pagecontent_form = PageContentForm(request.POST, prefix="dest")
        else:
            dest_pagemeta_form = PageMetaForm(
                request.POST, prefix=dest_language.code, instance=dest_pagemeta
            )
            dest_pagecontent_form = PageContentForm(
                request.POST, prefix=dest_language.code, instance=dest_pagecontent
            )

        if not (source_pagemeta_form.is_valid() and source_pagecontent_form.is_valid() and
                            dest_pagemeta_form.is_valid() and dest_pagecontent_form.is_valid()):
            context["has_errors"] = True
        else:
            # All forms are valid -> Save all.
            context["has_errors"] = False
            sid = transaction.savepoint()
            try:
                source_pagecontent_form.save()
                source_pagemeta_form.save()

                # Create new PageMeta entry
                new_pagemeta = dest_pagemeta_form.save(commit=False)
                new_pagemeta.pagetree = pagetree
                new_pagemeta.language = dest_language
                new_pagemeta.save()

                # Create new PageContent entry
                new_pagecontent = dest_pagecontent_form.save(commit=False)
                new_pagecontent.pagemeta = new_pagemeta
                new_pagecontent.save()
            except:
                transaction.savepoint_rollback(sid)
                raise
            else:
                transaction.savepoint_commit(sid)
                if dest_pagemeta is None:
                    messages.success(request, "New content %r created." % new_pagecontent)
                else:
                    messages.success(request, "All updated.")
                return http.HttpResponseRedirect(new_pagemeta.get_absolute_url())
    else:
        context["has_errors"] = False
        source_pagemeta_form = PageMetaForm(
            prefix="source", instance=source_pagemeta
        )
        source_pagecontent_form = PageContentForm(
            prefix="source", instance=source_pagecontent
        )
        if dest_pagemeta is None:
            dest_pagemeta_form = PageMetaForm(
                prefix="dest", initial={
                    "robots": source_pagemeta.robots,
                    "permitViewGroup": source_pagemeta.permitViewGroup, # FIXME: Doesn't work
                }
            )
            dest_pagecontent_form = PageContentForm(
                prefix="dest", initial={
                    "markup": source_pagecontent.markup,
                }
            )
        else:
            dest_pagemeta_form = PageMetaForm(
                prefix=dest_language.code, instance=dest_pagemeta
            )
            dest_pagecontent_form = PageContentForm(
                prefix=dest_language.code, instance=dest_pagecontent
            )


        if "prefill" in request.GET:
            filled_fields = []
            if "content" not in dest_pagecontent_form.initial:
                source_content = source_pagecontent_form.initial["content"]
                try:
                    translated_content = translate(
                        source_content, src=source_language.code, to=dest_language.code
                    )
                except ValueError, err:
                    messages.info(request, "Can't translate content with google: %s" % err)
                else:
                    dest_pagecontent_form.initial["content"] = translated_content
                    filled_fields.append("content")
                    dest_pagecontent_form.fields['content'].widget.attrs['class'] = 'auto_translated'

            for key, source_value in source_pagemeta_form.initial.iteritems():
                if not source_value \
                    or not isinstance(source_value, basestring)\
                    or key == "robots" \
                    or dest_pagemeta_form.initial.get(key, None):
                    # Skip empty, non string, robots field and if dest. value exist
                    continue

                try:
                    dest_value = translate(
                        source_value, src=source_language.code, to=dest_language.code
                    )
                except ValueError, err:
                    messages.info(request,
                        "Can't translate %(key)s with google: %(err)s" % {"key":key, "err":err}
                    )
                else:
                    dest_pagemeta_form.initial[key] = dest_value
                    filled_fields.append(key)
                    dest_pagemeta_form.fields[key].widget.attrs['class'] = 'auto_translated'

            if filled_fields:
                messages.info(request, "These fields are translated via google: %s" % ", ".join(filled_fields))
            else:
                messages.info(request, "No fields translated via google.")

    source_pagecontent_form.language = source_language
    dest_pagecontent_form.language = dest_language

    pagemeta_fields = []
    for source_field, dest_field in zip(source_pagemeta_form, dest_pagemeta_form):
        source_field.language = source_language
        pagemeta_fields.append(source_field)
        dest_field.language = dest_language
        pagemeta_fields.append(dest_field)

    context.update({
        "form_url": request.path,
        "abort_url": source_pagemeta.get_absolute_url(),
        "all_forms": [
            source_pagemeta_form, source_pagecontent_form,
            dest_pagemeta_form, dest_pagecontent_form
        ],
        "source_pagemeta_form": source_pagemeta_form,
        "source_pagecontent_form": source_pagecontent_form,
        "dest_pagemeta_form": dest_pagemeta_form,
        "dest_pagecontent_form": dest_pagecontent_form,

        "pagemeta_fields": pagemeta_fields,
    })
    return context


