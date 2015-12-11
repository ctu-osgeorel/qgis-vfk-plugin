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

    def partTelesoJednotky(self, id, jedIds):
        model = VfkTableModel(self.__mConnectionName)

        ok = model.telesoJednotky(id, False)
        if ok is False or model.rowCount() == 0:
            return

        self.tableJednotky(model, jedIds, False)

    def partVlastnikJednotky(self, opsubId):
        model = VfkTableModel(self.__mConnectionName)

        ok = model.vlastnikJednotky(opsubId, False)
        if ok is False or model.rowCount() == 0:
            return

        jedIds = []
        self.tableJednotky(model, jedIds, True)

    def tableJednotky(self, model, jedIds, LVColumn):
        self.__mDocument.heading3(u"Jednotky")
        self.__mDocument.beginTable()
        header = ["Č.p./Č.jednotky ", "Způsob využití", "Způsob ochrany",
                  "Podíl na společných{}částech domu a pozemku".format(self.__mDocument.newLine())]

        if LVColumn is True:
            header.append("LV")

        self.__mDocument.tableHeader(header)

        for i in xrange(model.rowCount()):
            row = []

            jedId = model.value(i, "jed_id")
            row.append(self.makeJednotka(model, i))
            row.append(model.value(i, "zpvyje_nazev"))
            ochranaModel = VfkTableModel(self.__mConnectionName)

            ok = ochranaModel.nemovitostOchrana(jedId, VfkTableModel.Nemovitost.NJednotka)
            if ok is False:
                break

            ochranaNazev = []
            for j in xrange(ochranaModel.rowCount()):
                ochranaNazev.append(ochranaModel.value(j, "zpochn_nazev"))

            row.append(", ".join(ochranaNazev))

            podilCit = str(model.value(i, "jed_podil_citatel"))
            podilJmen = str(model.value(i, "jed_podil_jmenovatel"))
            podil = ""

            if podilCit and podilJmen and podilJmen != "1":
                podil += "{}/{}".format(podilCit, podilJmen)

            row.append(podil)

            if LVColumn:
                row.append(self.makeLVCislo(model, i))

            self.__mDocument.tableRow(row)
            self.partTelesoJednotkaDetail(model.value(i, "bud_id"))

            jedIds.append(jedId)
        self.__mDocument.endTable()

    def partTelesoJednotkaDetail(self, budId):
        """

        :param budId: str
        :return:
        """
        budInfo = ""
        parInfo = ""

        budModel = VfkTableModel(self.__mConnectionName)
        ok = budModel.budova(budId, False)
        if ok is False or budModel.rowCount() == 0:
            return

        budInfo += "Budova" + " "
        casobc = budModel.value(0, "casobc_nazev")
        budInfo += "" if casobc else casobc + ", "

        budova = ""
        budova += budModel.value(0, "typbud_zkratka")
        if Domains.anoNe(budModel.value(0, "typbud_zadani_cd")):
            budova += " " + budModel.value(0, "bud_cislo_domovni")
        budInfo += self.__mDocument.link("showText?page=bud&id={}".format(budId), budova)

        lv = budModel.value(0, "tel_cislo_tel")
        lvId = budModel.value(0, "tel_id")
        if lv:
            budInfo += self.__mDocument.link("showText?page=tel&id={}".format(lvId), "LV {}".format(lv))

        zpvybu = budModel.value(0, "zpvybu_nazev")
        budInfo += "" if not zpvybu else ", {}".format(zpvybu)

        budInfo + ", na parcele {}".format(self.makeParcelniCislo(budModel, 0))

        self.__mDocument.tableRowOneColumnSpan(budInfo)

        parcelaId = budModel.value(0, "par_id")
        parModel = VfkTableModel(self.__mConnectionName)
        ok = parModel.parcela(parcelaId, False)
        if ok is False:
            return

        parInfo += "Parcela {}".format(self.makeParcelniCislo(parModel, 0))
        lv = parModel.value(0, "tel_cislo_tel")
        lvId = parModel.value(0, "tel_id")
        if lv:
            parInfo += self.__mDocument.link("showText?page=tel&id={}".format(lvId), "LV {}".format(lv))

        zpvypo = parModel.value(0, "zpvypo_nazev")
        parInfo += "" if not zpvypo else ", {}".format(zpvypo)
        parInfo += ", {} m{}".format(parModel.value(0, "par_vymera_parcely"), self.__mDocument.superScript("2"))

        self.__mDocument.tableRowOneColumnSpan(parInfo)

    def partTelesoB1(self, parIds, budIds, jedIds, opsubIds, forLV):
        """

        :param parIds: list
        :param budIds: list
        :param jedIds: list
        :param opsubIds: list
        :param forLV: bool
        """

        header = ["Typ vztahu", "Oprávnění pro", "Povinnost k"]

        if forLV:
            self.__mDocument.heading2("B1 – Jiná práva")
            self.__mDocument.beginTable()
            self.__mDocument.tableHeader(header)

            if self.partTelesoJinaPrava( parIds, VfkTableModel.OpravnenyPovinny.OPParcela ) or \
                    self.partTelesoJinaPrava(budIds, VfkTableModel.OpravnenyPovinny.OPBudova) or \
                    self.partTelesoJinaPrava(jedIds, VfkTableModel.OpravnenyPovinny.OPJednotka ) or \
                    self.partTelesoJinaPrava(opsubIds, VfkTableModel.OpravnenyPovinny.OPOsoba):
                self.__mDocument.endTable()
            else:
                self.__mDocument.discardLastBeginTable()
                self.__mDocument.text(self.__mStringBezZapisu)
        else:
            self.__mDocument.heading2("Jiná práva")
            self.__mDocument.beginTable()
            self.__mDocument.tableHeader(header)

            if self.partNemovitostJinaPrava(parIds, VfkTableModel.OpravnenyPovinny.OPParcela) or \
                    self.partNemovitostJinaPrava(budIds, VfkTableModel.OpravnenyPovinny.OPBudova) or \
                    self.partNemovitostJinaPrava(jedIds, VfkTableModel.OpravnenyPovinny.OPJednotka) or \
                    self.partNemovitostJinaPrava(opsubIds, VfkTableModel.OpravnenyPovinny.OPOsoba):
                self.__mDocument.endTable()
            else:
                self.__mDocument.discardLastBeginTable()
                self.__mDocument.text(self.__mStringBezZapisu)

    def partTelesoC(self, parIds, budIds, jedIds, opsubIds, forLV):
        """

        :param parIds: list
        :param budIds: list
        :param jedIds: list
        :param opsubIds: list
        :param forLV: bool
        """
        header = ["Typ vztahu", "Oprávnění pro", "Povinnost k"]

        if forLV:
            self.__mDocument.heading2("C – Omezení vlastnického práva")
            self.__mDocument.beginTable()
            self.__mDocument.tableHeader(header)

            if self.partTelesoOmezeniPrava(parIds, VfkTableModel.OpravnenyPovinny.OPParcela) or \
                    self.partTelesoOmezeniPrava(budIds, VfkTableModel.OpravnenyPovinny.OPBudova) or \
                    self.partTelesoOmezeniPrava(jedIds, VfkTableModel.OpravnenyPovinny.OPJednotka) or \
                    self.partTelesoOmezeniPrava(opsubIds, VfkTableModel.OpravnenyPovinny.OPOsoba):
                self.__mDocument.endTable()
            else:
                self.__mDocument.discardLastBeginTable()
                self.__mDocument.text(self.__mStringBezZapisu)
        else:
            self.__mDocument.heading2("Omezení vlastnického práva")
            self.__mDocument.beginTable()
            self.__mDocument.tableHeader(header)

            if self.partNemovitostOmezeniPrava(parIds, VfkTableModel.OpravnenyPovinny.OPParcela) or \
                    self.partNemovitostOmezeniPrava(budIds, VfkTableModel.OpravnenyPovinny.OPBudova) or \
                    self.partNemovitostOmezeniPrava(jedIds, VfkTableModel.OpravnenyPovinny.OPJednotka) or \
                    self.partNemovitostOmezeniPrava(opsubIds, VfkTableModel.OpravnenyPovinny.OPOsoba):
                self.__mDocument.endTable()
            else:
                self.__mDocument.discardLastBeginTable()
                self.__mDocument.text(self.__mStringBezZapisu)

    def partTelesoD(self, parIds, budIds, jedIds, opsubIds, forLV):
        """

        :param parIds: list
        :param budIds: list
        :param jedIds: list
        :param opsubIds: list
        :param forLV: bool
        """
        header = ["Typ vztahu", "Vztah pro", "Vztah k"]

        if forLV:
            self.__mDocument.heading2("D – Jiné zápisy")
            self.__mDocument.beginTable()
            self.__mDocument.tableHeader(header)

            if self.partTelesoJineZapisy(parIds, VfkTableModel.OpravnenyPovinny.OPParcela) or \
                    self.partTelesoJineZapisy(budIds, VfkTableModel.OpravnenyPovinny.OPBudova) or \
                    self.partTelesoJineZapisy(jedIds, VfkTableModel.OpravnenyPovinny.OPJednotka) or \
                    self.partTelesoJineZapisy(opsubIds, VfkTableModel.OpravnenyPovinny.OPOsoba):
                self.__mDocument.endTable()
            else:
                self.__mDocument.discardLastBeginTable()
                self.__mDocument.text(self.__mStringBezZapisu)
        else:
            self.__mDocument.heading2("D – Jiné zápisy")
            self.__mDocument.beginTable()
            self.__mDocument.tableHeader(header)

            if self.partNemovitostJineZapisy(parIds, VfkTableModel.OpravnenyPovinny.OPParcela) or \
                    self.partNemovitostJineZapisy(budIds, VfkTableModel.OpravnenyPovinny.OPBudova) or \
                    self.partNemovitostJineZapisy(jedIds, VfkTableModel.OpravnenyPovinny.OPJednotka) or \
                    self.partNemovitostJineZapisy(opsubIds, VfkTableModel.OpravnenyPovinny.OPOsoba):
                self.__mDocument.endTable()
            else:
                self.__mDocument.discardLastBeginTable()
                self.__mDocument.text(self.__mStringBezZapisu)

    def partTelesoE(self, parIds, budIds, jedIds):
        """

        :param parIds: list
        :param budIds: list
        :param jedIds: list
        """
        self.__mDocument.heading2("E – Nabývací tituly a jiné podklady k zápisu")

        model = VfkTableModel(self.__mConnectionName)
        ok = model.nabyvaciListiny(parIds, budIds, jedIds)
        if ok is False:
            return

        if model.rowCount() == 0:
            self.__mDocument.text(self.__mStringBezZapisu)
        else:
            lastListinaId = ""
            self.__mDocument.beginItemize()
            for i in xrange(model.rowCount()):
                currentListinaId = model.value(i, "rl_listin_id")
                if currentListinaId == lastListinaId:
                    self.__mDocument.item(self.makeShortDescription(model.value(i, "rl_opsub_id"),
                                                                    VfkTableModel.OpravnenyPovinny.OPOsoba))
                else:
                    if lastListinaId:
                        self.__mDocument.endItemize()
                        self.__mDocument.endItem()
                    lastListinaId = currentListinaId
                    self.__mDocument.beginItem()
                    self.__mDocument.text(self.makeListina(model, i))
                    self.__mDocument.beginItemize()
                    self.__mDocument.item(self.makeShortDescription(model.value(i, "rl_opsub_id"),
                                                                    VfkTableModel.OpravnenyPovinny.OPOsoba))

            if lastListinaId:
                self.__mDocument.endItemize()
                self.__mDocument.endItem()

            self.__mDocument.endItemize()

    def partTelesoF(self, parIds, forLV):
        """

        :param parIds: list
        :param forLV: bool
        """
        if forLV:
            self.__mDocument.heading2("F – Vztah bonitovaných půdně ekologických jednotek (BPEJ) k parcelám")
        else:
            self.__mDocument.heading2("BPEJ")

        header = ["Parcela", "BPEJ", "Výměra [m{}]".format(self.__mDocument.superScript("2"))]
        self.__mDocument.beginTable()
        self.__mDocument.tableHeader(header)

        isRecord = False
        for id in parIds:
            row = []
            model = VfkTableModel(self.__mConnectionName)
            ok = model.parcelaBpej(id)
            if ok is False:
                break

            if model.rowCount() == 0:
                continue

            isRecord = True
            row.append(self.makeParcelniCislo(model, 0))
            row.append(model.value(0, "bdp_bpej_kod"))
            row.append(model.value(0, "bdp_vymera"))

            self.__mDocument.tableRow(row)

        if isRecord:
            self.__mDocument.endTable()
        else:
            self.__mDocument.discardLastBeginTable()
            self.__mDocument.text(self.__mStringBezZapisu)

    def partNemovitostJinaPrava(self, ids, opravneny):
        """

        :param ids: list
        :param opravneny: VfkTableModel.OpravnenyPovinny
        :return:
        """
        return self.partTelesoB1CDSubjekt(ids, opravneny, VfkTableModel.Pravo.Opravneni, False, False)

    def partTelesoJinaPrava(self, ids, opravneny):
        """

        :param ids: list
        :param opravneny: VfkTableModel.OpravnenyPovinny
        :return:
        """
        return self.partTelesoB1CDSubjekt(ids, opravneny, VfkTableModel.Pravo.Opravneni, False, True)

    def partNemovitostOmezeniPrava(self, ids, povinny):
        """

        :param ids: list
        :param povinny: VfkTableModel.OpravnenyPovinny
        :return:
        """
        return self.partTelesoB1CDSubjekt(ids, povinny, VfkTableModel.Pravo.Povinnost, False, False)

    def partTelesoOmezeniPrava(self, ids, povinny):
        """

        :param ids: list
        :param povinny: VfkTableModel.OpravnenyPovinny
        :return:
        """
        return self.partTelesoB1CDSubjekt(ids, povinny, VfkTableModel.Pravo.Povinnost, False, True)

    def partNemovitostJineZapisy(self, ids, povinny):
        """

        :param ids: list
        :param povinny: VfkTableModel.OpravnenyPovinny
        :return: bool
        """
        test1 = self.partTelesoB1CDSubjekt(ids, povinny, VfkTableModel.Pravo.Opravneni, True, False)
        test2 = self.partTelesoB1CDSubjekt(ids, povinny, VfkTableModel.Pravo.Povinnost, True, False)
        return test1 or test2

    def partTelesoJineZapisy(self, ids, povinny):
        """

        :param ids: list
        :param povinny: VfkTableModel.OpravnenyPovinny
        :return: bool
        """
        test1 = self.partTelesoB1CDSubjekt(ids, povinny, VfkTableModel.Pravo.Opravneni, True, True)
        test2 = self.partTelesoB1CDSubjekt(ids, povinny, VfkTableModel.Pravo.Povinnost, True, True)
        return test1 or test2

    def partTelesoB1CDSubjekt(self, ids, pravniSubjekt, pravo, sekceD, showListiny):
        """

        :param ids: list
        :param pravniSubjekt: VfkTableModel.OpravnenyPovinny
        :param pravo: VfkTableModel.Pravo
        :param sekceD: bool
        :param showListiny: bool
        :return: bool
        """
        isRecord = False
        povinni = ["jpv_par_id_k", "jpv_bud_id_k", "jpv_jed_id_k", "jpv_opsub_id_k"]
        opravneni = ["jpv_par_id_pro", "jpv_bud_id_pro", "jpv_jed_id_pro", "jpv_opsub_id_pro"]

        for id in ids:
            model = VfkTableModel(self.__mConnectionName)
            where = "typrav.sekce {}= \"D\"".format("" if sekceD else "!")
            ok = model.nemovitostJpv(id, pravniSubjekt, pravo, where)
            if ok is False or model.rowCount() == 0:
                continue

            isRecord = True
            for i in xrange(model.rowCount()):
                row = []
                typPrava = model.value(i, "typrav_nazev")
                row.append(typPrava)

                opravneniList = []
                for column1 in opravneni:
                    if model.value(i, column1):
                        opravneny = VfkTableModel.tableName2OpravnenyPovinny(column1)
                        opravnenyId = model.value(i, column1)
                        opravneniList.append(self.makeShortDescription(opravnenyId, opravneny))

                row.append(str(self.__mDocument.newLine()).join(opravneniList))

                povinniList = []
                for column2 in povinni:
                    if model.value(i, column2):
                        povinny = VfkTableModel.tableName2OpravnenyPovinny(column2)
                        povinnyId = model.value(i, column2)
                        povinniList.append(self.makeShortDescription(povinnyId, povinny))

                row.append(str(self.__mDocument.newLine()).join(povinniList))

                self.__mDocument.tableRow(row)

                if showListiny:
                    self.partTelesoListiny(model.value(i, "jpv_id"))

        return isRecord

    def partTelesoListiny(self, jpvId):
        """

        :param jpvId: str
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)
        ok = model.jpvListiny(jpvId)
        if ok is False:
            return

        for i in xrange(model.rowCount()):
            self.__mDocument.tableRowOneColumnSpan(self.makeListina(model, i))

    def pageParcela(self, id):
        """

        :param id: str
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)
        ok = model.parcela(id, True)
        if ok is False:
            return

        self.__mCurrentPageParIds.append(id)
        self.saveDefinitionPoint(id, VfkTableModel.Nemovitost.NParcela)

        content = [TPair("Parcelní číslo:", self.makeParcelniCislo(model, 0))]

        telesoModel = VfkTableModel(self.__mConnectionName)
        telesoModel.nemovitostTeleso(id, VfkTableModel.Nemovitost.NParcela)
        content.append(TPair("List vlastnictví:", self.makeLVCislo(telesoModel, 0)))
        content.append(TPair("Výměra [m{}]:".format(self.__mDocument.superScript("2")),
                             model.value(0, "par_vymera_parcely")))
        content.append(TPair("Určení výměry:", model.value(0, "zpurvy_nazev")))

        if model.value(0, "par_cena_nemovitosti"):
            content.append(TPair("Cena nemovitosti:", model.value(0, "par_cena_nemovitosti")))

        content.append(TPair("Typ parcely:", model.value(0, "par_par_type")))
        content.append(TPair("Mapový list:", model.value(0, "maplis_oznaceni_mapoveho_listu")))
        content.append(TPair("Katastrální území:", self.makeKatastrUzemi(model, 0)))
        content.append(TPair("Druh pozemku:", model.value(0, "drupoz_nazev")))

        if model.value(0, "zpvypo_nazev"):
            content.append(TPair("Způsob využití pozemku:", model.value(0, "zpvypo_nazev")))

        if Domains.anoNe(model.value(0, "drupoz_stavebni_parcela")):
            content.append(TPair("Stavba na parcele:", self.makeDomovniCislo(model, 0)))
            self.__mCurrentPageBudIds.append(model.value(0, "bud_id"))

        self.__mDocument.heading1("Informace o parcele")
        self.__mDocument.keyValueTable(content)

        sousedniModel = VfkTableModel(self.__mConnectionName)
        sousedniModel.sousedniParcely(id)
        ids = []
        for i in sousedniModel.rowCount():
            ids.append(sousedniModel.value(i, "hp_par_id_1"))
            ids.append(sousedniModel.value(i, "hp_par_id_2"))

        ids = list(set(ids))
        ids.remove(id)

        link = self.__mDocument.link("showText?page=seznam&type=id&parcely={}".format(",".join(ids)),
                                     "Sousední parcely")

        self.__mDocument.paragraph(link)
        opsubIds = []
        self.partTelesoVlastnici(telesoModel.value(0, "tel_id"), opsubIds, False)
        self.partNemovitostOchrana(id, VfkTableModel.Nemovitost.NParcela)

        parIds = [id]
        tempList = []
        self.partTelesoB1(parIds, tempList, tempList, tempList, False)
        self.partTelesoC(parIds, tempList, tempList, tempList, False)
        self.partTelesoD(parIds, tempList, tempList, tempList, False)
        self.partTelesoF(parIds, False)






    def currentParIds(self):
        return self.__mCurrentPageParIds

    def currentBudIds(self):
        return self.__mCurrentPageBudIds

    def currentDefinitionPoint(self):
        return self.__mCurrentDefinitionPoint
