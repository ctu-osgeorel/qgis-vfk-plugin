Návod k použití
---------------

**Rozložení**

.. image:: images/vfk.png
   :width: 600


**Import VFK souboru:**

Při importu dat nejdříve vyberte vfk soubor a následně zaškrtněte vrstvy, 
které chcete importovat (Parcely (PAR), Budovy (BUD)). Můžete zvolit obě, 
jednu z nich nebo žádnou. Pokud nezaškrtnete žádnou, načtou se pouze 
popisná data. Bude tedy možné vyhledávat informace, ale nebude možná 
interakce s mapou. Nakonec klikněte na tlačítko ``Načíst``.

.. image:: images/vfk_import.png
   :width: 600
           
**Prohlížení dat**

V panelu nástrojů stiskněte ikonu vyhledávání (dalekohled). V levé části 
prohlížeče VFK vyberte v rozbalovacím menu, co chcete vyhledat - vlastníky,
parcely, budovy nebo jednotky. Po výběru možnosti, zadejte parametry vyhledávání
a klikněte na tlačítko ``Hledej``. Můžete zadat jeden, ale i více parametrů 
vyhledávání. Vyhledané informace se zobrazí v pravém okně prohlížeče VFK.

   .. figure:: images/vfk_info.png
      :width: 600 
      
.. tip:: Pokud nezadáte žádný parametr vyhledávání, jsou vyhledány všechny 
   nemovitosti či osoby obsažené v databázi.

Prohlížeč VFK funguje obdobně jako webové prohlížeče. Kliknutím na odkaz se 
zobrazí informace o stavbě, parcele, oprávněných osobách nebo list vlastnicví.
Stejně jako ve webovém prohlížeči se ukládá historie stránek, je tedy možné 
listovat tam a zpět, a proto není třeba opakovaně vykonávat dotazy do databáze.

   .. figure:: images/vfk_link.png
      :width: 600 

   .. figure:: images/vfk_link_info.png
      :width: 600 

  
Pokud chcete zobrazit vyhledaná data v mapovém okně, klikněte na ikonu Označit 
aktuální budovy/parcely v mapě v panelu nástrojů.

   .. figure:: images/vfk_map.png
      :width: 600 
 
Plugin umožňuje také otevření aplikace Nahlížení do katastru nemovitostí ve 
webovém prohlížeči pro aktuálně zobrazovanou nemovitost. Je zavolán ten webový 
prohlížeč, který máte nastavený jako výchozí ve vašem operačním systému.

   .. figure:: images/vfk_cuzk.png
      :width: 600 

    
   .. figure:: images/cuzk.png
      :width: 600 

**Export dat**

Momentálně je možný export dat do formátů LaTex (možno následně vytvořit PDF)
a HTML (možno následně vytvořit ODF např. překopírováním HTML stránky z webového prohlížeče do `LibreOffice <https://www.libreoffice.org/>`__)

   .. figure:: images/vfk_export.png
      :width: 600 