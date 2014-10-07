# -*- coding: iso-8859-1 -*-
#------------------------------
# METROPACCESS-DIGIROAD
# MetropAccess-tutkimushanke
# HELSINGIN YLIOPISTO
# Koodi: Henrikki Tenkanen
#-------------------------------
# 4. Kokonaismatkaketjun Laskentaty�kalu (sis. pys�k�inti)
#-------------------------------

####################################################################################
#MetropAccess-Digiroad, ty�kalu Digiroad-aineiston muokkaukseen MetropAccess-hankkeen menetelm�n mukaisesti
#    Copyright (C) 2013  MetropAccess (Tenkanen). For MetropAccess-project and contact details, please see http://blogs.helsinki.fi/accessibility/
# 
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###################################################################################

import arcpy
from arcpy import env
import sys
import time
import string
import os

# Tarkistetaan tarvittavat Lisenssit
arcpy.CheckOutExtension("Network")

#--------------------------------------------
#OD COST MATRIX
#KOKONAISMATKAKETJUN LASKEMINEN:

#M��ritet��n tiedostopolut:

Origins = arcpy.GetParameterAsText(0)
Destinations = arcpy.GetParameterAsText(1)
NetworkData = arcpy.GetParameterAsText(2)
LiikenneElementit = arcpy.GetParameterAsText(3)
Impedanssi = arcpy.GetParameterAsText(4)
LaskKohteet = arcpy.GetParameterAsText(5)
Pysakointityyppi = int(arcpy.GetParameterAsText(6))
Pysakointikentta = arcpy.GetParameterAsText(7)
Kavelynopeus = float(arcpy.GetParameterAsText(8))
Grafiikka = arcpy.GetParameterAsText(9)

#Environment m��ritykset:
temp = arcpy.GetSystemEnvironment("TEMP")
ElemKansio = os.path.dirname(NetworkData)
OrigKansio = os.path.dirname(Origins)
DestKansio = os.path.dirname(Destinations)
mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd, "*")[0]

#Suoritusinfot:
def Aloitus():
    aika = time.asctime()
    teksti = "Aloitus: " + aika
    arcpy.AddMessage(teksti)

def Valmis():
    aika = time.asctime()
    teksti = "Valmis: " + aika
    arcpy.AddMessage(teksti)

def msg(Message):
    arcpy.AddMessage(Message)

def virhe(Virheilmoitus):
    arcpy.AddError(Virheilmoitus)
    sys.exit()

#Metodit/m��ritykset:
    
arcpy.overwriteOutputs = True
    
def AddLayerToMap(addLayer):
 mxd = arcpy.mapping.MapDocument("CURRENT")
 df = arcpy.mapping.ListDataFrames(mxd, "*")[0]
 arcpy.mapping.AddLayer(df, addLayer, "TOP")
 arcpy.RefreshActiveView()
 arcpy.RefreshTOC()
 del mxd, df, addLayer

def ExDel(haettava):
    if arcpy.Exists(haettava):
        arcpy.Delete_management(haettava)


msg("------------------------------")
msg("METROPACCESS-DIGIROAD")
msg("MetropAccess-tutkimushanke")
msg("HELSINGIN YLIOPISTO")
msg("-------------------------------")
msg("4. Kokonaismatkaketjun laskenta (sis. pys�k�inti)")
msg("-------------------------------")

time.sleep(2.5)

#------------------------------------------------------------------------------------
#TARKISTUKSET ENNEN LASKENTAA
Aloitus()
msg("TARKISTUKSET:")
arcpy.SetProgressor("step", "KOKONAISMATKAKETJUN LASKENTA...Tarkistukset ennen laskentaa...", 0, 100, 5) #Luodaan suoritusinfopalkki

#Tarkistetaan, ett� aineisto on joko EurefFiniss� tai KKJ:ssa

Desc = arcpy.Describe(NetworkData)
NDProjektio = Desc.spatialReference.factoryCode

if NDProjektio == 3067 or NDProjektio == 2391 or NDProjektio == 2392 or NDProjektio == 2393 or NDProjektio == 2394 or NDProjektio == 104129:
    msg("Tarkistettiin liikenneverkon projektio.")
else:
    virhe("Tieverkkoaineiston tulee olla projisoituna joko EUREF_FIN_TM35FIN:iin, GCS_EUREF_FIN:iin tai Finland_Zone_1, 2, 3 tai -4:��n (KKJ). Muuta Liikenne_elementti.shp projektio johonkin n�ist� Project -ty�kalulla, luo uusi Network Dataset perustuen t�h�n uuteen projisoituun LiikenneElementti -tiedostoon ja aja ty�kalu uudelleen.")
    
#Tarkistetaan pys�k�intikent�n l�ytyminen:
msg("Tarkistetaan pys�k�intikent�n l�ytyminen")
if Pysakointityyppi == 5:
    fieldList = arcpy.ListFields(Destinations, Pysakointikentta)
    fieldCount = len(fieldList)
    if fieldCount == 1:
        teksti = "K�ytt�j�n m��rittelem� pys�k�intikentt�!"
        msg(teksti)
    elif Pysakointikentta == "":
        virhe("VIRHE! Pys�k�intityypin m��ritt�v�� kentt�� ei ole m��ritetty!")
    else:
        virhe("VIRHE! Pys�k�intityypin m��ritt�v�� kentt�� ei l�ydy taulusta! Tarkista, ett� pys�k�intikentt� on luotu kohdetauluun ja ett� kirjoitusasu on oikein.")
        
