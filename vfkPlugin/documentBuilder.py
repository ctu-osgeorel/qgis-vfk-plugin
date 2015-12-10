# -*- coding: utf-8 -*-

from vfkDocument import *
from vfkTableModel import *
from htmlDocument import *
from domains import *


class Coordinates:
    def __init__(self):
        self.first = ""
        self.second = ""


class DocumentBuilder:
    def __init__(self, connectionName=""):
        # variables
        self.__mCurrentPageParIds = []
        self.__mCurrentPageBudIds = []
        self.__mCurrentDefinitionPoint = Coordinates()
        self.__mDocument = VfkDocument()

        # constructor depended decision
        if connectionName != "":
            self.__mHasConnection = True
            self.__mConnectionName = connectionName
            self.__mDveRadyCislovani = False
            self.__mStringBezZapisu = u"Bez zápisu."
            self.initKatUzemi()
        else:
            self.__mHasConnection = False

    def buildHtml(self, document, taskMap):
        self.__mCurrentPageParIds = []
        self.__mCurrentPageBudIds = []
        self.__mCurrentDefinitionPoint.first = ""
        self.__mCurrentDefinitionPoint.first = ""

        self.__mDocument = document
        self.__mDocument.header()

        ###########################
        pass




    def initKatUzemi(self):
        model = VfkTableModel(self.__mConnectionName)

        if model.dveRadyCislovani() is True:
            self.__mDveRadyCislovani = True

    def pageTelesa(self):
        model = VfkTableModel(self.__mConnectionName)

        ok = model.telesa()
        if ok is False:
            return

        for i in xrange(model.rowCount()):
            tel_id = model.value(i, "tel_id")
            cislo_tel = model.value(i, "tel_cislo_tel")
            link = self.__mDocument.link("showText?page=tel&id={}".format(tel_id), cislo_tel+"<br/>")
            self.__mDocument.text(link)

    def pageTeleso(self, id):
        parIds = []
        budIds = []
        jedIds = []
        opsubIds = []

        self.partTelesoHlavicka(id)
        self.partTelesoVlastnici(id, opsubIds, True)
        self.partTelesoNemovitosti(id, parIds, budIds, jedIds)

        self.partTelesoB1(parIds, budIds, jedIds, opsubIds, True)
        self.partTelesoC(parIds, budIds, jedIds, opsubIds, True)
        self.partTelesoD(parIds, budIds, jedIds, opsubIds, True)
        self.partTelesoE(parIds, budIds, jedIds)
        self.partTelesoF(parIds, True)

    def partTelesoHlavicka(self, id):
        hlavickaModel = VfkTableModel(self.__mConnectionName)

        ok = hlavickaModel.telesoHlavicka(id)
        if ok is False:
            return

        self.__mDocument.heading1(u"List vlastnictví")
        content = [TPair("List vlastnictví:", self.makeLVCislo(hlavickaModel, 0)),
                   TPair("Kat. území:", self.makeKatastrUzemi(hlavickaModel, 0)),
                   TPair("Obec:", self.makeObec(hlavickaModel, 0)),
                   TPair("Okres:", "{} {}".format(hlavickaModel.value(0, "okresy_nazev"),
                                                  hlavickaModel.value(0, "okresy_nuts4")))]

        self.__mDocument.keyValueTable(content)

        if hlavickaModel.dveRadyCislovani() is True:
            self.__mDocument.paragraph(u"V kat. území jsou pozemky vedeny ve dvou číselných řadách.")
        else:
            self.__mDocument.paragraph(u"V kat. území jsou pozemky vedeny v jedné číselné řadě.")

    def partTelesoNemovitosti(self, id, parIds, budIds, jedIds):
        self.__mDocument.heading2(u"B – Nemovitosti")
        self.partTelesoParcely(id, parIds)
        self.partTelesoBudovy(id, budIds)
        self.partTelesoJednotky(id, jedIds)

        self.__mCurrentPageParIds = parIds
        self.__mCurrentPageBudIds = budIds

    def partVlastnikNemovitosti(self, opsubId):
        self.__mDocument.heading2(u"Nemovitosti vlastníka")
        self.partVlastnikParcely(opsubId)
        self.partVlastnikBudovy(opsubId)
        self.partVlastnikJednotky(opsubId)

    def partTelesoParcely(self, opsubId, parIds):
        model = VfkTableModel(self.__mConnectionName)

        ok = model.telesoParcely(opsubId, False)
        if ok is False or model.rowCount() == 0:
            return

        self.tableParcely(model, parIds, False)

    def partVlastnikParcely(self, id):
        model = VfkTableModel(self.__mConnectionName)

        ok = model.vlastnikParcely(id, False)
        if ok is False or model.rowCount() == 0:
            return

        parIds = []
        self.tableParcely(model, parIds, False)
        self.__mCurrentPageParIds = parIds

    def tableParcely(self, model, parIds, LVColumn):
        self.__mDocument.heading3(u"Pozemky")
        self.__mDocument.beginTable()
        header = ["Parcela", "Výměra [m{}]".format(self.__mDocument.superScript("2")), "Druh pozemku", "Způsob využití",
                  "Způsob ochrany"]
        if LVColumn is True:
            header.append("LV")

        self.__mDocument.tableHeader(header)

        for i in xrange(model.rowCount()):
            row = [self.makeParcelniCislo(model, i), model.value(i, "par_vymera_parcely"),
                   model.value(i, "drupoz_nazev"), model.value(i, "zpvypo_nazev")]

            parcelaId = model.value(i, "par_id")
            ochranaModel = VfkTableModel(self.__mConnectionName)

            ok = ochranaModel.nemovitostOchrana(parcelaId, VfkTableModel.Nemovitost.NParcela)
            if ok is False:
                break

            ochranaNazev = []
            for j in xrange(ochranaModel.rowCount()):
                ochranaNazev.append(ochranaModel.value(j, "zpochn_nazev"))

            row.append(", ".join(ochranaNazev))

            if LVColumn is True:
                row.append(self.makeLVCislo(model, i))

            self.__mDocument.tableRow(row)
            parIds.append(parcelaId)
        self.__mDocument.endTable()

    def partTelesoBudovy(self, opsubId, budIds):
        model = VfkTableModel(self.__mConnectionName)

        ok = model.telesoBudovy(opsubId, False)
        if ok is False or model.rowCount() == 0:
            return

        self.tableBudovy(model, budIds, False)

    def partVlastnikBudovy(self, id):
        model = VfkTableModel(self.__mConnectionName)

        ok = model.vlastnikBudovy(id, False)
        if ok is False or model.rowCount() == 0:
            return

        budIds = []
        self.tableBudovy(model, budIds, True)
        self.__mCurrentPageBudIds.append(budIds)

    def tableBudovy(self, model, budIds, LVColumn):
        self.__mDocument.heading3("Stavby")
        self.__mDocument.beginTable()
        header = ["Typ stavby", "Část obce", "Č. budovy", "Způsob využití", "Způsob ochrany", "Na parcele"]

        if LVColumn is True:
            header.append("LV")

        self.__mDocument.tableHeader(header)

        for i in xrange(model.rowCount()):
            row = []

            if Domains.anoNe(model.value(i, "typbud_zadani_cd")) is False:
                row.append(self.__mDocument.link("showText?page=bud&id={}".format(model.value(i, "bud_id")),
                                                 model.value(i, "typbud_zkratka")))
                row.append(model.value(i, "casobc_nazev"))
                row.append("")
            else:
                row.append("")
                row.append(model.value(i, "casobc_nazev"))
                row.append(self.__mDocument.link("showText?page=bud&id={}".format(model.value(i, "bud_id")),
                                                 "{} {}".format(model.value(i, "typbud_zkratka"),
                                                                model.value(i, "bud_cislo_domovni"))))
            row.append(model.value(i, "zpvybu_nazev"))

            budId = model.value(i, "bud_id")
            ochranaModel = VfkTableModel(self.__mConnectionName)

            ok = ochranaModel.nemovitostOchrana(budId, VfkTableModel.Nemovitost.NBudova)
            if ok is False:
                break

            ochranaNazev = []
            for j in xrange(ochranaModel.rowCount()):
                ochranaNazev.append(ochranaModel.value(j, "zpochn_nazev"))

            row.append(", ".join(ochranaNazev))
            row.append(self.makeParcelniCislo(model, i))

            if LVColumn is True:
                row.append(self.makeLVCislo(model, i))

            self.__mDocument.tableRow(row)
            budIds.append(budId)
        self.__mDocument.endTable()





    def currentParIds(self):
        return self.__mCurrentPageParIds

    def currentBudIds(self):
        return self.__mCurrentPageBudIds

    def currentDefinitionPoint(self):
        return self.__mCurrentDefinitionPoint
