
PyLucid v0.0.1
==============

copyleft 2005 by Jens Diemer
Wie all meine Programme, stehen auch dieses unter der GPL-Lizenz.

Aktuelle Version auf meiner Homepage: http://www.jensdiemer.de


Was ist PyLucid ?

    Python-CGI Erweiterungen f�r das LucidCMS: http://lucidcms.net/


Welche Erweiterungen ?

 Search.py + makePyLucidSearchIndex.py
 -------------------------------------
 Suche mit Index (noch nicht fertig!)


 BackLinks.py
 ------------
 Generiert eine horizontale zur�ck-Linkleiste

    Einzubinden �ber lucid-IncludeRemote-Tag:
    <lucidFunction:IncludeRemote>/cgi-bin/PyLucid/BackLinks.py?page_name=<lucidTag:page_name/></lucidFunction>

 Menu.py
 -------
 Generiert das komplette Hauptmen� mit Untermen�s

    eingebunden kann es per lucid-"IncludeRemote"-Tag:
    <lucidFunction:IncludeRemote>/cgi-bin/PyLucid/Menu.py?page_name=<lucidTag:page_name/></lucidFunction>

 ListOfNewSides.py
 -----------------
 Generiert eine Liste der Seiten die zuletzt ge�ndert worden sind


Wie benutzen ?

 1. Unter "./system/config.py" mu� der Pfad zur Konfigurations-Datei
    von Lucid angegeben werden.
 2. Das ganze auf dem WebSpace z.B. unter "/cgi-bin/PyLucid/" packen.
 3. Zum einbinden in einer CMS-Seite den "IncludeRemote"-Tag benutzen.
    z.B.:
    <lucidFunction:IncludeRemote>/cgi-bin/PyLucid/ListOfNewSides.py</lucidFunction>

 Zum lokalen Testen mu� in der "./system/config.py" die SQL-Konfig bei dict dbconf
 eingetragen werden. Diese werden dann nicht �berschrieben, sondern genutzt.


 History
=========
v0.0.2
    - neue Module: Menu, Search, BackLinks
    - ListOfNewSides: Nur Seiten Anzeigen, die auch permitViewPublic=1 sind (also öffentlich)
v0.0.1
    - erste Version