Valmis()
#Tarkistetaan mitk� aikasakkolaskennan parametrit l�ytyv�t NetworkDatasetist�:
msg("Tarkistetaan kustannusparametrit")
Aloitus()

desc = arcpy.Describe(NetworkData)
attributes = desc.attributes
NDparams = []
for attribute in attributes:
    NDparams.append(attribute.name)

Haettava = ["Digiroa_aa", "Kokopva_aa", "Keskpva_aa", "Ruuhka_aa", "Pituus"]
Nro = 0
Accumulation = []
for x in range(5):
    if Haettava[Nro] in NDparams:
        Accumulation.append(Haettava[Nro])
        Nro += 1
    else:
        Nro += 1

Valmis()

#Tarkistetaan l�ytyyk� Impedanssi Accumulation taulusta, onko impedanssimuuttuja olemassa:
msg("Tarkistetaan, ett� impedanssiatribuutti l�ytyy Network Datasetist�")
Aloitus()

if Impedanssi in NDparams:
    msg("Impedanssi m��ritetty!")
else:
    virhe("VIRHE! M��ritelty� impedanssia ei ole m��ritelty Network Datasettiin. Tarkista, ett� muuttuja on todella olemassa\nja ett� Impedanssikent�n kirjoitusasu t�sm�� k�ytett�v�n muuttujan kanssa. ")

NDPath = desc.path
NDsource = desc.edgeSources[0].name
LE = NDPath + "\\" + NDsource + ".shp" #Parsitaan sourcedatan (Liikenne_Elementit) polku ja nimi
del desc

desc = arcpy.Describe(LiikenneElementit)
basename = desc.baseName
del desc

if basename != NDsource: #Tarkistetaan onko inputiksi m��ritelty LiikenneElementti -tiedosto Network Datan todellinen source-layer:
    msg("LiikenneElementti -tiedosto ei ollut Network Datan source-layer. Vaihdettiin LiikenneElementti -tiedosto Network Datan Edge-sourceksi.")
    LiikenneElementit = LE
    
if not Impedanssi in Accumulation:
    Accumulation.append(Impedanssi)
    msg("K�ytt�j�n m��rittelem� impedanssi lis�ttiin Accumulation arvoihin!")
    
            
#Tarkistetaan laskettavien kohteiden lukum��r�:
LaskKohteet.replace(" ","")
if LaskKohteet == "" or LaskKohteet == "ALL" or LaskKohteet == "all" or LaskKohteet == "All":
    LaskKohteet = ""
elif LaskKohteet == "0":
    virhe("Laskettavia kohteita tulee olla v�hint��n yksi!")
else:
    LaskKohteet = LaskKohteet
  
Valmis()
arcpy.SetProgressorPosition(5)
msg("----------------------")
#---------------------------------------------------------------------------------------------        
#LASKENTA
#---------------------------------------------------------------------------------------------
msg("ALOITETAAN LASKENTA")
msg("Luodaan tarvittavat attribuutit")
arcpy.SetProgressorLabel("KOKONAISMATKAKETJUN LASKENTA...Luodaan tarvittavat attribuutit...")
Aloitus()
        
#Tehd��n tiedostoihin tarvittavat attribuutit:
#Origins:
arcpy.AddField_management(Origins, "NameO", "TEXT")
arcpy.AddField_management(Origins, "Kavely_O_T", "DOUBLE") #K�velyaika l�ht�paikasta l�himp��n tieverkkoon (vanha: KavelLahtO)
arcpy.AddField_management(Origins, "Kavely_T_P", "DOUBLE") #K�velyaika tieverkosta parkkipaikalle (vanha: KavelParkO)

#Ajoaika kent�t:
if "Digiroa_aa" in Accumulation:
    arcpy.AddField_management(Origins, "Digiroa_aa", "DOUBLE")
if "Kokopva_aa" in Accumulation:
    arcpy.AddField_management(Origins, "Kokopva_aa", "DOUBLE")
if "Keskpva_aa" in Accumulation:
    arcpy.AddField_management(Origins, "Keskpva_aa", "DOUBLE")
if "Ruuhka_aa" in Accumulation:
    arcpy.AddField_management(Origins, "Ruuhka_aa", "DOUBLE")
if Impedanssi in Accumulation:                                  #Tehd��n jos k�ytt�j� on haluaa k�ytt�� jotain omaa impedanssiaan
    arcpy.AddField_management(Origins, Impedanssi, "DOUBLE")
if "Pituus" in Accumulation:
    arcpy.AddField_management(Origins, "KavelMatkO", "DOUBLE") #Matka l�ht�paikasta parkkipaikalle kaupungin alueella/kaupungin ulkopuolella
    arcpy.AddField_management(Origins, "KavelDistO", "DOUBLE") #K�velymatka l�ht�paikasta l�himp��n tieverkkopisteeseen
