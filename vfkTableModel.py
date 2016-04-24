# -*- coding: utf-8 -*-
"""
/***************************************************************************
 vfkPluginDialog
                                 A QGIS plugin
 Plugin umoznujici praci s daty katastru nemovitosti
                             -------------------
        begin                : 2015-06-11
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Stepan Bambula
        email                : stepan.bambula@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtSql import QSqlQueryModel, QSqlRecord, QSqlField, QSqlDatabase
from PyQt4.QtCore import qDebug, QTime, QObject


class VfkTableModel(QSqlQueryModel):

    class Nemovitost:
        NParcela = 0
        NBudova = 1
        NJednotka = 2

    class OpravnenyPovinny:
        OPParcela = 0
        OPBudova = 1
        OPJednotka = 2
        OPOsoba = 3

    class Pravo:
        Opravneni = 0
        Povinnost = 1

    def __init__(self, connectionName='', parent=None):
        """

        :type connectionName:str
        :type parent: QObject
        :return:
        """
        QSqlQueryModel.__init__(self, parent)

        self.__mConnectionName = connectionName

    def telesa(self):
        """

        :return: bool
        """
        query = "SELECT tel.id tel_id, " \
            "tel.katuze_kod tel_katuze_kod, " \
            "tel.cislo_tel tel_cislo_tel " \
            "FROM tel;"

        return self.__evaluate(query)

    def telesoHlavicka(self, id):
        """

        :type id: str
        :return:
        """
        query = "SELECT tel.id tel_id, tel.cislo_tel tel_cislo_tel, " \
            "katuze.kod katuze_kod, katuze.nazev katuze_nazev, " \
            "obce.kod obce_kod, obce.nazev obce_nazev, " \
            "okresy.nuts4 okresy_nuts4, okresy.nazev okresy_nazev " \
            "FROM tel " \
            "JOIN katuze ON tel.katuze_kod = katuze.kod " \
            "JOIN obce ON katuze.obce_kod = obce.kod " \
            "JOIN okresy ON obce.okresy_kod = okresy.kod " \
            "WHERE tel.id = {};".format(id)
        return self.__evaluate(query)

    def telesoParcely(self, cisloTel, extended):
        """

        :type cisloTel: str
        :type extended: bool
        :return:
        """
        columns = ", ".join(self.parColumns(extended))
        query = "SELECT {} " \
                "FROM tel " \
                "JOIN par ON par.tel_id = tel.id " \
                "LEFT JOIN drupoz ON par.drupoz_kod = drupoz.kod " \
                "LEFT JOIN zpvypo ON par.zpvypa_kod = zpvypo.kod " \
                "WHERE tel.id = {};".format(columns, cisloTel)
        return self.__evaluate(query)

    def vlastnikParcely(self, opsubId, extended):
        """

        :type opsubId: str
        :type extended: bool
        :return:
        """
        columns = ", ".join(self.parColumns(extended))
        query = "SELECT {} " \
                "FROM tel " \
                "JOIN vla ON vla.tel_id = tel.id " \
                "JOIN opsub ON vla.opsub_id = opsub.id " \
                "JOIN par ON par.tel_id = tel.id " \
                "LEFT JOIN drupoz ON par.drupoz_kod = drupoz.kod " \
                "LEFT JOIN zpvypo ON par.zpvypa_kod = zpvypo.kod " \
                "WHERE opsub.id = {};".format(columns, opsubId)
        return self.__evaluate(query)

    def telesoBudovy(self, cisloTel, extended):
        """

        :type cisloTel: str
        :type extended: bool
        :return:
        """
        columns = ", ".join(self.budColumns(extended))
        query = "SELECT {} " \
                "FROM tel " \
                "JOIN bud ON bud.tel_id = tel.id " \
                "JOIN typbud ON typbud.kod = bud.typbud_kod " \
                "JOIN par ON par.bud_id = bud.id " \
                "LEFT JOIN zpvybu ON zpvybu.kod = bud.zpvybu_kod " \
                "LEFT JOIN casobc ON casobc.kod = bud.caobce_kod " \
                "LEFT JOIN drupoz ON drupoz.kod = par.drupoz_kod " \
                "WHERE tel.id = {};".format(columns, cisloTel)
        return self.__evaluate(query)

    def vlastnikBudovy(self, opsubId, extended):
        """

        :type opsubId: str
        :type extended: bool
        :return:
        """
        columns = ", ".join(self.budColumns(extended))
        query = "SELECT {} " \
                "FROM tel " \
                "JOIN vla ON vla.tel_id = tel.id " \
                "JOIN opsub ON vla.opsub_id = opsub.id " \
                "JOIN bud ON bud.tel_id = tel.id " \
                "JOIN typbud ON typbud.kod = bud.typbud_kod " \
                "JOIN par ON par.bud_id = bud.id " \
                "LEFT JOIN zpvybu ON zpvybu.kod = bud.zpvybu_kod " \
                "LEFT JOIN casobc ON casobc.kod = bud.caobce_kod " \
                "LEFT JOIN drupoz ON drupoz.kod = par.drupoz_kod " \
                "WHERE opsub.id = {};".format(columns, opsubId)
        return self.__evaluate(query)

    def telesoJednotky(self, cisloTel, extended):
        """

        :type cisloTel: str
        :type extended: bool
        :return:
        """
        columns = ", ".join(self.jedColumns(extended))
        query = "SELECT {} " \
                "FROM jed " \
                "JOIN tel ON tel.id = jed.tel_id " \
                "JOIN bud ON jed.bud_id = bud.id " \
                "JOIN typjed ON typjed.kod = jed.typjed_kod " \
                "LEFT JOIN zpvyje ON zpvyje.kod = jed.zpvyje_kod " \
                "JOIN par ON par.bud_id = bud.id " \
                "LEFT JOIN drupoz ON drupoz.kod = par.drupoz_kod " \
                "WHERE tel.id = {};".format(columns, cisloTel)

        return self.__evaluate(query)

    def vlastnikJednotky(self, opsubId, extended):
        """

        :type opsubId: str
        :type extended: bool
        :return:
        """
        columns = ", ".join(self.jedColumns(extended))
        query = "SELECT {} " \
            "FROM jed " \
            "JOIN tel ON tel.id = jed.tel_id " \
            "JOIN vla ON vla.tel_id = tel.id " \
            "JOIN opsub ON vla.opsub_id = opsub.id " \
            "JOIN bud ON jed.bud_id = bud.id " \
            "JOIN typjed ON typjed.kod = jed.typjed_kod " \
            "LEFT JOIN zpvyje ON zpvyje.kod = jed.zpvyje_kod " \
            "JOIN par ON par.bud_id = bud.id " \
            "LEFT JOIN drupoz ON drupoz.kod = par.drupoz_kod " \
            "WHERE opsub.id = {};".format(columns, opsubId)

        return self.__evaluate(query)

    def parcela(self, id, extended):
        """

        :type id: str
        :type extended: bool
        :return:
        """
        columns = ", ".join(self.parColumns(extended))
        query = "SELECT DISTINCT {} " \
                "FROM par " \
                "LEFT JOIN tel ON par.tel_id = tel.id " \
                "LEFT JOIN zpurvy ON par.zpurvy_kod = zpurvy.kod " \
                "LEFT JOIN drupoz ON par.drupoz_kod = drupoz.kod " \
                "LEFT JOIN zpvypo ON par.zpvypa_kod = zpvypo.kod " \
                "LEFT JOIN maplis ON par.maplis_kod = maplis.id " \
                "JOIN katuze ON par.katuze_kod = katuze.kod " \
                "LEFT JOIN bud ON par.bud_id = bud.id " \
                "LEFT JOIN typbud ON bud.typbud_kod = typbud.kod " \
                "WHERE par.id = {};".format(columns, id)

        return self.__evaluate(query)

    def budova(self, id, extended):
        """

        :type id: str
        :type extended: bool
        :return:
        """
        columns = ", ".join(self.budColumns(extended))
        query = "SELECT {} " \
                "FROM bud " \
                "JOIN typbud ON typbud.kod = bud.typbud_kod " \
                "JOIN par ON par.bud_id = bud.id " \
                "LEFT JOIN tel ON bud.tel_id = tel.id " \
                "LEFT JOIN zpvybu ON zpvybu.kod = bud.zpvybu_kod " \
                "LEFT JOIN casobc ON casobc.kod = bud.caobce_kod " \
                "JOIN katuze ON par.katuze_kod = katuze.kod " \
                "LEFT JOIN drupoz ON drupoz.kod = par.drupoz_kod " \
                "WHERE bud.id = {};".format(columns, id)

        return self.__evaluate(query)

    def jednotka(self, id, extended):
        """

        :type id: str
        :type extended: bool
        :return:
        """
        columns = ", ".join(self.jedColumns(extended))
        query = "SELECT {} " \
                "FROM jed " \
                "JOIN typjed ON typjed.kod = jed.typjed_kod " \
                "LEFT JOIN zpvyje ON zpvyje.kod = jed.zpvyje_kod " \
                "LEFT JOIN bud ON bud.id = jed.bud_id " \
                "JOIN typbud ON typbud.kod = bud.typbud_kod " \
                "JOIN par on par.bud_id = bud.id " \
                "LEFT JOIN drupoz ON drupoz.kod = par.drupoz_kod " \
                "JOIN katuze ON par.katuze_kod = katuze.kod " \
                "JOIN tel ON tel.id = jed.tel_id " \
                "WHERE jed.id = {};".format(columns, id)

        return self.__evaluate(query)

    def budovaJednotky(self, id):
        """

        :type id: str
        :return:
        """
        query = "SELECT jed.id jed_id, " \
                "jed.cislo_jednotky jed_cislo_jednotky, " \
                "bud.cislo_domovni bud_cislo_domovni " \
                "FROM bud " \
                "JOIN jed ON bud.id = jed.bud_id " \
                "WHERE bud.id = {};".format(id)

        return self.__evaluate(query)

    def sousedniParcely(self, id):
        """

        :type id: str
        :return:
        """
        query = "SELECT DISTINCT hp.par_id_1 hp_par_id_1, " \
                "hp.par_id_2 hp_par_id_2 " \
                "FROM hp " \
                "WHERE hp.par_id_1 = {} " \
                "OR hp.par_id_2 = {};".format(id, id)

        return self.__evaluate(query)

    def opravnenySubjekt(self, id, extended):
        """

        :type id: str
        :type extended: bool
        :return:
        """
        columns = ", ".join(self.opsubColumns(extended))
        query = "SELECT {} " \
                "FROM opsub " \
                "JOIN charos ON charos.kod = opsub.charos_kod " \
                "WHERE opsub.id = {};".format(columns, id)

        return self.__evaluate(query)

    def nemovitostTeleso(self, id, nemovitost):
        """

        :type id: str
        :type nemovitost: Nemovitost
        :return:
        """
        table = self.nemovitost2TableName(nemovitost)
        query = "SELECT tel.id tel_id, tel.cislo_tel tel_cislo_tel " \
                "FROM tel " \
                "JOIN {} ON {}.tel_id = tel.id " \
                "WHERE {}.id = {};".format(table, table, table, id)

        return self.__evaluate(query)

    def telesoVlastnici(self, id):
        """

        :type id: str
        :return:
        """
        query = "SELECT " \
                "vla.id vla_id, " \
                "vla.opsub_id vla_opsub_id, " \
                "vla.podil_citatel vla_podil_citatel, " \
                "vla.podil_jmenovatel vla_podil_jmenovatel, " \
                "typrav.nazev typrav_nazev, " \
                "typrav.sekce typrav_sekce " \
                "FROM vla " \
                "JOIN tel ON vla.tel_id = tel.id " \
                "JOIN typrav ON typrav.kod = vla.typrav_kod " \
                "WHERE tel.id = {} ORDER BY typrav.sekce;".format(id)

        return self.__evaluate(query)

    def nemovitostOchrana(self, id, nemovitost):
        """

        :type id: str
        :type nemovitost: Nemovitost
        :return:
        """
        table = self.nemovitost2TableName(nemovitost)
        query = "SELECT zpochn.nazev zpochn_nazev " \
                "FROM zpochn " \
                "JOIN {} ON rzo.{}_id = {}.id " \
                "JOIN rzo ON rzo.zpochr_kod = zpochn.kod " \
                "WHERE {}.id = {};".format(table, table, table, table, id)

        return self.__evaluate(query)

    def vlastnikNemovitosti(self, id):
        """

        :type id: str
        :return:
        """
        query = "SELECT tel.cislo_tel tel_cislo_tel, " \
                "tel.id tel_id, " \
                "par.id par_id, " \
                "bud.id bud_id, " \
                "jed.id jed_id " \
                "FROM tel " \
                "JOIN vla ON vla.tel_id = tel.id " \
                "JOIN opsub ON vla.opsub_id = opsub.id " \
                "LEFT JOIN par ON par.tel_id = tel.id " \
                "LEFT JOIN bud ON bud.tel_id = tel.id " \
                "LEFT JOIN jed ON jed.tel_id = tel.id " \
                "WHERE opsub.id = {};".format(id)

        return self.__evaluate(query)

    def parcelaBpej(self, id):
        """

        :type id: str
        :return:
        """
        columns = ", ".join(self.bpejColumns())
        query = "SELECT {} " \
                "FROM bdp " \
                "JOIN par ON bdp.par_id = par.id " \
                "LEFT JOIN drupoz ON drupoz.kod = par.drupoz_kod " \
                "WHERE par.id = {};".format(columns, id)

        return self.__evaluate(query)

    def nemovitostJpv(self, id, op, pravo, where):
        """

        :type id: str
        :type op: str
        :type pravo: Pravo
        :type where: str
        :return:
        """
        table = self.opravnenyPovinny2TableName(op)
        columnNameSuffix = self.pravo2ColumnSuffix(pravo)
        columns = ", ".join(self.jpvColumns(False))
        query = "SELECT {} " \
                "FROM jpv " \
                "JOIN {} ON {}.id = jpv.{}_id_{} " \
                "JOIN typrav ON typrav.kod = jpv.typrav_kod " \
                "WHERE {}.id = {}{};".format(columns, table, table, table, columnNameSuffix,
                                             table, id, "" if not where else " AND {}".format(where))

        return self.__evaluate(query)

    def jpvListiny(self, id):
        """

        :type id: id
        :return:
        """
        columns = ", ".join(self.listinyColumns())
        query = "SELECT {} " \
                "FROM jpv " \
                "JOIN rl ON rl.jpv_id = jpv.id " \
                "JOIN listin ON rl.listin_id = listin.id " \
                "JOIN ldu ON ldu.listin_id=listin.id " \
                "join dul ON dul.kod = ldu.dul_kod " \
                "JOIN typlis ON typlis.kod=listin.typlist_kod " \
                "WHERE jpv.id = {};".format(columns, id)

        return self.__evaluate(query)

    def nabyvaciListiny(self, parIds, budIds, jedIds):
        """

        :type parIds: parcely ids
        :type budIds: budovy ids
        :type jedIds: jednotky ids
        :return:
        """
        columns = ", ".join(self.listinyColumns())
        query = "SELECT DISTINCT {} " \
                "FROM rl " \
                "JOIN listin ON rl.listin_id = listin.id " \
                "LEFT JOIN par ON par.id=rl.par_id " \
                "LEFT JOIN bud ON bud.id=rl.bud_id " \
                "LEFT JOIN jed ON jed.id=rl.jed_id " \
                "JOIN ldu ON ldu.listin_id=listin.id " \
                "JOIN dul ON dul.kod = ldu.dul_kod " \
                "JOIN typlis ON typlis.kod=listin.typlist_kod " \
                "WHERE par.id in ({}) " \
                "OR bud.id in ({}) " \
                "OR jed.id in ({}) " \
                "ORDER BY rl.listin_id;".format(
                    columns, ",".join(parIds), ",".join(budIds), ",".join(jedIds))

        return self.__evaluate(query)

    def vlastnik(self, id, extended=False):
        """

        :type id: str
        :type extended: bool
        :return:
        """
        columns = ", ".join(self.opsubColumns(extended))
        query = "SELECT {} " \
                "FROM opsub " \
                "JOIN charos ON opsub.charos_kod = charos.kod " \
                "WHERE opsub.id = {};".format(columns, id)
        return self.__evaluate(query)

    def dveRadyCislovani(self):
        """

        :return: bool
        """
        query = "SELECT 1 FROM doci WHERE druh_cislovani_par = 1"
        self.setQuery(query, QSqlDatabase.database(self.__mConnectionName))

        if self.rowCount() > 0:
            return True
        else:
            return False

    def definicniBod(self, id, nemovitost):
        """

        :type id: str
        :type nemovitost: Nemovitost
        :return:
        """
        tableName = self.nemovitost2TableName(nemovitost)
        query = "SELECT obdebo.souradnice_x obdebo_souradnice_x, " \
                "obdebo.souradnice_y obdebo_souradnice_y " \
                "FROM obdebo " \
                "WHERE {}_id = {};".format(tableName, id)
        return self.__evaluate(query)

    def searchOpsub(self, jmeno, identifikator, sjm, opo, ofo, lv):
        """

        :type jmeno: str
        :type identifikator: str
        :type sjm: bool
        :type opo: bool
        :type ofo: bool
        :type lv: str
        :return:
        """
        whereJmeno = u''
        join = u''

        if jmeno:
            if ofo:
                whereJmeno += u"opsub.jmeno LIKE ('%{}%') OR opsub.prijmeni LIKE ('%{}%') OR ".format(
                    jmeno, jmeno)
            if sjm or opo:
                whereJmeno += u"opsub.nazev LIKE ('%{}%') OR ".format(jmeno)
            whereJmeno += u"0 "

        whereIdent = u''
        if identifikator:
            if ofo:
                whereIdent += u"opsub.rodne_cislo = {} OR ".format(
                    identifikator)
            if opo:
                whereIdent += u"opsub.ico = {} OR ".format(identifikator)
            whereIdent += u'0 '

        opsubType = []
        if ofo == u'1':
            opsubType.append("'OFO'")
        if opo == u'1':
            opsubType.append("'OPO'")
        if sjm == u'1':
            opsubType.append("'BSM'")
        where = u"WHERE "
        if whereJmeno:
            where += u"({}) AND ".format(whereJmeno)
        if whereIdent:
            where += u"({}) AND ".format(whereIdent)

        if lv:
            where += u"tel.cislo_tel = {} AND ".format(lv)
            join += u"JOIN vla ON vla.opsub_id = opsub.id " \
                    u"JOIN tel ON vla.tel_id = tel.id "

        where += u"opsub.opsub_type IN ({}) ".format(", ".join(opsubType))
        query = u"SELECT DISTINCT opsub.id opsub_id " \
                u"FROM opsub " \
                u"{} {} " \
                u"ORDER BY opsub.prijmeni, opsub.nazev;".format(join, where)
        return self.__evaluate(query)

    def searchPar(self, parcelniCislo, typIndex, druhKod, lv):
        """

        :type parcelniCislo: str
        :type typIndex: str
        :type druhKod: str
        :type lv: str
        :return:
        """
        where = u"WHERE "
        join = u''

        if parcelniCislo:
            kmenAPoddeleni = parcelniCislo.split('/')
            where += u"par.kmenove_cislo_par = {} AND ".format(
                kmenAPoddeleni[0])

            if len(kmenAPoddeleni) == 2 and kmenAPoddeleni[1] != u"":
                where += u"par.poddeleni_cisla_par = {} AND ".format(
                    kmenAPoddeleni[1])

        if druhKod:
            where += u"drupoz.zkratka = '{}' AND ".format(druhKod)

        if typIndex == u'1':
            where += u"drupoz.stavebni_parcela = 'n' AND "
        elif typIndex == u'2':
            where += u"drupoz.stavebni_parcela = 'a' AND "

        if druhKod:
            # where += u"par.drupoz_kod = '{}' AND ".format(druhKod)
            where += u"par.drupoz_kod = (SELECT kod FROM drupoz WHERE zkratka='{}') AND ".format(
                druhKod)

        if lv:
            where += u"tel.cislo_tel = {} AND ".format(lv)
            join += u"JOIN tel ON tel.id = par.tel_id "

        where += u'1 '

        query = u"SELECT DISTINCT par.id par_id " \
                u"FROM par " \
                u"JOIN drupoz ON par.drupoz_kod = drupoz.kod " \
                u"{} {};".format(join, where)
        return self.__evaluate(query)

    def searchBud(self, domovniCislo, naParcele, zpusobVyuzitiKod, lv):
        """

        :type domovniCislo: str
        :type naParcele: str
        :type zpusobVyuzitiKod: str
        :type lv: str
        :return:
        """
        where = u"WHERE "
        join = u""

        if domovniCislo:
            where += u"bud.cislo_domovni = {} AND ".format(domovniCislo)

        if naParcele:
            kmenAPoddeleni = str(naParcele).split("/")
            where += u"par.kmenove_cislo_par = {} AND ".format(
                kmenAPoddeleni[0])

            if len(kmenAPoddeleni) == 2 and kmenAPoddeleni[1] != u"":
                where += u"par.poddeleni_cisla_par = {} AND ".format(
                    kmenAPoddeleni[1])

            join += u"JOIN par ON bud.id = par.bud_id "

        if lv:
            where += u"tel.cislo_tel = {} AND ".format(lv)
            join += u"JOIN tel ON tel.id = bud.tel_id "

        if zpusobVyuzitiKod:
            where += u"zpvybu.kod = (SELECT kod FROM zpvybu WHERE zkratka='{}') AND ".format(
                zpusobVyuzitiKod)
            join += u"JOIN zpvybu ON zpvybu.kod = bud.zpvybu_kod "

        where += u"1 "

        query = u"SELECT DISTINCT bud.id bud_id " \
                u"FROM bud " \
                u"{} {};".format(join, where)

        return self.__evaluate(query)

    def searchJed(self, cisloJednotky, domovniCislo, naParcele, zpusobVyuzitiKod, lv):
        """

        :type cisloJednotky: str
        :type domovniCislo: str
        :type naParcele: str
        :type zpusobVyuzitiKod: str
        :type lv: str
        :return:
        """
        where = u"WHERE "
        join = u''

        if cisloJednotky:
            where += u"jed.cislo_jednotky = {} AND ".format(cisloJednotky)

        if domovniCislo:
            where += u"bud.cislo_domovni = {} AND ".format(domovniCislo)

        if naParcele:
            kmenAPoddeleni = str(naParcele).split(u"/")
            where += u"par.kmenove_cislo_par = {} AND ".format(
                kmenAPoddeleni[0])

            if len(kmenAPoddeleni) == 2 and kmenAPoddeleni[1] != u"":
                where += u"par.poddeleni_cisla_par = {} AND ".format(
                    kmenAPoddeleni[1])

            join += u"JOIN par ON bud.id = par.bud_id "

        if lv:
            where += u"tel.cislo_tel = {} AND ".format(lv)
            join += u"JOIN tel ON tel.id = jed.tel_id "

        if zpusobVyuzitiKod:
            where += u"zpvyje.nazev = '{}' AND ".format(zpusobVyuzitiKod)
            join += u"JOIN zpvyje ON zpvyje.kod = jed.zpvyje_kod "

        where += u"1 "

        query = u"SELECT DISTINCT jed.id jed_id " \
                u"FROM jed " \
                u"JOIN bud ON bud.id = jed.bud_id " \
                u"{} {};".format(join, where)

        return self.__evaluate(query)

    def parColumns(self, extended):
        """

        :type extended: bool
        :return: []
        """
        columns = [
            u"par.id par_id", u"par.kmenove_cislo_par par_kmenove_cislo_par",
                   u"par.poddeleni_cisla_par par_poddeleni_cisla_par", u"par.vymera_parcely par_vymera_parcely",
                   u"tel.id tel_id", u"tel.cislo_tel tel_cislo_tel", u"drupoz.nazev drupoz_nazev",
                   u"drupoz.stavebni_parcela drupoz_stavebni_parcela", u"zpvypo.nazev zpvypo_nazev"]

        if extended:
            columns.append(u"par.stav_dat par_stav_dat")
            columns.append(u"par.par_type par_par_type")
            columns.append(u"par.katuze_kod par_katuze_kod")
            columns.append(u"katuze.nazev katuze_nazev")
            columns.append(
                u"maplis.oznaceni_mapoveho_listu maplis_oznaceni_mapoveho_listu")
            columns.append(u"zpurvy.nazev zpurvy_nazev")
            columns.append(u"par.cena_nemovitosti par_cena_nemovitosti")
            columns.append(u"bud_id bud_id")
            columns.append(u"bud.cislo_domovni bud_cislo_domovni")
            columns.append(u"typbud.nazev typbud_nazev")
            columns.append(u"typbud.zkratka typbud_zkratka")

        return columns

    def budColumns(self, extended):
        """

        :type extended: bool
        :return: []
        """
        columns = [
            u"bud.id bud_id", u"bud.typbud_kod bud_typbud_kod", u"casobc.nazev casobc_nazev",
                   u"casobc.kod casobc_kod", u"bud.cislo_domovni bud_cislo_domovni", u"par.id par_id", u"tel.id tel_id",
                   u"tel.cislo_tel tel_cislo_tel", u"par.kmenove_cislo_par par_kmenove_cislo_par",
                   u"par.poddeleni_cisla_par par_poddeleni_cisla_par", u"drupoz.stavebni_parcela drupoz_stavebni_parcela",
                   u"zpvybu.kod zpvybu_kod", u"zpvybu.nazev zpvybu_nazev", u"typbud.nazev typbud_nazev",
                   u"typbud.zkratka typbud_zkratka", u"typbud.zadani_cd typbud_zadani_cd"]

        if extended:
            columns.append(u"bud.cena_nemovitosti bud_cena_nemovitosti")
            columns.append(u"par.katuze_kod par_katuze_kod")
            columns.append(u"katuze.nazev katuze_nazev")

        return columns

    def jedColumns(self, extended):
        """

        :type extended: bool
        :return: []
        """
        columns = [
            u"jed.id jed_id", u"bud.id bud_id", u"bud.cislo_domovni bud_cislo_domovni", u"typjed.nazev typjed_nazev",
                   u"jed.cislo_jednotky jed_cislo_jednotky", u"zpvyje.nazev zpvyje_nazev",
                   u"jed.podil_citatel jed_podil_citatel", u"jed.podil_jmenovatel jed_podil_jmenovatel", u"tel.id tel_id",
                   u"tel.cislo_tel tel_cislo_tel"]

        if extended:
            columns.append(u"jed.cena_nemovitosti jed_cena_nemovitosti")
            columns.append(u"jed.popis jed_popis")
            columns.append(u"typbud.zkratka typbud_zkratka")
            columns.append(u"par.katuze_kod par_katuze_kod")
            columns.append(u"par.id par_id")
            columns.append(u"drupoz.stavebni_parcela drupoz_stavebni_parcela")
            columns.append(u"par.kmenove_cislo_par par_kmenove_cislo_par")
            columns.append(u"par.poddeleni_cisla_par par_poddeleni_cisla_par")
            columns.append(u"tel.id tel_id")
            columns.append(u"tel.cislo_tel tel_cislo_tel")
            columns.append(u"katuze.nazev katuze_nazev")

        return columns

    def opsubColumns(self, extended):
        """

        :type extended: bool
        :return: []
        """
        columns = [
            u"opsub.opsub_type opsub_opsub_type", u"opsub.id opsub_id", u"charos.zkratka charos_zkratka",
                   u"charos.nazev charos_nazev", u"opsub.nazev opsub_nazev",
                   u"opsub.titul_pred_jmenem opsub_titul_pred_jmenem", u"opsub.jmeno opsub_jmeno",
                   u"opsub.prijmeni opsub_prijmeni", u"opsub.titul_za_jmenem opsub_titul_za_jmenem"]

        if extended:
            columns.append(
                u"opsub.id_je_1_partner_bsm opsub_id_je_1_partner_bsm")
            columns.append(
                u"opsub.id_je_2_partner_bsm opsub_id_je_2_partner_bsm")
            columns.append(u"opsub.ico opsub_ico")
            columns.append(u"opsub.rodne_cislo opsub_rodne_cislo")
            columns.append(u"opsub.cislo_orientacni opsub_cislo_orientacni")
            columns.append(u"opsub.nazev_ulice opsub_nazev_ulice")
            columns.append(u"opsub.cast_obce opsub_cast_obce")
            columns.append(u"opsub.obec opsub_obec")
            columns.append(u"opsub.psc opsub_psc")
            columns.append(u"opsub.mestska_cast opsub_mestska_cast")
        return columns

    def jpvColumns(self, extended):
        """

        :type extended: bool
        :return: []
        """
        columns = [
            u"typrav.nazev typrav_nazev", u"jpv.id jpv_id", u"jpv.popis_pravniho_vztahu jpv_popis_pravniho_vztahu",
                   u"jpv.par_id_k jpv_par_id_k", u"jpv.par_id_pro jpv_par_id_pro", u"jpv.bud_id_k jpv_bud_id_k",
                   u"jpv.bud_id_pro jpv_bud_id_pro", u"jpv.jed_id_k jpv_jed_id_k", u"jpv.jed_id_pro jpv_jed_id_pro",
                   u"jpv.opsub_id_k jpv_opsub_id_k", u"jpv.opsub_id_pro jpv_opsub_id_pro"]

        if extended:
            pass
        return columns

    def listinyColumns(self):
        """

        :return: []
        """
        columns = [
            u"rl.listin_id rl_listin_id", u"rl.opsub_id rl_opsub_id", u"typlis.nazev typlis_nazev",
                   u"dul.nazev dul_nazev"]

        return columns

    def bpejColumns(self):
        """

        :return: []
        """
        columns = [
            u"bdp.bpej_kod bdp_bpej_kod", u"bdp.vymera bdp_vymera", u"par.id par_id",
                   u"par.kmenove_cislo_par par_kmenove_cislo_par", u"par.poddeleni_cisla_par par_poddeleni_cisla_par",
                   u"drupoz.stavebni_parcela drupoz_stavebni_parcela"]

        return columns

    def nemovitost2TableName(self, nemovitost):
        """

        :type nemovitost: Nemovitost
        :return: str
        """
        table = u''

        if nemovitost == self.Nemovitost.NParcela:
            table = u"par"
        elif nemovitost == self.Nemovitost.NBudova:
            table = u"bud"
        elif nemovitost == self.Nemovitost.NJednotka:
            table = u"jed"
        else:
            pass

        return table

    def opravnenyPovinny2TableName(self, opravnenyPovinny):
        """

        :type opravnenyPovinny: OpravnenyPovinny
        :return: str
        """
        table = u''

        if opravnenyPovinny == self.OpravnenyPovinny.OPParcela:
            table = u"par"
        elif opravnenyPovinny == self.OpravnenyPovinny.OPBudova:
            table = u"bud"
        elif opravnenyPovinny == self.OpravnenyPovinny.OPJednotka:
            table = u"jed"
        elif opravnenyPovinny == self.OpravnenyPovinny.OPOsoba:
            table = u"opsub"
        else:
            pass

        return table

    def pravo2ColumnSuffix(self, pravo):
        """

        :type pravo: Pravo
        :return: str
        """
        columnNameSuffix = u''

        if pravo == self.Pravo.Opravneni:
            columnNameSuffix = u"pro"
        elif pravo == self.Pravo.Povinnost:
            columnNameSuffix = u"k"
        else:
            pass

        return columnNameSuffix

    def tableName2OpravnenyPovinny(self, name):
        """

        :type name: unicode
        :return: OpravnenyPovinny
        """
        if unicode(name).find(u"par") > -1:
            return self.OpravnenyPovinny.OPParcela
        if unicode(name).find(u"bud") > -1:
            return self.OpravnenyPovinny.OPBudova
        if unicode(name).find(u"jed") > -1:
            return self.OpravnenyPovinny.OPJednotka
        if unicode(name).find(u"opsub") > -1:
            return self.OpravnenyPovinny.OPOsoba

        return self.OpravnenyPovinny.OPParcela

    def druhyPozemku(self, pozemkova, stavebni):
        """

        :type pozemkova: bool
        :type stavebni: bool
        :return: bool
        """
        where = ''

        if pozemkova and stavebni:
            pass
        elif pozemkova:
            where += "WHERE drupoz.stavebni_parcela = 'n'"
        else:
            where += "WHERE drupoz.stavebni_parcela = 'a'"

        query = "SELECT drupoz.kod drupoz_kod, drupoz.zkratka drupoz_zkratka " \
                "FROM drupoz " \
                "{};".format(where)
        return self.__evaluate(query)

    def zpusobVyuzitiBudov(self):
        """

        :return: bool
        """
        query = "SELECT zpvybu.kod zpvybu_kod, zpvybu.zkratka zpvybu_zkratka " \
                "FROM zpvybu; "
        return self.__evaluate(query)

    def zpusobVyuzitiJednotek(self):
        """

        :return: bool
        """
        query = "SELECT zpvyje.kod zpvyje_kod, zpvyje.zkratka zpvyje_zkratka " \
                "FROM zpvyje; "
        return self.__evaluate(query)

    def __evaluate(self, query):
        """

        :type query: str
        :return: bool
        """
        t = QTime()
        t.start()

        qDebug("\n(VFK) SQL: {}\n".format(query))
        self.setQuery(query, QSqlDatabase.database(self.__mConnectionName))

        while self.canFetchMore():
            self.fetchMore()

        if t.elapsed() > 500:
            qDebug("\n(VFK) Time elapsed: {} ms\n".format(t.elapsed()))

        if self.lastError().isValid():
            qDebug('\n(VFK) SQL ERROR: {}'.format(self.lastError().text()))
            return False

        return True

    def value(self, row, column):
        """

        :type row:
        :type column:
        :return: str
        """
        value = unicode(self.record(row).field(column).value())

        if value == u"NULL" or value == u'None':
            return u''
        else:
            return unicode(value)
