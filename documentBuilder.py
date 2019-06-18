from __future__ import absolute_import
from builtins import str
from builtins import range
from builtins import object
# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QObject

from qgis.utils import iface

from .vfkDocument import *
from .vfkTableModel import *
from .htmlDocument import *
from .domains import *

class Coordinates(object):

    def __init__(self):
        self.first = u''
        self.second = u''


class DocumentBuilder(object):

    def __init__(self, connectionName=''):
        """
        :type connectionName: str
        """
        # variables
        self.__mCurrentPageParIds = []
        self.__mCurrentPageBudIds = []
        self.__mCurrentDefinitionPoint = Coordinates()
        self.__mDocument = None

        # constructor depended decision
        if connectionName:
            self.__mHasConnection = True
            self.__mConnectionName = connectionName
            self.__mDveRadyCislovani = False
            self.__mStringBezZapisu = u"Bez zápisu."
            self.initKatUzemi()
        else:
            self.__mHasConnection = False

    def currentParIds(self):
        return self.__mCurrentPageParIds

    def currentBudIds(self):
        return self.__mCurrentPageBudIds

    def currentDefinitionPoint(self):
        return self.__mCurrentDefinitionPoint

    def buildHtml(self, document, taskMap):
        """

        :type document: VfkDocument
        :type taskMap: dict
        """
        self.__mCurrentPageParIds = []
        self.__mCurrentPageBudIds = []
        self.__mCurrentDefinitionPoint.first = ''
        self.__mCurrentDefinitionPoint.second = ''

        self.__mDocument = document
        self.__mDocument.header()

        if taskMap["page"] == "help":
            self.pageHelp()

        if self.__mHasConnection:
            if taskMap["page"] == "tel":
                self.pageTeleso(taskMap["id"])
            elif taskMap["page"] == "par":
                self.pageParcela(taskMap["id"])
            elif taskMap["page"] == "bud":
                self.pageBudova(taskMap["id"])
            elif taskMap["page"] == "jed":
                self.pageJednotka(taskMap["id"])
            elif taskMap["page"] == "opsub":
                self.pageOpravnenySubjekt(taskMap["id"])
            elif taskMap["page"] == "seznam":
                if taskMap["type"] == "id":
                    if "parcely" in taskMap:
                        self.pageSeznamParcel(taskMap["parcely"].split(","))
                    if "budovy" in taskMap:
                        self.pageSeznamBudov(taskMap["budovy"].split(","))
                elif taskMap["type"] == "string":
                    if "opsub" in taskMap:
                        self.pageSeznamOsob(taskMap['opsub'].split(","))
            elif taskMap["page"] == "search":
                if taskMap["type"] == "vlastnici":
                    self.pageSearchVlastnici(
                        taskMap["jmeno"], taskMap["rcIco"],
                                             taskMap["sjm"], taskMap["opo"],
                                             taskMap["ofo"], taskMap["lv"])
                elif taskMap["type"] == "parcely":
                    self.pageSearchParcely(
                        taskMap["parcelniCislo"], taskMap["typ"], taskMap["druh"], taskMap["lv"])
                elif taskMap["type"] == "budovy":
                    self.pageSearchBudovy(
                        taskMap["domovniCislo"], taskMap[
                            "naParcele"], taskMap["zpusobVyuziti"],
                                          taskMap["lv"])
                elif taskMap["type"] == "jednotky":
                    self.pageSearchJednotky(
                        taskMap["cisloJednotky"], taskMap[
                            "domovniCislo"], taskMap["naParcele"],
                                            taskMap["zpusobVyuziti"], taskMap["lv"])
        self.__mDocument.footer()
        return

    def initKatUzemi(self):
        model = VfkTableModel(self.__mConnectionName)

        if model.dveRadyCislovani():
            self.__mDveRadyCislovani = True

    def pageTelesa(self):
        model = VfkTableModel(self.__mConnectionName)

        ok = model.telesa()
        if not ok:
            return

        for i in range(model.rowCount()):
            tel_id = model.value(i, u"tel_id")
            cislo_tel = model.value(i, u"tel_cislo_tel")
            link = self.__mDocument.link(
                u"showText?page=tel&id={}".format(tel_id), cislo_tel + u"<br/>")
            self.__mDocument.text(link)

    def pageTeleso(self, id):
        """

        :type id: str
        :return:
        """
        parIds = []
        budIds = []
        jedIds = []
        opsubIds = []

        self.partTelesoHlavicka(id)
        # self.partTelesoVlastnici(id, opsubIds, True)
        self.partTelesoNemovitosti(id, parIds, budIds, jedIds)

        self.partTelesoB1(parIds, budIds, jedIds, opsubIds, True)
        self.partTelesoC(parIds, budIds, jedIds, opsubIds, True)
        self.partTelesoD(parIds, budIds, jedIds, opsubIds, True)
        self.partTelesoE(parIds, budIds, jedIds)
        self.partTelesoF(parIds, True)

    def partTelesoHlavicka(self, id):
        """

        :type id: str
        :return:
        """
        hlavickaModel = VfkTableModel(self.__mConnectionName)

        ok = hlavickaModel.telesoHlavicka(id)
        if not ok:
            return

        self.__mDocument.heading1(u"List vlastnictví")
        content = [TPair(
            u"List vlastnictví:", self.makeLVCislo(hlavickaModel, 0)),
            TPair(
            u"Kat. území:", self.makeKatastrUzemi(hlavickaModel, 0)),
                   TPair(u"Obec:", self.makeObec(hlavickaModel, 0)),
                   TPair(
                       u"Okres:", u"{} {}".format(hlavickaModel.value(0, u"okresy_nazev"),
                                                  hlavickaModel.value(0, u"okresy_nuts4")))]

        self.__mDocument.keyValueTable(content)

        if hlavickaModel.dveRadyCislovani():
            self.__mDocument.paragraph(
                u"V kat. území jsou pozemky vedeny ve dvou číselných řadách.")
        else:
            self.__mDocument.paragraph(
                u"V kat. území jsou pozemky vedeny v jedné číselné řadě.")

    def partTelesoNemovitosti(self, id, parIds, budIds, jedIds):
        """

        :type id: str
        :type parIds: list
        :type budIds: list
        :type jedIds: list
        """
        self.__mDocument.heading2(u"B – Nemovitosti")
        self.partTelesoParcely(id, parIds)
        self.partTelesoBudovy(id, budIds)
        self.partTelesoJednotky(id, jedIds)

        self.__mCurrentPageParIds = parIds
        self.__mCurrentPageBudIds = budIds

    def partVlastnikNemovitosti(self, opsubId):
        """

        :type opsubId: str
        """
        self.__mDocument.heading2(u"Nemovitosti vlastníka")
        self.partVlastnikParcely(opsubId)
        self.partVlastnikBudovy(opsubId)
        self.partVlastnikJednotky(opsubId)

    def partTelesoParcely(self, opsubId, parIds):
        """

        :type opsubId: str
        :type parIds: list
        """
        model = VfkTableModel(self.__mConnectionName)

        ok = model.telesoParcely(opsubId, False)
        if not ok or model.rowCount() == 0:
            return

        self.tableParcely(model, parIds, False)

    def partVlastnikParcely(self, id):
        """

        :type id: str
        """
        model = VfkTableModel(self.__mConnectionName)

        ok = model.vlastnikParcely(id, False)
        if not ok or model.rowCount() == 0:
            return

        parIds = []
        self.tableParcely(model, parIds, True)
        self.__mCurrentPageParIds = parIds

    def tableParcely(self, model, parIds, LVColumn):
        """

        :type model: VfkTableModel
        :type parIds: list
        :type LVColumn: bool
        """
        self.__mDocument.heading3(u"Pozemky")
        self.__mDocument.beginTable()
        header = [
            u"Parcela", u"Výměra [m{}]".format(
                self.__mDocument.superScript(
                    u"2")), u"Druh pozemku", u"Způsob využití",
                  u"Způsob ochrany"]
        if LVColumn:
            header.append(u"LV")

        self.__mDocument.tableHeader(header)

        for i in range(model.rowCount()):
            row = [self.makeParcelniCislo(
                model, i), model.value(i, u"par_vymera_parcely"),
                model.value(i, u"drupoz_nazev"), model.value(i, u"zpvypo_nazev")]

            parcelaId = model.value(i, u"par_id")
            ochranaModel = VfkTableModel(self.__mConnectionName)

            ok = ochranaModel.nemovitostOchrana(
                parcelaId, VfkTableModel.Nemovitost.NParcela)
            if not ok:
                break

            ochranaNazev = []
            for j in range(ochranaModel.rowCount()):
                ochranaNazev.append(ochranaModel.value(j, u"zpochn_nazev"))

            row.append(u", ".join(ochranaNazev))

            if LVColumn:
                row.append(self.makeLVCislo(model, i))

            self.__mDocument.tableRow(row)
            parIds.append(parcelaId)
        self.__mDocument.endTable()

    def partTelesoBudovy(self, opsubId, budIds):
        """

        :type opsubId: str
        :type budIds: list
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)

        ok = model.telesoBudovy(opsubId, False)
        if not ok or model.rowCount() == 0:
            return

        self.tableBudovy(model, budIds, False)

    def partVlastnikBudovy(self, id):
        """

        :type id: str
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)

        ok = model.vlastnikBudovy(id, False)
        if not ok or model.rowCount() == 0:
            return

        budIds = []
        self.tableBudovy(model, budIds, True)
        self.__mCurrentPageBudIds.append(budIds)

    def tableBudovy(self, model, budIds, LVColumn):
        """

        :param model: VfkTableModel
        :param budIds: list
        :param LVColumn: bool
        :return:
        """
        self.__mDocument.heading3(u"Stavby")
        self.__mDocument.beginTable()
        header = [u"Typ stavby", u"Část obce", u"Č. budovy",
                  u"Způsob využití", u"Způsob ochrany", u"Na parcele"]

        if LVColumn:
            header.append(u"LV")

        self.__mDocument.tableHeader(header)

        for i in range(model.rowCount()):
            row = []

            if Domains.anoNe(model.value(i, u"typbud_zadani_cd")) is False:
                row.append(
                    self.__mDocument.link(
                        u"showText?page=bud&id={}".format(
                            model.value(i, u"bud_id")),
                                                 model.value(i, u"typbud_zkratka")))
                row.append(model.value(i, u"casobc_nazev"))
                row.append(u'')
            else:
                row.append(u'')
                row.append(model.value(i, u"casobc_nazev"))
                row.append(
                    self.__mDocument.link(
                        u"showText?page=bud&id={}".format(
                            model.value(i, u"bud_id")),
                                                 u"{} {}".format(model.value(i, u"typbud_zkratka"),
                                                                 model.value(i, u"bud_cislo_domovni"))))
            row.append(model.value(i, u"zpvybu_nazev"))

            budId = model.value(i, u"bud_id")
            ochranaModel = VfkTableModel(self.__mConnectionName)

            ok = ochranaModel.nemovitostOchrana(
                budId, VfkTableModel.Nemovitost.NBudova)
            if not ok:
                break

            ochranaNazev = []
            for j in range(ochranaModel.rowCount()):
                ochranaNazev.append(ochranaModel.value(j, u"zpochn_nazev"))

            row.append(u", ".join(ochranaNazev))
            row.append(self.makeParcelniCislo(model, i))

            if LVColumn:
                row.append(self.makeLVCislo(model, i))

            self.__mDocument.tableRow(row)
            budIds.append(budId)
        self.__mDocument.endTable()

    def partTelesoJednotky(self, id, jedIds):
        """

        :type id: str
        :type jedIds: list
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)

        ok = model.telesoJednotky(id, False)
        if ok is False or model.rowCount() == 0:
            return

        self.tableJednotky(model, jedIds, False)

    def partVlastnikJednotky(self, opsubId):
        """

        :type opsubId: str
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)

        ok = model.vlastnikJednotky(opsubId, False)
        if not ok or model.rowCount() == 0:
            return

        jedIds = []
        self.tableJednotky(model, jedIds, True)

    def tableJednotky(self, model, jedIds, LVColumn):
        """

        :type model: VfkTableModel
        :type jedIds: list
        :type LVColumn: bool
        :return:
        """
        self.__mDocument.heading3(u"Jednotky")
        self.__mDocument.beginTable()
        header = [u"Č.p./Č.jednotky ", u"Způsob využití", u"Způsob ochrany",
                  u"Podíl na společných{}částech domu a pozemku".format(self.__mDocument.newLine())]

        if LVColumn:
            header.append(u"LV")

        self.__mDocument.tableHeader(header)

        for i in range(model.rowCount()):
            row = []

            jedId = model.value(i, u"jed_id")
            row.append(self.makeJednotka(model, i))
            row.append(model.value(i, u"zpvyje_nazev"))
            ochranaModel = VfkTableModel(self.__mConnectionName)

            ok = ochranaModel.nemovitostOchrana(
                jedId, VfkTableModel.Nemovitost.NJednotka)
            if not ok:
                break

            ochranaNazev = []
            for j in range(ochranaModel.rowCount()):
                ochranaNazev.append(ochranaModel.value(j, u"zpochn_nazev"))

            row.append(u", ".join(ochranaNazev))

            podilCit = model.value(i, u"jed_podil_citatel")
            podilJmen = model.value(i, u"jed_podil_jmenovatel")
            podil = u''

            if podilCit and podilJmen and podilJmen != u"1":
                podil += u"{}/{}".format(podilCit, podilJmen)

            row.append(podil)

            if LVColumn:
                row.append(self.makeLVCislo(model, i))

            self.__mDocument.tableRow(row)
            self.partTelesoJednotkaDetail(model.value(i, u"bud_id"))

            jedIds.append(jedId)
        self.__mDocument.endTable()

    def partTelesoJednotkaDetail(self, budId):
        """

        :type budId: str
        :return:
        """
        budInfo = u''
        parInfo = u''

        budModel = VfkTableModel(self.__mConnectionName)
        ok = budModel.budova(budId, False)
        if not ok or budModel.rowCount() == 0:
            return

        budInfo += u"Budova" + u" "
        casobc = budModel.value(0, u"casobc_nazev")
        budInfo += u'' if casobc else casobc + u", "

        budova = u''
        budova += budModel.value(0, u"typbud_zkratka")
        if Domains.anoNe(budModel.value(0, u"typbud_zadani_cd")):
            budova += u" " + budModel.value(0, u"bud_cislo_domovni")
        budInfo += self.__mDocument.link(
            u"showText?page=bud&id={}".format(budId), budova)

        lv = budModel.value(0, u"tel_cislo_tel")
        lvId = budModel.value(0, u"tel_id")
        if lv:
            budInfo += self.__mDocument.link(
                u"showText?page=tel&id={}".format(lvId), u"LV {}".format(lv))

        zpvybu = budModel.value(0, u"zpvybu_nazev")
        budInfo += u", {}".format(zpvybu) if zpvybu else u''

        budInfo + u", na parcele {}".format(
            self.makeParcelniCislo(budModel, 0))

        self.__mDocument.tableRowOneColumnSpan(budInfo)

        parcelaId = budModel.value(0, u"par_id")
        parModel = VfkTableModel(self.__mConnectionName)
        ok = parModel.parcela(parcelaId, False)
        if not ok:
            return

        parInfo += u"Parcela {}".format(self.makeParcelniCislo(parModel, 0))
        lv = parModel.value(0, u"tel_cislo_tel")
        lvId = parModel.value(0, u"tel_id")
        if lv:
            parInfo += self.__mDocument.link(
                u"showText?page=tel&id={}".format(lvId), u"LV {}".format(lv))

        zpvypo = parModel.value(0, u"zpvypo_nazev")
        parInfo += u'' if not zpvypo else u", {}".format(zpvypo)
        parInfo += u", {} m{}".format(
            parModel.value(0, u"par_vymera_parcely"), self.__mDocument.superScript(u"2"))

        self.__mDocument.tableRowOneColumnSpan(parInfo)

    def partTelesoB1(self, parIds, budIds, jedIds, opsubIds, forLV):
        """

        :type parIds: list
        :type budIds: list
        :type jedIds: list
        :type opsubIds: list
        :type forLV: bool
        """

        header = [u"Typ vztahu", u"Oprávnění pro", u"Povinnost k"]

        if forLV:
            self.__mDocument.heading2(u"B1 – Jiná práva")
            self.__mDocument.beginTable()
            self.__mDocument.tableHeader(header)

            if self.partTelesoJinaPrava(parIds, VfkTableModel.OpravnenyPovinny.OPParcela) or \
                    self.partTelesoJinaPrava(budIds, VfkTableModel.OpravnenyPovinny.OPBudova) or \
                    self.partTelesoJinaPrava(jedIds, VfkTableModel.OpravnenyPovinny.OPJednotka) or \
                    self.partTelesoJinaPrava(opsubIds, VfkTableModel.OpravnenyPovinny.OPOsoba):
                self.__mDocument.endTable()
            else:
                self.__mDocument.discardLastBeginTable()
                self.__mDocument.text(self.__mStringBezZapisu)
        else:
            self.__mDocument.heading2(u"Jiná práva")
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

        :type parIds: list
        :type budIds: list
        :type jedIds: list
        :type opsubIds: list
        :type forLV: bool
        """
        header = [u"Typ vztahu", u"Oprávnění pro", u"Povinnost k"]

        if forLV:
            self.__mDocument.heading2(u"C – Omezení vlastnického práva")
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
            self.__mDocument.heading2(u"Omezení vlastnického práva")
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

        :type parIds: list
        :type budIds: list
        :type jedIds: list
        :type opsubIds: list
        :type forLV: bool
        """
        header = [u"Typ vztahu", u"Vztah pro", u"Vztah k"]

        if forLV:
            self.__mDocument.heading2(u"D – Jiné zápisy")
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
            self.__mDocument.heading2(u"Jiné zápisy")
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

        :type parIds: list
        :type budIds: list
        :type jedIds: list
        """
        self.__mDocument.heading2(
            u"E – Nabývací tituly a jiné podklady k zápisu")

        model = VfkTableModel(self.__mConnectionName)
        ok = model.nabyvaciListiny(parIds, budIds, jedIds)
        if not ok:
            return

        if model.rowCount() == 0:
            self.__mDocument.text(self.__mStringBezZapisu)
        else:
            lastListinaId = u''
            self.__mDocument.beginItemize()
            for i in range(model.rowCount()):
                currentListinaId = model.value(i, u"rl_listin_id")
                if currentListinaId == lastListinaId:
                    self.__mDocument.item(
                        self.makeShortDescription(
                            model.value(i, u"rl_opsub_id"),
                                                                    VfkTableModel.OpravnenyPovinny.OPOsoba))
                else:
                    if lastListinaId:
                        self.__mDocument.endItemize()
                        self.__mDocument.endItem()
                    lastListinaId = currentListinaId
                    self.__mDocument.beginItem()
                    self.__mDocument.text(self.makeListina(model, i))
                    self.__mDocument.beginItemize()
                    self.__mDocument.item(
                        self.makeShortDescription(
                            model.value(i, u"rl_opsub_id"),
                                                                    VfkTableModel.OpravnenyPovinny.OPOsoba))

            if lastListinaId:
                self.__mDocument.endItemize()
                self.__mDocument.endItem()

            self.__mDocument.endItemize()

    def partTelesoF(self, parIds, forLV):
        """

        :type parIds: list
        :type forLV: bool
        """
        if forLV:
            self.__mDocument.heading2(
                u"F – Vztah bonitovaných půdně ekologických jednotek (BPEJ) k parcelám")
        else:
            self.__mDocument.heading2(u"BPEJ")

        header = [u"Parcela", u"BPEJ", u"Výměra [m{}]".format(
            self.__mDocument.superScript(u"2"))]
        self.__mDocument.beginTable()
        self.__mDocument.tableHeader(header)

        isRecord = False
        for id in parIds:
            row = []
            model = VfkTableModel(self.__mConnectionName)
            ok = model.parcelaBpej(id)
            if not ok:
                break

            if model.rowCount() == 0:
                continue

            isRecord = True
            row.append(self.makeParcelniCislo(model, 0))
            row.append(model.value(0, u"bdp_bpej_kod"))
            row.append(model.value(0, u"bdp_vymera"))

            self.__mDocument.tableRow(row)

        if isRecord:
            self.__mDocument.endTable()
        else:
            self.__mDocument.discardLastBeginTable()
            self.__mDocument.text(self.__mStringBezZapisu)

    def partNemovitostJinaPrava(self, ids, opravneny):
        """

        :type ids: list
        :type opravneny: VfkTableModel.OpravnenyPovinny
        :return:
        """
        return self.partTelesoB1CDSubjekt(ids, opravneny, VfkTableModel.Pravo.Opravneni, False, False)

    def partTelesoJinaPrava(self, ids, opravneny):
        """

        :type ids: list
        :type opravneny: VfkTableModel.OpravnenyPovinny
        :return:
        """
        return self.partTelesoB1CDSubjekt(ids, opravneny, VfkTableModel.Pravo.Opravneni, False, True)

    def partNemovitostOmezeniPrava(self, ids, povinny):
        """

        :type ids: list
        :type povinny: VfkTableModel.OpravnenyPovinny
        :return:
        """
        return self.partTelesoB1CDSubjekt(ids, povinny, VfkTableModel.Pravo.Povinnost, False, False)

    def partTelesoOmezeniPrava(self, ids, povinny):
        """

        :type ids: list
        :type povinny: VfkTableModel.OpravnenyPovinny
        :return:
        """
        return self.partTelesoB1CDSubjekt(ids, povinny, VfkTableModel.Pravo.Povinnost, False, True)

    def partNemovitostJineZapisy(self, ids, povinny):
        """

        :type ids: list
        :type povinny: VfkTableModel.OpravnenyPovinny
        :return: bool
        """
        test1 = self.partTelesoB1CDSubjekt(
            ids, povinny, VfkTableModel.Pravo.Opravneni, True, False)
        test2 = self.partTelesoB1CDSubjekt(
            ids, povinny, VfkTableModel.Pravo.Povinnost, True, False)
        return test1 or test2

    def partTelesoJineZapisy(self, ids, povinny):
        """

        :type ids: list
        :type povinny: VfkTableModel.OpravnenyPovinny
        :return: bool
        """
        test1 = self.partTelesoB1CDSubjekt(
            ids, povinny, VfkTableModel.Pravo.Opravneni, True, True)
        test2 = self.partTelesoB1CDSubjekt(
            ids, povinny, VfkTableModel.Pravo.Povinnost, True, True)
        return test1 or test2

    def partTelesoB1CDSubjekt(self, ids, pravniSubjekt, pravo, sekceD, showListiny):
        """

        :type ids: list
        :type pravniSubjekt: VfkTableModel.OpravnenyPovinny
        :type pravo: VfkTableModel.Pravo
        :type sekceD: bool
        :type showListiny: bool
        :return: bool
        """
        isRecord = False
        povinni = [u"jpv_par_id_k", u"jpv_bud_id_k",
                   u"jpv_jed_id_k", u"jpv_opsub_id_k"]
        opravneni = [u"jpv_par_id_pro", u"jpv_bud_id_pro",
                     u"jpv_jed_id_pro", u"jpv_opsub_id_pro"]

        for id in ids:
            model = VfkTableModel(self.__mConnectionName)
            where = u"typrav.sekce {}= 'D'".format(u'' if sekceD else u'!')
            ok = model.nemovitostJpv(id, pravniSubjekt, pravo, where)
            if not ok or model.rowCount() == 0:
                continue

            isRecord = True
            for i in range(model.rowCount()):
                row = []
                typPrava = model.value(i, u"typrav_nazev")
                row.append(typPrava)

                opravneniList = []
                for column1 in opravneni:
                    if model.value(i, column1):
                        opravneny = VfkTableModel().tableName2OpravnenyPovinny(
                            column1)
                        opravnenyId = model.value(i, column1)
                        opravneniList.append(
                            self.makeShortDescription(opravnenyId, opravneny))

                row.append(str(self.__mDocument.newLine()).join(opravneniList))

                povinniList = []
                for column2 in povinni:
                    if model.value(i, column2):
                        povinny = VfkTableModel().tableName2OpravnenyPovinny(
                            column2)
                        povinnyId = model.value(i, column2)
                        povinniList.append(
                            self.makeShortDescription(povinnyId, povinny))

                row.append(str(self.__mDocument.newLine()).join(povinniList))

                self.__mDocument.tableRow(row)

                if showListiny:
                    self.partTelesoListiny(model.value(i, u"jpv_id"))

        return isRecord

    def partTelesoListiny(self, jpvId):
        """

        :type jpvId: str
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)
        ok = model.jpvListiny(jpvId)
        if not ok:
            return

        for i in range(model.rowCount()):
            self.__mDocument.tableRowOneColumnSpan(self.makeListina(model, i))

    def pageParcela(self, id):
        """

        :type id: str
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)
        ok = model.parcela(id, True)
        if not ok:
            return

        self.__mCurrentPageParIds.append(id)
        self.saveDefinitionPoint(id, VfkTableModel.Nemovitost.NParcela)

        content = [TPair(u"Parcelní číslo:", self.makeParcelniCislo(model, 0))]

        telesoModel = VfkTableModel(self.__mConnectionName)
        telesoModel.nemovitostTeleso(id, VfkTableModel.Nemovitost.NParcela)
        content.append(
            TPair(u"List vlastnictví:", self.makeLVCislo(telesoModel, 0)))
        content.append(
            TPair(u"Výměra [m{}]:".format(self.__mDocument.superScript(u"2")),
                  model.value(0, u"par_vymera_parcely")))
        content.append(
            TPair(u"Určení výměry:", model.value(0, u"zpurvy_nazev")))

        if model.value(0, u"par_cena_nemovitosti"):
            content.append(
                TPair(u"Cena nemovitosti:", model.value(0, u"par_cena_nemovitosti")))

        content.append(TPair(u"Typ parcely:", model.value(0, u"par_par_type")))
        content.append(
            TPair(u"Mapový list:", model.value(0, u"maplis_oznaceni_mapoveho_listu")))
        content.append(
            TPair(u"Katastrální území:", self.makeKatastrUzemi(model, 0)))
        content.append(
            TPair(u"Druh pozemku:", model.value(0, u"drupoz_nazev")))

        if model.value(0, u"zpvypo_nazev"):
            content.append(
                TPair(u"Způsob využití pozemku:", model.value(0, u"zpvypo_nazev")))

        if Domains.anoNe(model.value(0, u"drupoz_stavebni_parcela")):
            content.append(
                TPair(u"Stavba na parcele:", self.makeDomovniCislo(model, 0)))
            self.__mCurrentPageBudIds.append(model.value(0, u"bud_id"))

        self.__mDocument.heading1(u"Informace o parcele")
        self.__mDocument.keyValueTable(content)

        # neighbours
        sousedniModel = VfkTableModel(self.__mConnectionName)
        sousedniModel.sousedniParcely(id)
        ids = []
        for i in range(0, sousedniModel.rowCount()):
            ids.append(sousedniModel.value(i, u"hp_par_id_1"))
            ids.append(sousedniModel.value(i, u"hp_par_id_2"))

        ids = list(set(ids))
        ids.remove(id)

        link = self.__mDocument.link(
            u"showText?page=seznam&type=id&parcely={}".format(u",".join(ids)),
                                     u"Sousední parcely")

        self.__mDocument.paragraph(link)
        opsubIds = []
        # self.partTelesoVlastnici(
        #     telesoModel.value(0, u"tel_id"), opsubIds, False)
        self.partNemovitostOchrana(id, VfkTableModel.Nemovitost.NParcela)

        parIds = [id]
        tempList = []
        self.partTelesoB1(parIds, tempList, tempList, tempList, False)
        self.partTelesoC(parIds, tempList, tempList, tempList, False)
        self.partTelesoD(parIds, tempList, tempList, tempList, False)
        self.partTelesoF(parIds, False)

    def partTelesoVlastnici(self, id, opsubIds, forLV):
        """

        :type id: str
        :type opsubIds: list
        :type forLV: bool
        :return:
        """
        # vlastniciModel = VfkTableModel(self.__mConnectionName)
        # ok = vlastniciModel.telesoVlastnici(id)
        # if not ok:
            # return
        if forLV:
            self.__mDocument.heading2(u"A – Vlastníci, jiní oprávnění")
        else:
            self.__mDocument.heading2(u"Vlastníci, jiní oprávnění")
        
        self.mDocument.text(u"Informace o vlastníkovi není dostupná.")
    #     orderedPrava = []
    #     for i in range(vlastniciModel.rowCount()):
    #         orderedPrava.append(vlastniciModel.value(i, u"typrav_nazev"))

    #     orderedPrava = list(set(orderedPrava))

    #     # tables =  {[[]]}
    #     tables = {}
    #     header = [u"Jméno", u"Adresa", u"Identifikátor", u"Podíl"]

    #     for i, item in enumerate(orderedPrava):
    #         table = [header]
    #         tables[orderedPrava[i]] = table

    #     for i in range(vlastniciModel.rowCount()):
    #         typravNazev = vlastniciModel.value(i, u"typrav_nazev")
    #         opsubId = vlastniciModel.value(i, u"vla_opsub_id")
    #         vlaPodilCitatel = vlastniciModel.value(i, u"vla_podil_citatel")
    #         vlaPodilJmenovatel = vlastniciModel.value(
    #             i, u"vla_podil_jmenovatel")
    #         podil = u''

    #         if vlaPodilCitatel and vlaPodilJmenovatel and vlaPodilJmenovatel != u'1':
    #             podil += u"{}/{}".format(vlaPodilCitatel, vlaPodilJmenovatel)

    #         vlastnikModel = VfkTableModel(self.__mConnectionName)
    #         ok = vlastnikModel.vlastnik(opsubId, True)
    #         if not ok:
    #             return

    #         opsub_type = vlastnikModel.value(0, u"opsub_opsub_type")
    #         nazev = self.makeJmeno(vlastnikModel, 0)

    #         if opsub_type != u"BSM":
    #             content = []
    #             adresa = self.makeAdresa(vlastnikModel, 0)
    #             identifikator = self.makeIdentifikator(vlastnikModel, 0)
    #             content.append(nazev)
    #             content.append(adresa)
    #             content.append(identifikator)
    #             content.append(podil)
    #             tables[typravNazev].append(content)
    #         else:
    #             nazev += u" ({})".format(
    #                 vlastnikModel.value(0, u"charos_zkratka"))
    #             rowContent = [nazev, u'', u'', podil]
    #             tables[typravNazev].append(rowContent)

    #             manzeleId = [vlastnikModel.value(
    #                 0, u"opsub_id_je_1_partner_bsm"),
    #                 vlastnikModel.value(0, u"opsub_id_je_2_partner_bsm")]

    #             sjmModel = VfkTableModel(self.__mConnectionName)
    #             for j in range(len(manzeleId)):
    #                 ok = sjmModel.vlastnik(manzeleId[j])
    #                 if not ok:
    #                     break

    #                 identifikatorSJM = sjmModel.value(0, u"opsub_rodne_cislo")
    #                 rowContent = [self.makeJmeno(sjmModel, 0), self.makeAdresa(
    #                     sjmModel, 0), identifikatorSJM, u'']
    #                 tables[typravNazev].append(rowContent)

    #         opsubIds.append(opsubId)
    #     for i in range(len(orderedPrava)):
    #         self.__mDocument.heading3(orderedPrava[i])
    #         self.__mDocument.table(tables[orderedPrava[i]], True)

    def partNemovitostOchrana(self, id, nemovitost):
        """

        :type id: str
        :type nemovitost: VfkTableModel.Nemovitost
        :return:
        """
        ochrana = VfkTableModel(self.__mConnectionName)
        ok = ochrana.nemovitostOchrana(id, nemovitost)
        if not ok:
            return

        self.__mDocument.heading2(u"Způsob ochrany nemovitosti")

        if ochrana.rowCount() == 0:
            self.__mDocument.text(u"Není evidován žádný způsob ochrany.")
        else:
            self.__mDocument.beginTable()
            header = [u"Název"]

            for i in range(ochrana.rowCount()):
                content = [ochrana.value(i, u"zpochn_nazev")]
                self.__mDocument.tableRow(content)

            self.__mDocument.endTable()

    def pageBudova(self, id):
        """

        :type id: str
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)
        ok = model.budova(id, True)
        if not ok:
            return

        self.__mCurrentPageBudIds.append(id)
        self.saveDefinitionPoint(id, VfkTableModel.Nemovitost.NBudova)

        content = []

        if Domains.anoNe(model.value(0, u"typbud_zadani_cd")):
            content.append(TPair(u"Stavba:", self.makeDomovniCislo(model, 0)))
            content.append(TPair(u"Část obce:", self.makeCastObce(model, 0)))

        content.append(TPair(u"Na parcele:", self.makeParcelniCislo(model, 0)))
        self.__mCurrentPageParIds.append(model.value(0, u"par_id"))

        telesoModel = VfkTableModel(self.__mConnectionName)
        telesoModel.nemovitostTeleso(id, VfkTableModel.Nemovitost.NBudova)
        content.append(
            TPair(u"List vlastnictví:", self.makeLVCislo(telesoModel, 0)))

        cena = model.value(0, u"bud_cena_nemovitosti")
        if cena:
            content.append(TPair(u"Cena nemovitosti:", cena))
        content.append(TPair(u"Typ stavby:", model.value(0, u"typbud_nazev")))
        content.append(
            TPair(u"Způsob využití:", model.value(0, u"zpvybu_nazev")))

        jednotkyModel = VfkTableModel(self.__mConnectionName)
        jednotkyModel.budovaJednotky(id)
        if jednotkyModel.rowCount() > 0:
            jednotky = []
            for i in range(jednotkyModel.rowCount()):
                jednotky.append(self.makeJednotka(jednotkyModel, i))

            content.append(TPair(u"Jednotky v budově:", u", ".join(jednotky)))

        content.append(
            TPair(u"Katastrální území:", self.makeKatastrUzemi(model, 0)))

        self.__mDocument.heading1(u"Informace o stavbě")
        self.__mDocument.keyValueTable(content)

        opsubIds = []
        # self.partTelesoVlastnici(
        #     telesoModel.value(0, u"tel_id"), opsubIds, False)
        self.partNemovitostOchrana(id, VfkTableModel.Nemovitost.NBudova)

        budIds = [id]
        self.partTelesoB1([], budIds, [], [], False)
        self.partTelesoC([], budIds, [], [], False)
        self.partTelesoD([], budIds, [], [], False)

    def pageJednotka(self, id):
        """

        :type id: str
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)
        ok = model.jednotka(id, True)
        if not ok:
            return

        content = [TPair(u"Číslo jednotky:", self.makeJednotka(model, 0)),
                   TPair(u"V budově:", self.makeDomovniCislo(model, 0)),
                   TPair(u"Na parcele:", self.makeParcelniCislo(model, 0))]

        self.__mCurrentPageParIds.append(model.value(0, u"par_id"))
        self.__mCurrentPageBudIds.append(model.value(0, u"bud_id"))

        telesoModel = VfkTableModel(self.__mConnectionName)
        telesoModel.nemovitostTeleso(id, VfkTableModel.Nemovitost.NJednotka)
        content.append(
            TPair(u"List vlastnictví:", self.makeLVCislo(telesoModel, 0)))

        cena = model.value(0, u"jed_cena_nemovitosti")
        if cena:
            content.append(TPair(u"Cena nemovitosti:", cena))

        content.append(
            TPair(u"Typ jednotky:", model.value(0, u"typjed_nazev")))
        content.append(
            TPair(u"Způsob využití:", model.value(0, u"zpvyje_nazev")))
        content.append(TPair(u"Podíl jednotky na společných částech domu:", u"{}/{}"
                             .format(model.value(0, u"jed_podil_citatel"), model.value(0, u"jed_podil_jmenovatel"))))
        content.append(
            TPair(u"Katastrální území:", self.makeKatastrUzemi(model, 0)))

        self.__mDocument.heading1(u"Informace o jednotce")
        self.__mDocument.keyValueTable(content)

        opsubIds = []
        # self.partTelesoVlastnici(
        #     telesoModel.value(0, u"tel_id"), opsubIds, False)
        self.partNemovitostOchrana(id, VfkTableModel.Nemovitost.NJednotka)

        jedIds = [id]
        self.partTelesoB1([], [], jedIds, [], False)
        self.partTelesoC([], [], jedIds, [], False)
        self.partTelesoD([], [], jedIds, [], False)

    def pageOpravnenySubjekt(self, id):
        """

        :type id: str
        :return:
        """
        opsubModel = VfkTableModel(self.__mConnectionName)
        ok = opsubModel.opravnenySubjekt(id, True)
        if not ok:
            return

        content = []
        name = self.makeJmeno(opsubModel, 0)

        if opsubModel.value(0, u"opsub_opsub_type") == u"OPO":
            content.append(TPair(u"Název:", name))
            content.append(TPair(u"Adresa:", self.makeAdresa(opsubModel, 0)))
            content.append(
                TPair(u"IČO:", self.makeIdentifikator(opsubModel, 0)))
        elif opsubModel.value(0, u"opsub_opsub_type") == u"OFO":
            content.append(TPair(u"Jméno:", name))
            content.append(TPair(u"Adresa:", self.makeAdresa(opsubModel, 0)))
            content.append(
                TPair(u"Rodné číslo:", self.makeIdentifikator(opsubModel, 0)))
        else:
            content.append(TPair(u"Jméno:", name))

            for i in range(1, 3):
                manzelId = opsubModel.value(
                    0, u"opsub_id_je_{}_partner_bsm".format(i))
                desc = self.makeShortDescription(
                    manzelId, VfkTableModel.OpravnenyPovinny.OPOsoba)
                content.append(TPair(u'', desc))

        content.append(TPair(u"Typ:", opsubModel.value(0, u"charos_nazev")))

        nemovitostiModel = VfkTableModel(self.__mConnectionName)
        nemovitostiModel.vlastnikNemovitosti(id)

        telesaDesc = []
        nemovitostDesc = []
        idColumns = [u"par_id", u"bud_id", u"jed_id"]

        for i in range(nemovitostiModel.rowCount()):
            telesaDesc.append(self.makeLVCislo(nemovitostiModel, i))

            for column in idColumns:
                nemovitostDesc.append(
                    self.makeLongDescription(nemovitostiModel.value(i, column),
                                             VfkTableModel().tableName2OpravnenyPovinny(column)))

        telesaDesc = list(set(telesaDesc))
        if telesaDesc:
            content.append(
                TPair(u"Listy vlastnictví:", u", ".join(telesaDesc)))
        self.__mDocument.heading1(u"Informace o oprávněné osobě")
        self.__mDocument.keyValueTable(content)

        self.partVlastnikNemovitosti(id)

        opsubIds = [id]
        self.partTelesoB1([], [], [], opsubIds, False)
        self.partTelesoC([], [], [], opsubIds, False)
        self.partTelesoD([], [], [], opsubIds, False)

    def pageSeznamParcel(self, ids):
        """

        :type ids: list
        """
        self.__mDocument.heading2(u"Seznam parcel")
        self.__mDocument.beginItemize()

        self.__mCurrentPageParIds = ids

        for id in ids:
            model = VfkTableModel(self.__mConnectionName)
            ok = model.parcela(id, False)
            if not ok:
                continue

            self.__mDocument.item(self.makeLongDescription(
                id, VfkTableModel.OpravnenyPovinny.OPParcela))

        self.__mDocument.endItemize()

    def pageSeznamOsob(self, ids):
        """

        :type ids: list
        """
        self.__mDocument.heading2(u"Seznam osob")
        self.__mDocument.text(u"Seznam osob není v tuto chvíli dostupný.")
        # self.__mDocument.beginItemize()

        # self.__mCurrentPageParIds = ids

        # for id in ids:
        #     model = VfkTableModel(self.__mConnectionName)
        #     ok = model.opravnenySubjekt(id, True)
        #     if not ok:
        #         continue

        #     self.__mDocument.item(self.makeLongDescription(
        #         id, VfkTableModel.OpravnenyPovinny.OPOsoba))

        # self.__mDocument.endItemize()

    def pageSeznamBudov(self, ids):
        """

        :type ids: list
        """
        self.__mDocument.heading2(u"Seznam budov")
        self.__mDocument.beginItemize()
        self.__mCurrentPageBudIds = ids

        for id in ids:
            self.__mDocument.item(self.makeLongDescription(
                id, VfkTableModel.OpravnenyPovinny.OPBudova))

        self.__mDocument.endItemize()

    def pageSeznamJednotek(self, ids):
        """

        :type ids: list
        """
        self.__mDocument.heading2(u"Seznam jednotek")
        self.__mDocument.beginItemize()
        self.__mCurrentPageBudIds = ids

        for id in ids:
            self.__mDocument.item(self.makeLongDescription(
                id, VfkTableModel.OpravnenyPovinny.OPJednotka))

        self.__mDocument.endItemize()

    def pageSearchVlastnici(self, jmeno, identifikator, sjm, opo, ofo, lv):
        """

        :type jmeno: str
        :type identifikator: str
        :type sjm: bool
        :type opo: bool
        :type ofo: bool
        :type lv: bool
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)
        ok = model.searchOpsub(jmeno, identifikator, sjm, opo, ofo, lv)
        if not ok:
            return

        ids = []
        for i in range(model.rowCount()):
            ids.append(model.value(i, u'opsub_id'))

        self.pageSeznamOsob(ids)

    def pageSearchParcely(self, parcelniCislo, typIndex, druhKod, lv):
        """

        :type parcelniCislo: str
        :type typIndex: str
        :type druhKod: str
        :type lv: str
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)
        ok = model.searchPar(parcelniCislo, typIndex, druhKod, lv)
        if not ok:
            return

        ids = []
        for i in range(model.rowCount()):
            ids.append(model.value(i, u"par_id"))

        self.pageSeznamParcel(ids)

    def pageSearchBudovy(self, domovniCislo, naParcele, zpusobVyuziti, lv):
        """

        :type domovniCislo: str
        :type naParcele: str
        :type zpusobVyuziti: str
        :type lv: str
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)
        ok = model.searchBud(domovniCislo, naParcele, zpusobVyuziti, lv)
        if not ok:
            return

        ids = []
        for i in range(model.rowCount()):
            ids.append(model.value(i, u"bud_id"))

        self.pageSeznamBudov(ids)

    def pageSearchJednotky(self, cisloJednotky, domovniCislo, naParcele, zpusobVyuziti, lv):
        """

        :type cisloJednotky: str
        :type domovniCislo: str
        :type naParcele: str
        :type zpusobVyuziti: str
        :type lv: str
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)
        ok = model.searchJed(
            cisloJednotky, domovniCislo, naParcele, zpusobVyuziti, lv)
        if not ok:
            iface.messageBar().pushWarning(u'ERROR',
                u"Nemohu najit dane jednotky, nekde se stala nejaka chyba"
            )
            return

        ids = []
        for i in range(model.rowCount()):
            ids.append(model.value(i, u"jed_id"))

        self.pageSeznamJednotek(ids)

    def pageHelp(self):
        self.__mDocument.heading1(u"VFK plugin")
        self.__mDocument.paragraph(
            u"VFK plugin slouží pro usnadnění práce s českými katastrálními daty ve formátu VFK.")
        self.__mDocument.heading2(u"Kde začít?")

        link = self.__mDocument.link(
            u"switchPanel?panel=import", u"Importujte")
        text = u"{} data ve formátu VFK, nebo již připravenou databázi SQLite s daty katastru nemovitostí. " \
               u"Během importu se vytváří databáze, tato operace může chvíli trvat. ".format(
            link)
        text += u"Následně lze vyhledávat:"
        self.__mDocument.paragraph(text)

        self.__mDocument.beginItemize()      
        link = self.__mDocument.link(
            u"switchPanel?panel=search&type=0", u"oprávněné osoby")
        text = u"{} (tato možnost je momentálně nedostupná)".format(link)
        self.__mDocument.item(text)
        link = self.__mDocument.link(
            u"switchPanel?panel=search&type=1", u"parcely")
        self.__mDocument.item(link)
        link = self.__mDocument.link(
            u"switchPanel?panel=search&type=2", u"budovy")
        self.__mDocument.item(link)
        link = self.__mDocument.link(
            u"switchPanel?panel=search&type=3", u"jednotky")
        self.__mDocument.item(link)
        self.__mDocument.endItemize()

        text = u"Vyhledávat lze na základě různých kritérií. " \
            u"Není-li kritérium zadáno, vyhledány jsou všechny nemovitosti či osoby obsažené v databázi. " \
            u"Výsledky hledání jsou pak vždy zobrazeny v tomto okně."
        self.__mDocument.paragraph(text)

        text = u"Výsledky hledání obsahují odkazy na další informace, " \
            u"kliknutím na odkaz si tyto informace zobrazíte, " \
            u"stejně jako je tomu u webového prohlížeče. " \
            u"Pro procházení historie použijte tlačítka Zpět a Vpřed v panelu nástrojů nad tímto oknem."
        self.__mDocument.paragraph(text)

        self.__mDocument.heading2(u"Aplikace změn")

        link = self.__mDocument.link(
            u"switchPanel?panel=changes", u"aplikaci změn")

        text = u"Změny je možné aplikovat v panelu pro {}. Pro aplikování změn na stavová data je potřeba zadat " \
               u"cestu k databázi se stavovými daty, k databázi se změnovými daty a nakonec cestu/jméno " \
               u"pro výstupní databázi.".format(link)
        self.__mDocument.paragraph(text)

    def makeShortDescription(self, id, nemovitost):
        """

        :type id: str
        :type nemovitost: VfkTableModel.OpravnenyPovinny
        :return: str
        """
        text = u''
        if not id:
            return text

        model = VfkTableModel(self.__mConnectionName)
        if nemovitost == VfkTableModel.OpravnenyPovinny.OPParcela:
            model.parcela(id, False)
            text = u"Parcela: "
            text += self.makeParcelniCislo(model, 0)
        elif nemovitost == VfkTableModel.OpravnenyPovinny.OPBudova:
            model.budova(id, False)
            text = u"Budova: {}".format(self.makeDomovniCislo(model, 0))
        elif nemovitost == VfkTableModel.OpravnenyPovinny.OPJednotka:
            model.jednotka(id, False)
            text = u"Jednotka: {}".format(self.makeJednotka(model, 0))
        elif nemovitost == VfkTableModel.OpravnenyPovinny.OPOsoba:
            model.opravnenySubjekt(id, True)
            if model.value(0, u"opsub_opsub_type") == u"BSM":
                text = u"{}".format(self.makeJmeno(model, 0))
            else:
                text = u"{}, {}, RČ/IČO: {}".format(self.makeJmeno(model, 0), self.makeAdresa(model, 0),
                                                    self.makeIdentifikator(model, 0))
        else:
            pass

        return text

    def makeLongDescription(self, id, nemovitost):
        """

        :type id: str
        :type nemovitost: VfkTableModel.OpravnenyPovinny
        :return: str
        """
        text = u''
        if not id:
            return text

        model = VfkTableModel(self.__mConnectionName)

        if nemovitost == VfkTableModel.OpravnenyPovinny.OPParcela:
            model.parcela(id, False)
            text = u"Parcela "
            text += self.makeParcelniCislo(model, 0)
            text += u", LV {}".format(self.makeLVCislo(model, 0))
        elif nemovitost == VfkTableModel.OpravnenyPovinny.OPBudova:
            model.budova(id, False)
            text = u"Budova: {}".format(self.makeDomovniCislo(model, 0))
            text += u" na parcele {}".format(self.makeParcelniCislo(model, 0))
            text += u", LV {}".format(self.makeLVCislo(model, 0))
        elif nemovitost == VfkTableModel.OpravnenyPovinny.OPJednotka:
            model.jednotka(id, True)
            text = u"Jednotka: ".format(self.makeJednotka(model, 0))
            text += u" v budově  {}".format(self.makeDomovniCislo(model, 0))
            text += u" na parcele {}".format(self.makeParcelniCislo(model, 0))
            text += u", LV {}".format(self.makeLVCislo(model, 0))
        elif nemovitost == VfkTableModel.OpravnenyPovinny.OPOsoba:
            text += self.makeShortDescription(id, nemovitost)
        else:
            pass

        return text

    def makeAdresa(self, model, row):
        """

        :type model: VfkTableModel
        :type row: int
        :return: str
        """
        cislo_domovni = model.value(row, u"opsub_cislo_domovni")
        cislo_orientacni = model.value(row, u"opsub_cislo_orientacni")
        ulice = model.value(row, u"opsub_nazev_ulice")
        cast_obce = model.value(row, u"opsub_cast_obce")
        obec = model.value(row, u"opsub_obec")
        mestska_cast = model.value(row, u"opsub_mestska_cast")
        psc = model.value(row, u"opsub_psc")

        cislo = cislo_domovni
        if cislo_orientacni:
            cislo += u"/" + cislo_orientacni

        adresa = []
        if not ulice:
            adresa.append(obec)
            if cislo:
                adresa.append(cislo)
            if cast_obce:
                adresa.append(cast_obce)
        else:
            adresa.append(ulice)
            if cislo:
                adresa.append(cislo)
            if not cast_obce:
                if mestska_cast:
                    adresa.append(mestska_cast)
                else:
                    adresa.append(cast_obce)
            adresa.append(obec)

        if psc:
            adresa.append(psc)
        return u", ".join(adresa)

    def makeJmeno(self, model, row):
        """

        :type model: VfkTableModel
        :type row: int
        :return: str
        """
        jmeno = u''
        if model.value(row, u"opsub_opsub_type") == u"OFO":
            jmeno += model.value(row, u"opsub_titul_pred_jmenem") + u" "
            jmeno += model.value(row, u"opsub_prijmeni") + u" "
            jmeno += model.value(row, u"opsub_jmeno") + u" "
            jmeno += model.value(row, u"opsub_titul_za_jmenem")
        else:
            jmeno += model.value(row, u"opsub_nazev")

        return self.__mDocument.link(u"showText?page=opsub&id={}".format(model.value(row, u"opsub_id")), jmeno)

    def makeIdentifikator(self, model, row):
        """

        :type model: VfkTableModel
        :type row: int
        :return: str
        """
        type = model.value(row, u"opsub_opsub_type")
        identifikator = u''
        if type == u"OPO":
            identifikator = model.value(row, u"opsub_ico")
        elif type == u"OFO":
            identifikator = model.value(row, u"opsub_rodne_cislo")

        return identifikator

    def makeParcelniCislo(self, model, row):
        """

        :param model: VfkTableModel
        :param row: int
        :return: str
        """
        cislo = u''
        cislo += model.value(row, u"par_kmenove_cislo_par")
        poddeleni = model.value(row, u"par_poddeleni_cisla_par")
        if poddeleni:
            cislo += u"/" + poddeleni

        st = u''
        if not model.value(row, u"drupoz_stavebni_parcela"):
            iface.messageBar().pushWarning(u'ERROR',
                "Neni k dispozici tabulka drupoz_stavebni_parcela"
            )
        if self.__mDveRadyCislovani and Domains.anoNe(model.value(row, u"drupoz_stavebni_parcela")):
            st = u"st."

        link = self.__mDocument.link(
            u"showText?page=par&id={}".format(model.value(row, u"par_id")), cislo)
        return u"{} {}".format(st, link)

    def makeDomovniCislo(self, model, row):
        """

        :type model: VfkTableModel
        :type row: int
        :return: str
        """
        return self.__mDocument.link(
            u"showText?page=bud&id={}".format(model.value(row, u"bud_id")),
                                     u"{} {}".format(model.value(row, u"typbud_zkratka"),
                                                     model.value(row, u"bud_cislo_domovni")))

    def makeJednotka(self, model, row):
        """

        :type model: VfkTableModel
        :type row: int
        :return: str
        """
        return self.__mDocument.link(
            u"showText?page=jed&id={}".format(model.value(row, u"jed_id")),
                                     u"{}/{}".format(model.value(row, u"bud_cislo_domovni"),
                                                     model.value(row, u"jed_cislo_jednotky")))

    def makeListina(self, model, row):
        """

        :type model: VfkTableModel
        :type row: int
        :return: str
        """
        return u"Listina: {} {}".format(model.value(row, u"typlis_nazev"), model.value(row, u"dul_nazev"))

    def makeLVCislo(self, model, row):
        """

        :type model: VfkTableModel
        :type row: int
        :return: str
        """
        return self.__mDocument.link(
            u"showText?page=tel&id={}".format(model.value(row, u"tel_id")),
                                     model.value(row, u"tel_cislo_tel"))

    def makeKatastrUzemi(self, model, row):
        """

        :type model: VfkTableModel
        :type row: int
        :return: str
        """
        return u"{} {}".format(model.value(row, u"katuze_nazev"), model.value(row, u"par_katuze_kod"))

    def makeCastObce(self, model, row):
        """

        :type model: VfkTableModel
        :type row: int
        :return: str
        """
        return u"{} {}".format(model.value(row, u"casobc_nazev"), model.value(row, u"casobc_kod"))

    def makeObec(self, model, row):
        """

        :param model: VfkTableModel
        :param row: int
        :return: str
        """
        return u"{} {}".format(model.value(row, u"obce_nazev"), model.value(row, u"obce_kod"))

    def saveDefinitionPoint(self, id, nemovitost):
        """

        :param id: str
        :param nemovitost: VfkTableModel.Nemovitost
        """
        model = VfkTableModel(self.__mConnectionName)
        ok = model.definicniBod(id, nemovitost)
        if not ok:
            return
        self.__mCurrentDefinitionPoint.first = model.value(
            0, u"obdebo_souradnice_x")
        self.__mCurrentDefinitionPoint.second = model.value(
            0, u"obdebo_souradnice_y")