#Destinations:
arcpy.AddField_management(Destinations, "NameD", "TEXT")
arcpy.AddField_management(Destinations, "Parkkiaika", "DOUBLE") #Parkkipaikan etsint��n kuluva aika (vanha: ParkkiAika)
arcpy.AddField_management(Destinations, "Kavely_P_T", "DOUBLE") #K�velyaika parkkipaikalta l�himp��n tieverkkoon (vanha: KavelParkD)
arcpy.AddField_management(Destinations, "Kavely_T_D", "DOUBLE") #K�velyaika l�himm�st� tieverkkopisteest� kohteeseen (vanha: KavelLahtD)

if "Pituus" in Accumulation:
    arcpy.AddField_management(Destinations, "KavelMatkD", "DOUBLE") #K�velymatka parkkipaikalta l�himp��n tieverkkopisteeseen
    arcpy.AddField_management(Destinations, "KavelDistD", "DOUBLE") #K�velymatka l�himm�st� tieverkkopisteest� kohteeseen kantakaupungin alueella/kaupungin ulkopuolella

Valmis()
arcpy.SetProgressorPosition(10)
msg("----------------------")

#Tehd��n id-kent�t:
msg("Luodaan ID-kent�t")
arcpy.SetProgressorLabel("KOKONAISMATKAKETJUN LASKENTA...Luodaan ID-kent�t...")
Aloitus()

arcpy.CalculateField_management(Origins, "NameO", "\"O\" & [FID]", "VB", "")
arcpy.CalculateField_management(Destinations, "NameD", "\"D\" & [FID]", "VB", "")

Valmis()
arcpy.SetProgressorPosition(15)
msg("----------------------")

#Lasketaan pisteiden et�isyydet tieverkostosta:
msg("Lasketaan k�velyaika ja matka tieverkostosta")
arcpy.SetProgressorLabel("KOKONAISMATKAKETJUN LASKENTA...Lasketaan k�velyaika ja matka tieverkostosta...")
Aloitus()

arcpy.Near_analysis(Origins, LiikenneElementit, "500 Meters", "NO_LOCATION", "NO_ANGLE")
arcpy.Near_analysis(Destinations, LiikenneElementit, "500 Meters", "NO_LOCATION", "NO_ANGLE")

#Lasketaan k�velyaika ja matka tieverkostosta:
OrigReader = arcpy.UpdateCursor(Origins)
DestReader = arcpy.UpdateCursor(Destinations)

for row in OrigReader:
    row.Kavely_O_T = row.NEAR_DIST / Kavelynopeus
    row.KavelDistO = row.NEAR_DIST
    OrigReader.updateRow(row)
    del row

for row in DestReader:
    row.Kavely_T_D = row.NEAR_DIST / Kavelynopeus
    row.KavelDistD = row.NEAR_DIST
    DestReader.updateRow(row)
    del row

del OrigReader
del DestReader

Valmis()
arcpy.SetProgressorPosition(20)
msg("----------------------")

#-----------------------------------------------------------------------------------------
#Lasketaan parkkipaikan etsint��n menev� aika perustuen k�ytt�j�n parametreihin:
# Pys�k�intityypit - etsint�aika (minuuteissa):
# 0: Ei oteta huomioon 
# 1: Keskiarvo - 0.42 (oletus)
# 2: Kadunvarsipaikka - 0.73
# 3: Pys�k�intitalo - 0.22
# 4: Erillisalueet - 0.16
# 5: Pys�k�intityyppi l�ytyy k�ytt�j�n m��ritt�m�st� kent�st�
# Pysakointikentta: <String> - K�ytt�j�n m��ritt�m� kentt�, josta l�ytyy pys�k�intityyppi
#------------------------------------------------------------------------------------------

msg("Lasketaan pys�k�intipaikan etsint��n kuluva aika")
arcpy.SetProgressorLabel("KOKONAISMATKAKETJUN LASKENTA...Lasketaan pys�k�intipaikan etsint��n kuluva aika...")
Aloitus()

if Pysakointityyppi == 0:
    arcpy.CalculateField_management(Destinations, "Parkkiaika", "0 ", "VB", "")
elif Pysakointityyppi == 1:
    arcpy.CalculateField_management(Destinations, "Parkkiaika", "0.42 ", "VB", "")

elif Pysakointityyppi == 2:
    arcpy.CalculateField_management(Destinations, "Parkkiaika", "0.73 ", "VB", "")

elif Pysakointityyppi == 3:
    arcpy.CalculateField_management(Destinations, "Parkkiaika", "0.22 ", "VB", "")

elif Pysakointityyppi == 4:
    arcpy.CalculateField_management(Destinations, "Parkkiaika", "0.16 ", "VB", "")

elif Pysakointityyppi == 5:
    DestReader = arcpy.UpdateCursor(Destinations)
    for row in DestReader:
        if row.getValue(Pysakointikentta) == 0:
            row.Parkkiaika = 0
        elif row.getValue(Pysakointikentta) == 1:
            row.Parkkiaika = 0.42
        elif row.getValue(Pysakointikentta) == 2:
            row.Parkkiaika = 0.73
        elif row.getValue(Pysakointikentta) == 3:
            row.Parkkiaika = 0.22
        elif row.getValue(Pysakointikentta) == 4:
            row.Parkkiaika = 0.16
        else:
            row.Parkkiaika = 0
            msg("Kohteelle asetettu pys�k�intityypin arvo on sallittujen arvojen (0-4) ulkopuolella! Kohteen pys�k�intityyppi� ei oteta huomioon.")
        DestReader.updateRow(row)
        del row
    del DestReader

