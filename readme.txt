
PyLucid v0.2.0
==============

copyleft 2005 by Jens Diemer
Wie all meine Programme, stehen auch dieses unter der GPL-Lizenz.

Aktuelle Version auf meiner Homepage: http://www.jensdiemer.de


!!! Diese Doku mu� noch aktualisiert werden !!!


Was ist PyLucid ?

PyLucid entwickelt sich langsam zum eigenst�ndigen CMS in pure Python CGI! Es ben�tigt keine zus�tzlichen Module (au�er der SQL anbindung �ber mySQLdb ) und ist ab Python v2.2.1 lauff�hig (evtl. auch mit noch �lteren Versionen). mySQLdb ist allerdings i.d.R. bei jedem WebHoster vorinstalliert.
Da die Datenbankarchitektur in der Basis gleich zum PHP LucidCMS ist, kann man beide systeme parallel betreiben. Das hei�t, man kann die komplette Administration aus beiden Systemen gleichzeitig nutzen.

Nun wird meine Homepage komplett mit PyLucid gerendert. Dazu kommt TinyTextile zum einsatz.


Welche Module gibt es?

 <lucidTag:back_links/> - BackLinks.py
 -------------------------------------
 Generiert eine horizontale zur�ck-Linkleiste

    !!!Obsolet!!! Einzubinden �ber lucid-IncludeRemote-Tag:
    <lucidFunction:IncludeRemote>http://localhost/cgi-bin/PyLucid/BackLinks.py?page_name=<lucidTag:page_name/></lucidFunction>



 <lucidTag:main_menu/> - Menu.py
 -------------------------------
 Generiert das komplette Hauptmen� mit Untermen�s

    !!!Obsolet!!! eingebunden kann es per lucid-"IncludeRemote"-Tag:
    <lucidFunction:IncludeRemote>http://localhost/cgi-bin/PyLucid/Menu.py?page_name=<lucidTag:page_name/></lucidFunction>



 ListOfNewSides.py
 -----------------
 Generiert eine Liste der Seiten die zuletzt ge�ndert worden sind



Wie benutzen ?

 !!!Obsolet!!!

 1. Unter "./system/config.py" mu� der Pfad zur Konfigurations-Datei
    von Lucid angegeben werden.
 2. Das ganze auf dem WebSpace z.B. unter "/cgi-bin/PyLucid/" packen.
 3. Zum einbinden in einer CMS-Seite den "IncludeRemote"-Tag benutzen.
    z.B.: <lucidFunction:IncludeRemote>http://localhost/cgi-bin/PyLucid/ListOfNewSides.py</lucidFunction>
    ( http://localhost mu� evtl. durch den Domainnamen ersetzt werden! )

 Zum lokalen Testen mu� in der "./system/config.py" die SQL-Konfig bei dict dbconf
 eingetragen werden. Diese werden dann nicht �berschrieben, sondern genutzt.


 History
=========
v0.0.4
    - Gro�er Umbau, da das rendern der Seiten nun von PyLucid, also den Python CGI's, �bernommen wird
v0.0.3
    - Menu: Menulink mit 'title' erweitert, Link-Text ist nun 'name'
v0.0.2
    - neue Module: Menu, Search, BackLinks
    - ListOfNewSides: Nur Seiten Anzeigen, die auch permitViewPublic=1 sind (also öffentlich)
v0.0.1
    - erste Version