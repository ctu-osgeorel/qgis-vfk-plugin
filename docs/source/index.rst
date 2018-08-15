Zásuvný modul QGIS pro práci s katastrálními daty ve formátu VFK
================================================================

QGIS VFK Plugin pracuje s daty českého katastru nemovitostí a to v takzvaném **novém 
výměnném formátu katastru** označovaném **VFK** či **NVF** (`Výměnný formát ISKN <http://freegis.fsv.cvut.cz/gwiki/V%C3%BDm%C4%9Bnn%C3%BD_form%C3%A1t_ISKN>`__). 
Plugin umožňuje vyhledávání, zobrazování a export informací vedených v 
katastru nemovitostí. 

.. important:: V současnosti je dostupný plugin pouze pro verzi **QGIS
   2.x**. Nová verze pro QGIS 3 je v přípravě, v případě zájmu se
   nezdráhejte oslovit autory.

.. toctree::
   :maxdepth: 2

   instalace
   popis
   dodatek

.. note:: První prototyp (verze 1.x) byl napsán v jazyce C++, ve verzi
          2.x byl portován do jazyka Python. K datům v souborech
          přistupuje plugin pomocí `knihovny GDAL
          <http://freegis.fsv.cvut.cz/gwiki/VFK_/_GDAL>`__. Tato
          dokumentace čerpá z `wiki projektu
          <http://freegis.fsv.cvut.cz/gwiki/VFK_/_QGIS_plugin>`__, kde
          najdete další informace především historického charakteru.