Valmis()
arcpy.SetProgressorPosition(25)
msg("----------------------")

#------------------------------------------------------
#Kantakaupunki polygonin rakentaminen valintaa varten:
#------------------------------------------------------          
msg("Luodaan kantakaupunkipolygoni")
arcpy.SetProgressorLabel("KOKONAISMATKAKETJUN LASKENTA...Luodaan kantakaupunkipolygoni...")
Aloitus()

#M��ritet��n polygonien kulmien koordinaatit:
coordList = [[387678.024778,6675360.99039],[387891.53396,6670403.35286],[383453.380944,6670212.21613],[383239.871737,6675169.85373],[387678.024778,6675360.99039]] #Koordinaatit ovat EUREF_FIN_TM35FIN:iss�
point = arcpy.Point()
array = arcpy.Array()

#Lis�t��n koordinaatit Arrayhin:
for coordPair in coordList:
    point.X = coordPair[0]
    point.Y = coordPair[1]
    array.add(point)

Kantakaupunki = arcpy.Polygon(array)

#M��ritet��n Spatial Reference:
sr = arcpy.SpatialReference()
sr.factoryCode = 3067
sr.create()

env.workspace = temp

#Luodaan kantakaupunki tiedosto:
Kantis = "Kantakaupunki.shp"
ExDel(Kantis)
arcpy.Select_analysis(Kantakaupunki, Kantis)

#M��ritet��n kantakaupungille projektio:
arcpy.DefineProjection_management(Kantis, sr)
msg("Luotiin kantakaupunki")
Valmis()
arcpy.SetProgressorPosition(30)
msg("----------------------")

#----------------------------------------------------
#M��ritet��n tiedostojen Spatial Reference:
#----------------------------------------------------          
msg("M��ritet��n tiedostot samaan koordinaatistoon")
arcpy.SetProgressorLabel("KOKONAISMATKAKETJUN LASKENTA...M��ritet��n tiedostot samaan koordinaatistoon...")
Aloitus()

#Destinations:
DDesc = arcpy.Describe(Destinations)
DestProjektio = DDesc.spatialReference.Name
DFactCode = DDesc.spatialReference.factoryCode
DProj = DestProjektio[:8]
KohdePath = temp + "\\" + "DestinationsProj.shp"

#Origins:
ODesc = arcpy.Describe(Origins)
OrigProjektio = ODesc.spatialReference.Name
OFactCode = ODesc.spatialReference.factoryCode
OProj = OrigProjektio[:8]
LahtoPath = temp + "\\" + "OriginsProj.shp"
KantisPath = temp + "\\" + "KantisProj.shp"

ExDel("DestinationsProj.shp")
ExDel("OriginsProj.shp")
ExDel("KantisProj.shp")

#Luodaan spatial reference perustuen NetworkDatan SR:een:
del sr
sr = arcpy.SpatialReference()
if NDProjektio == 3067: #EurefFin
    sr.factoryCode = 3067
    sr.create()
elif NDProjektio == 104129: #GCS_EurefFIN
    sr.factoryCode = 104129
    sr.create()
elif NDProjektio == 2391: #KKJ1
    sr.factoryCode = 2391
    sr.create()
elif NDProjektio == 2392: #KKJ2
    sr.factoryCode = 2392
    sr.create()
elif NDProjektio == 2393: #KKJ3
    sr.factoryCode = 2393
    sr.create()
elif NDProjektio == 2394: #KKJ4
    sr.factoryCode = 2394
    sr.create()


msg("M��ritettiin Spatial Reference")

#M��ritet��n Kohteille ja L�ht�paikoille oikea projektio, jos NetworkData on EUREF_FIN_TM35FIN:iss� tai GCS_EUREF_FIN:iss�::

if NDProjektio == 3067 or NDProjektio == 104129:
    if NDProjektio == 104129:
        arcpy.Project_management(Kantis, KantisPath, sr, "") #M��ritet��n kantakaupunki samaan koordinaatistoon
        Kantakaupunki = KantisPath
#Destinations:
    if NDProjektio != DFactCode: #Jos Network Data ja Destinationit ovat eri koordinaatistossa:
        if DFactCode >= 2391 and DFactCode <= 2394:
            Dtransform_method = "KKJ_To_EUREF_FIN"
        elif DFactCode == 3067:
            Dtransform_method = ""
        elif DProj == "WGS_1984" or DFactCode == 4326: #Projected WGS_1984 tai GCS_WGS_1984
            Dtransform_method = "EUREF_FIN_To_WGS_1984"
        elif DProj == "ETRS_198":
            Dtransform_method = "EUREF_FIN_To_ETRS_1989"
        else:
            virhe("Kohdepisteet tulee olla projisoituna johonkin seuraavista koordinaatistoista:")
            virhe("KKJ, EUREF_FIN, WGS_1984, ETRS_1989")
               
        env.workspace = temp
        if arcpy.Exists("DestinationsProj.shp"):
            arcpy.Delete_management("DestinationsProj.shp")
        arcpy.Project_management(Destinations, KohdePath, sr, Dtransform_method) #M��ritet��n Destinationit samaan koordinaatistoon
        Destinations = KohdePath
        msg("Kohdepaikkojen projektio vaihdettiin samaksi kuin Network Datalla. Luotiin kopio tiedostosta.")

#----------------------
#Origins:
    if NDProjektio != OFactCode: #Jos Network Data ja Originit ovat eri koordinaatistossa:
        if OFactCode >= 2391 and OFactCode <= 2394:
            Otransform_method = "KKJ_To_EUREF_FIN"
        elif OFactCode == 3067:
            Otransform_method = ""
        elif OProj == "WGS_1984" or OFactCode == 4326: #Projected WGS_1984 tai GCS_WGS_1984
            Otransform_method = "EUREF_FIN_To_WGS_1984"
        elif OProj == "ETRS_198":
            Otransform_method = "EUREF_FIN_To_ETRS_1989"
        else:
            virhe("L�ht�pisteet tulee olla projisoituna johonkin seuraavista koordinaatistoista:")
            virhe("KKJ, EUREF_FIN, WGS_1984, ETRS_1989")
        
        env.workspace = temp
        if arcpy.Exists("OriginsProj.shp"):
            arcpy.Delete_management("OriginsProj.shp")
        arcpy.Project_management(Origins, LahtoPath, sr, Otransform_method) #M��ritet��n Destinationit samaan koordinaatistoon
        Origins = LahtoPath
        msg("L�ht�paikkojen projektio vaihdettiin samaksi kuin Network Datalla. Luotiin kopio tiedostosta.")

#M��ritet��n Kohteille ja L�ht�paikoille oikea projektio, jos NetworkData on KKJ:ssa:
elif NDProjektio == 2391 or NDProjektio == 2392 or NDProjektio == 2393 or NDProjektio == 2394:
    arcpy.Project_management(Kantis, KantisPath, sr, "KKJ_To_EUREF_FIN") #M��ritet��n kantakaupunki samaan koordinaatistoon
    Kantakaupunki = KantisPath
    
    if NDProjektio != DFactCode: #Jos NetworkData ja kohdepisteet ovat eri KKJ:ssa projisoidaan ne samaan.
        if DFactCode >= 2391 and DFactCode <= 2394:
            Dtransform_method = ""
        elif DProj == "WGS_1984" or DFactCode == 4326: #Projected WGS_1984 tai GCS_WGS_1984
            Dtransform_method = "KKJ_To_WGS_1984_2_JHS153"
        elif DProj == "ETRS_198":
            Dtransform_method = "KKJ_To_ETRS_1989_2"
        else:
            virhe("Kohdepisteet tulee olla projisoituna johonkin seuraavista koordinaatistoista:")
            virhe("KKJ, EUREF_FIN, WGS_1984, ETRS_1989")
        
        env.workspace = temp
        if arcpy.Exists("DestinationsProj.shp"):
            arcpy.Delete_management("DestinationsProj.shp")

        arcpy.Project_management(Destinations, KohdePath, sr, Dtransform_method) #M��ritet��n Destinationit samaan koordinaatistoon
        Destinations = KohdePath
        msg("Kohdepaikkojen projektio vaihdettiin samaksi kuin Network Datalla. Luotiin kopio tiedostosta.")

    if NDProjektio != OFactCode: #Jos NetworkData ja kohdepisteet ovat eri KKJ:ssa projisoidaan ne samaan.
        if OFactCode >= 2391 and OFactCode <= 2394:
            Otransform_method = ""
        elif OProj == "WGS_1984" or OFactCode == 4326: #Projected WGS_1984 tai GCS_WGS_1984
            Otransform_method = "KKJ_To_WGS_1984_2_JHS153"
        elif OProj == "ETRS_198":
            Otransform_method = "KKJ_To_ETRS_1989_2"
        else:
            virhe("L�ht�pisteet tulee olla projisoituna johonkin seuraavista koordinaatistoista:")
            virhe("KKJ, EUREF_FIN, WGS_1984, ETRS_1989")

        env.workspace = temp
        if arcpy.Exists("OriginsProj.shp"):
            arcpy.Delete_management("OriginsProj.shp")
    
        arcpy.Project_management(Origins, LahtoPath, sr, Otransform_method) #M��ritet��n Destinationit samaan koordinaatistoon
        Origins = LahtoPath
        msg("L�ht�paikkojen projektio vaihdettiin samaksi kuin Network Datalla. Luotiin kopio tiedostosta.")

Valmis()
arcpy.SetProgressorPosition(35)
msg("----------------------")
    
#Tehd��n Feature Layerit spatiaalista valintaa varten:
Orig_lyr = "Orig_lyr"
Dest_lyr = "Dest_lyr"
OrigPath = Orig_lyr + ".lyr"
DestPath = Dest_lyr + ".lyr"

env.workspace = OrigKansio

if arcpy.Exists(Orig_lyr):   #Varmistetaan ettei FeatureLayeria ole jo olemassa
    arcpy.Delete_management(Orig_lyr)
    msg("Poistettiin vanha Feature Layer")

env.workspace = DestKansio

if arcpy.Exists(Dest_lyr):   #Varmistetaan ettei FeatureLayeria ole jo olemassa
    arcpy.Delete_management(Dest_lyr)
    msg("Poistettiin vanha Feature Layer")
    
arcpy.MakeFeatureLayer_management(Origins, Orig_lyr, "", OrigKansio)
arcpy.MakeFeatureLayer_management(Destinations, Dest_lyr, "", DestKansio)

#Valitaan kohteet, jotka ovat kantakaupungin sis�ll�:
arcpy.SelectLayerByLocation_management(Orig_lyr, "INTERSECT", Kantakaupunki, "", "NEW_SELECTION")
arcpy.SelectLayerByLocation_management(Dest_lyr, "INTERSECT", Kantakaupunki, "", "NEW_SELECTION")

#Lasketaan aika ja matka l�ht�paikasta parkkipaikalle/parkkipaikalta kohteeseen kantakaupungin alueella:

msg("Lasketaan aika ja matka l�ht�paikasta parkkipaikalle/parkkipaikalta kohteeseen kantakaupungin alueella")
arcpy.ResetProgressor()
arcpy.SetProgressor("step", "KOKONAISMATKAKETJUN LASKENTA...Lasketaan aika ja matka l�ht�paikasta parkkipaikalle/parkkipaikalta kohteeseen kantakaupungin alueella...", 0, 100, 5)
arcpy.SetProgressorPosition(40)
Aloitus()

OrigReader = arcpy.UpdateCursor(Orig_lyr)
DestReader = arcpy.UpdateCursor(Dest_lyr)

for row in OrigReader:
    row.Kavely_T_P = 180 / Kavelynopeus
    row.KavelMatkO = 180
    OrigReader.updateRow(row)
    del row

for row in DestReader:
    row.Kavely_P_T = 180 / Kavelynopeus
    row.KavelMatkD = 180
    DestReader.updateRow(row)
    del row

del OrigReader
del DestReader

Valmis()
arcpy.SetProgressorPosition(40)
msg("----------------------")

#Vaihdetaan valinta kantakaupungin ulkopuolisille alueille:

arcpy.SelectLayerByAttribute_management(Orig_lyr, "SWITCH_SELECTION", "")
arcpy.SelectLayerByAttribute_management(Dest_lyr, "SWITCH_SELECTION", "")

#Lasketaan aika ja matka l�ht�paikasta parkkipaikalle/parkkipaikalta kohteeseen kantakaupungin ulkopuolella:

msg("Lasketaan aika ja matka l�ht�paikasta parkkipaikalle/parkkipaikalta kohteeseen kantakaupungin ulkopuolella")
arcpy.SetProgressorLabel("KOKONAISMATKAKETJUN LASKENTA...Lasketaan aika ja matka l�ht�paikasta parkkipaikalle/parkkipaikalta kohteeseen kantakaupungin ulkopuolella...")
Aloitus()

OrigReader = arcpy.UpdateCursor(Orig_lyr)
DestReader = arcpy.UpdateCursor(Dest_lyr)

for row in OrigReader:
    row.Kavely_T_P = 135 / Kavelynopeus
    row.KavelMatkO = 135
    OrigReader.updateRow(row)
    del row

for row in DestReader:
    row.Kavely_P_T = 135 / Kavelynopeus
    row.KavelMatkD = 135
    DestReader.updateRow(row)
    del row

del OrigReader
del DestReader

#Poistetaan valinnat:
arcpy.SelectLayerByAttribute_management(Orig_lyr, "CLEAR_SELECTION", "")
arcpy.SelectLayerByAttribute_management(Dest_lyr, "CLEAR_SELECTION", "")

#Tarkistetaan onko aiempia OD-Cost-Matrixeja ja luodaan uniikki nimi:
env.workspace = temp
ODnimi = "Kokonaismatkaketju_ODC_MATRIX"
ODPath = ODnimi + ".lyr"

if arcpy.Exists(ODnimi):
    arcpy.Delete_management(ODnimi)
    msg("Poistettiin vanha OD Cost Matrix")
    
Valmis()
arcpy.SetProgressorPosition(45)
msg("----------------------")

#Tehd��n OD Cost Matrix Layer:
msg("Tehd��n OD Cost Matrix Layer")
arcpy.SetProgressorLabel("KOKONAISMATKAKETJUN LASKENTA...Tehd��n OD-Cost-Matrix Layer...")
Aloitus()

if Grafiikka == "true" or "True":
    GrafOut = "STRAIGHT_LINES"
else:
    GrafOut = "NO_LINES"

if "Hierarkia" in NDparams:
    Hierarkia = "USE_HIERARCHY"
else:
    Hierarkia = "NO_HIERARCHY"

arcpy.MakeODCostMatrixLayer_na(NetworkData, ODnimi, Impedanssi, "", LaskKohteet, Accumulation, "ALLOW_DEAD_ENDS_ONLY", "", Hierarkia, "", GrafOut)

#Lis�t��n OD cost matrix Locationit ja m��ritet��n parametrit:
msg("Lis�t��n OD cost matrix Locationit")
Aloitus()

Lahtopaikat = Orig_lyr
Kohdepaikat = Dest_lyr

arcpy.SetProgressorLabel("KOKONAISMATKAKETJUN LASKENTA...Lis�t��n OD-cost-matrix L�ht�paikat...T�ss� menee hetki...")                                                                            
arcpy.AddLocations_na(ODnimi, "Origins", Lahtopaikat, "Name NameO #", "5000 Meters", "", "", "MATCH_TO_CLOSEST", "APPEND", "NO_SNAP", "", "EXCLUDE", "")
arcpy.SetProgressorPosition(55)
arcpy.SetProgressorLabel("KOKONAISMATKAKETJUN LASKENTA...Lis�t��n OD-cost-matrix Kohdepaikat...T�ss� menee hetki...") 
arcpy.AddLocations_na(ODnimi, "Destinations", Kohdepaikat, "Name NameD #", "5000 Meters", "", "", "MATCH_TO_CLOSEST", "APPEND", "NO_SNAP", "", "EXCLUDE", "")

arcpy.SetProgressorPosition(65)
Valmis()
msg("----------------------")

#Suoritetaan OD cost matrix laskenta:
msg("Suoritetaan OD-cost-matrix laskenta")
arcpy.SetProgressorLabel("KOKONAISMATKAKETJUN LASKENTA...Suoritetaan OD-cost-matrix laskenta...") 
Aloitus()

arcpy.Solve_na(ODnimi, "SKIP", "TERMINATE")
Valmis()
arcpy.SetProgressorPosition(70)
msg("----------------------")

#Valitaan muokattavaksi OD C M:n Lines layer:
arcpy.SelectData_management(ODnimi, "Lines")

Lines = ODnimi + "/" + "Lines"

#Lis�t��n Lines_lyr:iin tarvittavat kent�t Joinin mahdollistamiseksi:
arcpy.AddFieldToAnalysisLayer_na(ODnimi, "Lines", "LahtoNimi", "TEXT")
arcpy.AddFieldToAnalysisLayer_na(ODnimi, "Lines", "KohdeNimi", "TEXT")

#Muodostetaan Joinin id-kent�t:

arcpy.CalculateField_management(Lines, "LahtoNimi", "!Name!.split(\" -\")[0]", "PYTHON_9.3")
arcpy.CalculateField_management(Lines, "KohdeNimi", "!Name!.split(\"- \")[1]", "PYTHON_9.3")

#Eksportataan Line-feature shapeksi, jotta Join saadaan toimimaan:

OutLineNimi = "KokonaismatkaLines.shp"

env.workspace = OrigKansio
if arcpy.Exists(OutLineNimi):
    unique = arcpy.CreateUniqueName(OutLineNimi)
    OutLines = unique
    Outnimi = string.split(unique, ".")[0]
else:
    OutLines = OutLineNimi
    Outnimi = "KokonaismatkaLines"
    
arcpy.Select_analysis(Lines, OutLines)
    
#Tehd��n Join L�ht�pisteiden/Kohdepisteiden ja Lines_lyr:in v�lill�:
msg("Tehd��n Join L�ht�pisteiden/Kohdepisteiden ja KokonaismatkaLines:in v�lill�")
Aloitus()

arcpy.JoinField_management(OutLines, "LahtoNimi", Origins, "NameO", ["Kavely_O_T", "KavelDistO", "Kavely_T_P", "KavelMatkO", "Digiroa_aa", "Kokopva_aa", "Keskpva_aa", "Ruuhka_aa"]) 
arcpy.JoinField_management(OutLines, "KohdeNimi", Destinations, "NameD", ["Kavely_T_D", "KavelDistD", "Kavely_P_T", "KavelMatkD", "Parkkiaika"])

Valmis()
arcpy.SetProgressorPosition(75)
msg("----------------------")

#Lis�t��n Lines tauluun tarvittavat kent�t Kokonaismatkaketjun laskentoja varten & Tehd��n Kokonaismatkaketjun laskenta:
msg("Suoritetaan Kokonaismatkaketjun laskenta")
arcpy.SetProgressorLabel("KOKONAISMATKAKETJUN LASKENTA...Suoritetaan Kokonaismatkaketjun laskenta...") 
Aloitus()

if "Digiroa_aa" in Accumulation:
    arcpy.AddField_management(OutLines, "TotDigiroa", "DOUBLE")
    arcpy.CalculateField_management(OutLines, "Digiroa_aa", "[Total_Digi]", "VB", "")
    arcpy.CalculateField_management(OutLines, "TotDigiroa", "[Kavely_O_T] + [Kavely_T_P] + [Digiroa_aa] + [Parkkiaika] + [Kavely_P_T] + [Kavely_T_D] ", "VB", "")
    
if "Kokopva_aa" in Accumulation:
    arcpy.AddField_management(OutLines, "TotKokopva", "DOUBLE")
    arcpy.CalculateField_management(OutLines, "Kokopva_aa", "[Total_Koko]", "VB", "")
    arcpy.CalculateField_management(OutLines, "TotKokopva", "[Kavely_O_T] + [Kavely_T_P] + [Kokopva_aa] + [Parkkiaika] + [Kavely_P_T] + [Kavely_T_D] ", "VB", "")

arcpy.SetProgressorPosition(80)
    
if "Keskpva_aa" in Accumulation:
    arcpy.AddField_management(OutLines, "TotKeskpva", "DOUBLE")
    arcpy.CalculateField_management(OutLines, "Keskpva_aa", "[Total_Kesk]", "VB", "")
    arcpy.CalculateField_management(OutLines, "TotKeskpva", "[Kavely_O_T] + [Kavely_T_P] + [Keskpva_aa] + [Parkkiaika] + [Kavely_P_T] + [Kavely_T_D] ", "VB", "")
    
if "Ruuhka_aa" in Accumulation:
    arcpy.AddField_management(OutLines, "TotRuuhka", "DOUBLE")
    arcpy.CalculateField_management(OutLines, "Ruuhka_aa", "[Total_Ruuh]", "VB", "")
    arcpy.CalculateField_management(OutLines, "TotRuuhka", "[Kavely_O_T] + [Kavely_T_P] + [Ruuhka_aa] + [Parkkiaika] + [Kavely_P_T] + [Kavely_T_D] ", "VB", "")

arcpy.SetProgressorPosition(85)

#Seuraavaan pit�� viel� selvitt�� kuinka pitk� matka kuljetaan keskim��rin kun haetaan parkkipaikkaa (Nyt k�yt�ss� 20 kilometri� tunnissa)
if "Pituus" in Accumulation: #Lasketaan kokonaismatka ja siirret��n attribuutit loogisesti taulun loppuun
    arcpy.AddField_management(OutLines, "Pituus_O_T", "DOUBLE")
    arcpy.AddField_management(OutLines, "Pituus_T_P", "DOUBLE")
    arcpy.AddField_management(OutLines, "Pituus_Ajo", "DOUBLE")
    arcpy.AddField_management(OutLines, "Pituus_P_E", "DOUBLE")
    arcpy.AddField_management(OutLines, "Pituus_P_T", "DOUBLE")
    arcpy.AddField_management(OutLines, "Pituus_T_D", "DOUBLE")
    arcpy.AddField_management(OutLines, "Pituus_TOT", "DOUBLE")
    arcpy.CalculateField_management(OutLines, "Pituus_O_T", "[KavelDistO]", "VB", "")
    arcpy.CalculateField_management(OutLines, "Pituus_T_P", "[KavelMatkO]", "VB", "")
    arcpy.CalculateField_management(OutLines, "Pituus_Ajo", "[Total_Pitu]", "VB", "")
    arcpy.CalculateField_management(OutLines, "Pituus_P_E", "(([Parkkiaika] / 60) / 20) * 1000", "VB", "")
    arcpy.CalculateField_management(OutLines, "Pituus_P_T", "[KavelMatkD]", "VB", "")
    arcpy.CalculateField_management(OutLines, "Pituus_T_D", "[KavelDistD]", "VB", "")
    arcpy.CalculateField_management(OutLines, "Pituus_TOT", "[Pituus_O_T] + [Pituus_T_P] + [Pituus_Ajo] + [Pituus_P_E] + [Pituus_P_T] + [Pituus_T_D] ", "VB", "")

#Impedanssi l�ytyy aina taulusta eli pit�� tsekata ettei tehd� t�t� laskentaa toistamiseen!    
if Impedanssi in Accumulation:
    if Impedanssi == "Digiroa_aa":
        True
    elif Impedanssi == "Kokopva_aa":
        True
    elif Impedanssi == "KokoPva_aa":
        True
    elif Impedanssi == "Keskpva_aa":
        True
    elif Impedanssi == "Ruuhka_aa":
        True
    else:
        ImpedLyh = Impedanssi[:4] #Impedanssista otetaan vain 4 ensimm�ist� kirjainta
        Laskukaava = "[Kavely_O_T] + [Kavely_T_P] + [Total_" + ImpedLyh + "] + [Parkkiaika] + [Kavely_P_T] + [Kavely_T_D] "
        arcpy.AddField_management(OutLines, Impedanssi, "DOUBLE")
        arcpy.CalculateField_management(OutLines, Impedanssi, Laskukaava, "VB", "")
        msg("Laskettiin kokonaismatkaketju perustuen k�ytt�j�n itsem��rittelem��n impedanssiin.")

#Poistetaan turhat kent�t tiedostosta:
arcpy.DeleteField_management(OutLines, ["OriginID", "Destinatio", "Destinat_1", "KavelDistO", "KavelMatkO", "KavelMatkD", "KavelDistD", "Total_Digi","Total_Koko","Total_Kesk","Total_Ruuh", "Total_Pitu"])

Valmis()
arcpy.SetProgressorPosition(90)
msg("----------------------")


#Lis�t��n tulokset kartalle

msg("Lis�t��n tulos kartalle")
arcpy.SetProgressorLabel("KOKONAISMATKAKETJUN LASKENTA...Lis�t��n tulos kartalle...") 
Aloitus()

arcpy.MakeFeatureLayer_management(OutLines, Outnimi, "", OrigKansio)
AddLyr = arcpy.mapping.Layer(OutLines)
AddLayerToMap(AddLyr)

Valmis()
arcpy.SetProgressorPosition(95)
msg("----------------------")
#Poistetaan v�liaikaistiedostot:
env.workspace = temp
if arcpy.Exists("DestinationsProj.shp"):
    arcpy.Delete_management(KohdePath)
if arcpy.Exists("OriginsProj.shp"):
    arcpy.Delete_management(LahtoPath)
if arcpy.Exists("KantisProj.shp"):
    arcpy.Delete_management(KantisPath)

arcpy.SetProgressorPosition(100)
msg("VALMIS! NYT VOIT HALUTESSASI EXPORTOIDA TULOKSET KOKONAISMATKALINESin KAUTTA!")
msg("Avainpari KokonaisMatkaLinesin ja L�ht�paikkojen v�lill�: LahtoNimi - NameO")
msg("Avainpari KokonaisMatkaLinesin ja Kohdepaikkojen v�lill�: Kohdenimi - NameD")
msg("----------------------")
