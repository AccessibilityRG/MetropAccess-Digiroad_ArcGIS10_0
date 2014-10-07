# -*- coding: iso-8859-1 -*-
#------------------------------
# METROPACCESS-DIGIROAD
# MetropAccess-tutkimushanke
# HELSINGIN YLIOPISTO
# Koodi: Henrikki Tenkanen
#-------------------------------
# 3. Aikasakkojen laskenta
#-------------------------------

####################################################################################
#MetropAccess-Digiroad, työkalu Digiroad-aineiston muokkaukseen MetropAccess-hankkeen menetelmän mukaisesti
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
import os
import sys
import time
import string

# Tarkistetaan tarvittavat Lisenssit
arcpy.CheckOutExtension("Network")

#METODIT:

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

def ExDel(haettava):
    if arcpy.Exists(haettava):
        arcpy.Delete_management(haettava)

#---------------------------------
# Tarvittavat tiedostot ja työskentelyhakemistot:
NetworkData = arcpy.GetParameterAsText(0)
Workspace = arcpy.GetParameterAsText(1)

#Parsitaan loppujen tarvittavien tiedostojen nimet ja sijainti:
desc = arcpy.Describe(NetworkData)
NDPath = desc.path
LiikenneElementit = NDPath + "\\" + desc.edgeSources[0].name + ".shp" #Parsitaan Liikenne_Elementti -tiedoston polku ja nimi
LiikenneJunctions = NDPath + "\\" + desc.junctionSources[0].name + ".shp" #Parsitaan Junctions -tiedoston polku ja nimi
#--------------------------------

if os.path.isfile(LiikenneJunctions) == False: #Tarkistetaan, että Junctions.shp tiedosto löytyy
    teksti = "Tiedostoa " + LiikenneJunctions + " ei löydy! Tarkista, että kansiosta, jossa sijaitsee käyttämäsi Network Dataset löytyy myös pistetiedosto seuraavassa kirjoitusmuodossa: '<NimeämäsiNetworkDataset>_ND_Junctions.shp'."
    virhe(teksti)

#Määritetään Scratchworkspace:
temp = arcpy.GetSystemEnvironment("TEMP")
env.workspace = temp

Liikennevalosegmentti = "Liikennevalosegmentti.shp"
if arcpy.Exists(Liikennevalosegmentti): #Tarkistetaan, että Liikennevalosegmentti.shp tiedosto löytyy
    Liikennevalosegmentti = temp + "\\" + "Liikennevalosegmentti.shp"
else:
    teksti = "Tarvittavaa tiedostoa 'Liikennevalosegmentti.shp' ei löydy! Suorita 1. työvaihe uudelleen tai siirrä Liikennevalosegmentti-tiedosto temp-kansioon ja palaa sen jälkeen suorittamaan tämä työvaihe."
    tempSijainti = "Temp kansiosi on: " + temp
    arcpy.AddError(teksti)
    arcpy.AddError(tempSijainti)
    sys.exit()
    
#Katsotaan NetworkDatan attribuutit:
attributes = desc.attributes
NDparams = []
for attribute in attributes:
    NDparams.append(attribute.name)
del desc
del attributes

#-----------------------------------------------------
#Katsotaan Liikenne_Elementti -tiedoston attribuutit:
LEparams = [f.name for f in arcpy.ListFields(LiikenneElementit)]

#Tarkistetaan, että tarvittavat muuttujat löytyvät Liikenne_elementti -tiedostosta:
if not "Pituus" in LEparams:
    virhe("Attribuuttia 'Pituus' ei löydy käytettävästä Liikenne_Elementti.shp tiedostosta. Tarkista, että tie-elementin pituuden määrittävä attribuutti on nimetty nimellä 'Pituus'")
if not "KmH" in LEparams:
    virhe("Attribuuttia 'KmH' ei löydy käytettävästä Liikenne_Elementti.shp tiedostosta. Tarkista, attribuutti on nimetty kirjoitusasulla 'KmH'")    
if not "Digiroa_aa" in LEparams:
    virhe("Attribuuttia 'Digiroa_aa' ei löydy käytettävästä Liikenne_Elementti.shp tiedostosta. Tarkista, että attribuutti on nimetty kirjoitusasulla 'Digiroa_aa'")
if "KokoPva_aa" or "Kokopva_aa" in LEparams:
    True
else:
    virhe("Attribuuttia 'Kokopva_aa' ei löydy käytettävästä Liikenne_Elementti.shp tiedostosta. Tarkista, että attribuutti on nimetty kirjoitusasulla 'Kokopva_aa'")
if not "Keskpva_aa" in LEparams:
    virhe("Attribuuttia 'Keskpva_aa' ei löydy käytettävästä Liikenne_Elementti.shp tiedostosta. Tarkista, että attribuutti on nimetty kirjoitusasulla 'Keskpva_aa'")
if not "Ruuhka_aa" in LEparams:
    virhe("Attribuuttia 'Ruuhka_aa' ei löydy käytettävästä Liikenne_Elementti.shp tiedostosta. Tarkista, että attribuutti on nimetty kirjoitusasulla 'Ruuhka_aa'")


#Tarkistetaan, että tarvittavat muuttujat löytyvät Network Datasetistä:
if not "Pituus" in NDparams:
    virhe("Attribuuttia 'Pituus' ei löydy käytettävästä Network Datasetistä. Tarkista, että tie-elementin pituuden määrittävä attribuutti on nimetty nimellä 'Pituus'")
if not "Digiroa_aa" in NDparams:
    virhe("Attribuuttia 'Digiroa_aa' ei löydy käytettävästä Network Datasetistä. Tarkista, että attribuutti on nimetty kirjoitusasulla 'Digiroa_aa'")
if "KokoPva_aa" or "Kokopva_aa" in NDparams:
    True
else:
    virhe("Attribuuttia 'Kokopva_aa' ei löydy käytettävästä Network Datasetistä. Tarkista, että attribuutti on nimetty kirjoitusasulla 'Kokopva_aa'")
if not "Keskpva_aa" in NDparams:
    virhe("Attribuuttia 'Keskpva_aa' ei löydy käytettävästä Network Datasetistä. Tarkista, että attribuutti on nimetty kirjoitusasulla 'Keskpva_aa'")
if not "Ruuhka_aa" in NDparams:
    virhe("Attribuuttia 'Ruuhka_aa' ei löydy käytettävästä Network Datasetistä. Tarkista, että attribuutti on nimetty kirjoitusasulla 'Ruuhka_aa'")

#--------------------------------------------------
#TARKISTETAAN PROJEKTIO
#--------------------------------------------------

desc = arcpy.Describe(LiikenneElementit)
Projektio = desc.spatialReference.factoryCode
if Projektio == 3067 or Projektio == 2391 or Projektio == 2392 or Projektio == 2393 or Projektio == 2394 or Projektio == 104129:
    msg("Tarkistettiin liikenneverkon projektio.")
else:
    virhe("Tieverkkoaineiston tulee olla projisoituna joko EUREF_FIN_TM35FIN:iin, GCS_EUREF_FIN:iin tai Finland_Zone_1, 2, 3 tai -4:ään (KKJ). Muuta Liikenne_elementti.shp projektio johonkin näistä Project -työkalulla, luo uusi Network Dataset perustuen tähän uuteen projisoituun LiikenneElementti -tiedostoon ja aja työkalu uudelleen.")

del desc
#--------------------------------------------------

msg("------------------------------")
msg("METROPACCESS-DIGIROAD")
msg("MetropAccess-tutkimushanke")
msg("HELSINGIN YLIOPISTO")
msg("-------------------------------")
msg("3. Aikasakkojen Laskenta")
msg("-------------------------------")

time.sleep(2.5)
#------------------------------------------------------------------------------------------------------------------------------
#MUODOSTETAAN LIIKENNEVALOPISTEET ODC:LLA (CutOff 20 metriä)
#------------------------------------------------------------------------------------------------------------------------------
msg("Määritetään tie-elementit, joihin vaikuttaa liikennevalot")
Aloitus()
arcpy.SetProgressor("step", "AIKASAKKOJEN LASKENTA...Määritetään tie-elementit, joihin vaikuttavat liikennevalot...", 0, 100, 10) #Luodaan suoritusinfopalkki

#Tehdään Liikennevalosegmenteistä pistemuotoinen:
LVSpoint = "LiikennevaloSegmenttiPoint.shp"
ExDel(LVSpoint)
arcpy.FeatureToPoint_management(Liikennevalosegmentti, LVSpoint, "CENTROID")
arcpy.SetProgressorPosition(5)

#Haetaan Near analyysilla Junction-pisteistä sellaiset kohteet, jotka ovat 20 metrin sisällä Liikennevaloista (jotta saadaan Destination pisteiden määrää pienennettyä ODC:hen)
arcpy.Near_analysis(LiikenneJunctions, LVSpoint, "20 Meters", "NO_LOCATION", "NO_ANGLE")

#Tehdään tästä Feature-Layer:
LVJ = "LiikennevalojenLaheisyydessaOlevatJunctionit"
ExDel(LVJ) #Tarkistetaan päällekkäisyys
arcpy.MakeFeatureLayer_management(LiikenneJunctions, LVJ, """NEAR_FID <> -1""", "")

arcpy.SetProgressorPosition(10)

ODC = "KAIKKILiikenneValot"
ExDel(ODC)

if "Hierarkia" in NDparams:
    Hierarkia = "USE_HIERARCHY"
else:
    Hierarkia = "NO_HIERARCHY"


#Tehdään OD-Cost-Matrix Layer ja LASKETAAN VAIN kohteet, jotka ovat 20 metrin päässä Origineista:
msg("Luodaan ODC-Cost-Matrix. Haetaan tie-elementit 20m liikennevaloista.")
Aloitus()
arcpy.SetProgressor("step", "Luodaan OD-Cost-Matrix...Haetaan tie-elementit 20m liikennevaloista...", 0, 100, 25) #Luodaan suoritusinfopalkki
arcpy.MakeODCostMatrixLayer_na(NetworkData, ODC, "Pituus", "20", "", "", "ALLOW_DEAD_ENDS_ONLY", "", Hierarkia, "", "STRAIGHT_LINES")
arcpy.SetProgressorPosition(25)
Valmis()

#Origineiksi määritellään Liikennevalosegmentit(pistemuotoisena):
msg("Lisätään OD-Cost-Matriisiin Lähtöpisteet")
Aloitus()
arcpy.SetProgressorLabel("Lisätään OD-Cost-Matriisiin Lähtöpisteet...Tässä menee hetki...")
arcpy.AddLocations_na(ODC, "Origins", LVSpoint, "Name FID #", "10 Meters", "", "", "MATCH_TO_CLOSEST", "CLEAR", "NO_SNAP", "5 Meters", "EXCLUDE", "")
arcpy.SetProgressorPosition(50)
Valmis()

#Destinationeiksi määritellään kaikki Junctionit, jotka ovat 20 metrin päässä LiikennevaloSegmenteistä:
msg("Lisätään OD-Cost-Matriisiin Kohdepisteet")
Aloitus()
arcpy.SetProgressorLabel("Lisätään OD-Cost-Matriisiin Kohdepisteet...Tässä menee hetki...")
arcpy.AddLocations_na(ODC, "Destinations", LVJ, "Name FID #", "10 Meters", "", "", "MATCH_TO_CLOSEST", "APPEND", "NO_SNAP", "5 Meters", "EXCLUDE", "")
arcpy.SetProgressorPosition(75)
Valmis()

#Suoritetaan ODC:
msg("Suoritetaan OD-Cost-Matrix")
Aloitus()
arcpy.SetProgressorLabel("Solve...")
arcpy.Solve_na(ODC, "SKIP", "TERMINATE")


#Luodaan kansio LiikenneElementeille (luodaan uniikki jos kansio jo löytyy Workspacesta):
directory = Workspace + "\\LiikenneElementit"
unique = "LiikenneElementit"

if os.path.isdir(directory) == True:
    unique = arcpy.CreateUniqueName(directory)
    os.makedirs(unique)
    Workspace = unique
else:
    os.makedirs(directory)
    Workspace = directory

#Määritetään ODC-Layer:
Lines = ODC + "/" + "Lines"

env.workspace = Workspace #Määritetään työskentelyhakemisto

LV = "Liikennevalot.shp"
ExDel(LV)
arcpy.SpatialJoin_analysis(LVJ, Lines, LV, "JOIN_ONE_TO_ONE", "KEEP_COMMON", "", "INTERSECT")


#Tehdään myöhemmin tarvittava FeatureLayer:
LVF = "LiikenneValoFeat"
ExDel(LVF)
arcpy.MakeFeatureLayer_management(LV, LVF, "", "")

arcpy.SetProgressorPosition(100)
msg("Liikennevalot määritetty!")
Valmis()
msg("----------------------")
arcpy.ResetProgressor()

arcpy.SetProgressor("step", "AIKASAKKOJEN LASKENTA...Määritetään rampit...", 0, 100, 10)
arcpy.SetProgressorPosition(40)

#------------------------------------------------------------------------------------------------------------------------------
#MUODOSTETAAN MUUNTYYPPISET LIIKENNE-ELEMENTIT (Rampit, Kevyen Liikenteen risteykset, Tavalliset Risteykset)
#------------------------------------------------------------------------------------------------------------------------------
env.workspace = temp

#Valitaan sellaiset Junctionit jotka ovat risteyksiä:
NDJunct = "NDJunct.shp"
ExDel(NDJunct) #Tarkistetaan päällekkäisyys
arcpy.SpatialJoin_analysis(LiikenneJunctions, LiikenneElementit, NDJunct, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "INTERSECT", "", "")
arcpy.SetProgressorPosition(45)

Risteys = "Risteys"
ExDel(Risteys) #Tarkistetaan päällekkäisyys
arcpy.MakeFeatureLayer_management(NDJunct, Risteys, """Join_Count > 2""", "")

#------------------------------------------------------------------------------------------------------------------------------
#MUODOSTETAAN RAMPIT

msg("Määritetään rampit")
Aloitus()

#Valitaan Liikenne-Elementeistä segmentit, jotka ovat tyyppiä Ramppi (DynTyyppi == 8)
RampitS = "RamppiSegmentti"
ExDel(RampitS)
arcpy.MakeFeatureLayer_management(LiikenneElementit, RampitS, """DynTyyppi = 8""", "")
arcpy.SetProgressorPosition(50)
#Haetaan Tavallisista Risteyksistä ne pisteet, jotka ovat ramppeja:
env.workspace = Workspace
Rampit = "Rampit.shp"
ExDel(Rampit)
arcpy.SpatialJoin_analysis(Risteys, RampitS, Rampit, "JOIN_ONE_TO_ONE", "KEEP_COMMON", "", "INTERSECT", "", "")

msg("Rampit määritetty!")
arcpy.SetProgressorPosition(55)
Valmis()
msg("----------------------")
#------------------------------------------------------------------------------------------------------------------------------
#MUODOSTETAAN KEVYENLIIKENTEEN RISTEYKSET

msg("Määritetään Kevyenliikenteen risteykset")
arcpy.SetProgressorLabel("AIKASAKKOJEN LASKENTA...Määritetään Kevyenliikenteen risteykset...")
Aloitus()

env.workspace = temp
KevytLS = "KevyenLiikenteenSegmentti"
ExDel(KevytLS)
arcpy.MakeFeatureLayer_management(LiikenneElementit, KevytLS, """TOIMINNALL = 10""", "")
arcpy.SetProgressorPosition(60)

env.workspace = Workspace
KevytL = "KevytLiikenne.shp"
ExDel(KevytL)
arcpy.SpatialJoin_analysis(Risteys, KevytLS, KevytL, "JOIN_ONE_TO_ONE", "KEEP_COMMON", "", "INTERSECT", "", "")

msg("Kevyenliikenteen risteykset määritetty!")
arcpy.SetProgressorPosition(65)
Valmis()
msg("----------------------")

#------------------------------------------------------------------------------------------------------------------------------

#MUODOSTETAAN TAVALLISET RISTEYKSET

msg("Määritetään tavalliset risteykset")
arcpy.SetProgressorLabel("AIKASAKKOJEN LASKENTA...Määritetään tavalliset risteykset...")
Aloitus()

#Valitaan Risteyksistä, pisteet jotka eivät ole Liikennevalollisia:
arcpy.SelectLayerByLocation_management(Risteys, "INTERSECT", LVF)
#Tehdään Switch:
arcpy.SelectLayerByAttribute_management(Risteys, "SWITCH_SELECTION")

#Tehdään tästä oma tiedosto:
TVR1F = "TavallisetRisteyksetF1"
ExDel(TVR1F)
arcpy.MakeFeatureLayer_management(Risteys, TVR1F, "", "")

#............................

#Valitaan näistä, pisteet jotka eivät ole ramppeja:
arcpy.SelectLayerByLocation_management(TVR1F, "INTERSECT", Rampit)
#Tehdään Switch:
arcpy.SelectLayerByAttribute_management(TVR1F, "SWITCH_SELECTION")

#Tehdään tästä oma tiedosto:
TVR2F = "TavallisetRisteyksetF2"
ExDel(TVR2F)
arcpy.MakeFeatureLayer_management(TVR1F, TVR2F, "", "")
arcpy.SetProgressorPosition(70)
#.............................

#Valitaan näistä, pisteet jotka eivät ole Kevyen Liikenteen risteyksiä:
arcpy.SelectLayerByLocation_management(TVR2F, "INTERSECT", KevytL)
#Tehdään Switch:
arcpy.SelectLayerByAttribute_management(TVR2F, "SWITCH_SELECTION")

#Tehdään tästä oma tiedosto:
TVR3F = "TavallisetRisteyksetF3"
ExDel(TVR3F)
arcpy.MakeFeatureLayer_management(TVR2F, TVR3F, "", "")

#............................

#MUODOSTETAAN TAVALLISET RISTEYKSET LAYER WORKSPACEEN
env.workspace = Workspace
TVR = "TavallisetRisteykset.shp"
ExDel(TVR)
arcpy.Select_analysis(TVR3F, TVR)

msg("Tavalliset risteykset määritetty!")
arcpy.SetProgressorPosition(75)
Valmis()
msg("----------------------")
#Poistetaan turhat tiedostot joita on tähän mennessä syntynyt:
ExDel(ODC)
ExDel(LVJ)
ExDel(LVSpoint)
ExDel(LVF)
ExDel(NDJunct)
ExDel(Risteys)
ExDel(RampitS)
ExDel(KevytLS)
ExDel(TVR1F)
ExDel(TVR2F)
ExDel(TVR3F)

#------------------------------------------------------------------------------------------------------------------------------
#LASKETAAN LIIKENNE-ELEMENTEILLE TIEDOT SIITÄ, MINKÄTYYPPISIÄ RISTEYKSIÄ KUHUNKIN ELEMENTTII KOHDISTUU
#------------------------------------------------------------------------------------------------------------------------------

msg("Määritetään tie-elementeille tieto siitä, minkätyyppisiä risteyksiä kuhunkin tie-elementtiin kohdistuu")
arcpy.SetProgressorLabel("AIKASAKKOJEN LASKENTA...Määritetään elementteihin kohdistuvat risteystyypit...")
Aloitus()

#Lisätään tarvittavat attribuutit:
arcpy.AddField_management(LiikenneElementit, "JuncType", "LONG")
arcpy.AddField_management(LiikenneElementit, "JuncType2", "LONG")
arcpy.AddField_management(LiikenneElementit, "JuncType3", "LONG")
arcpy.AddField_management(LiikenneElementit, "JuncType4", "LONG")
arcpy.AddField_management(LiikenneElementit, "JuncType5", "LONG")

#Tehdään LiikenneElementti FeatureLayer:
LEF = "LiikenneElementtiF"
ExDel(LEF)
arcpy.MakeFeatureLayer_management(LiikenneElementit, LEF, "", "")

#Määritetään Tie-Elementit, jotka ovat Liikennevalojen vaikutuksen alaisia:
arcpy.SelectLayerByLocation_management(LEF, "INTERSECT", LV, "", "NEW_SELECTION")
#Ei oteta Kevyen Liikenteen segmenttejä huomioon:
arcpy.SelectLayerByAttribute_management(LEF, "SUBSET_SELECTION", "\"TOIMINNALL\" <>10")
#Otetaan vain liikennevalosegmentit huomioon:
arcpy.SelectLayerByAttribute_management(LEF, "SUBSET_SELECTION", "\"DynTyyppi\" = 9") 
#Lasketaan JuncType arvoksi 1:
arcpy.CalculateField_management(LEF, "JuncType", "1", "VB")
arcpy.SetProgressorPosition(80)

#Määritetään Tie-Elementit, jotka ovat Tavallisten risteysten vaikutuksen alaisia:
arcpy.SelectLayerByLocation_management(LEF, "INTERSECT", TVR, "", "NEW_SELECTION")
#Ei oteta Kevyen Liikenteen segmenttejä huomioon:
arcpy.SelectLayerByAttribute_management(LEF, "SUBSET_SELECTION", "\"TOIMINNALL\" <>10")
#Lasketaan JuncType2 arvoksi 1:
arcpy.CalculateField_management(LEF, "JuncType2", "1", "VB")

#Määritetään Tie-Elementit, jotka ovat Ramppien vaikutuksen alaisia:
arcpy.SelectLayerByLocation_management(LEF, "INTERSECT", Rampit, "", "NEW_SELECTION")
#Otetaan vain TYYPPI = 8 huomioon(ramppi):
arcpy.SelectLayerByAttribute_management(LEF, "SUBSET_SELECTION", "\"TYYPPI\" =8")
#Lasketaan JuncType3 arvoksi 1:
arcpy.CalculateField_management(LEF, "JuncType3", "1", "VB")

#Määritetään Tie-Elementit, jotka ovat Kevyen Liikenteen väylien vaikutuksen alaisia:
arcpy.SelectLayerByLocation_management(LEF, "INTERSECT", KevytL, "", "NEW_SELECTION")
#Ei oteta Kevyen Liikenteen segmenttejä huomioon:
arcpy.SelectLayerByAttribute_management(LEF, "SUBSET_SELECTION", "\"TOIMINNALL\" <>10")
#Lasketaan JuncType4 arvoksi 1:
arcpy.CalculateField_management(LEF, "JuncType4", "1", "VB")


#LASKETAAN NÄMÄ KAIKKI YHTEEN
arcpy.CalculateField_management(LiikenneElementit, "JuncType5", "[JuncType] + [JuncType2] + [JuncType3] + [JuncType4]", "VB", "")

msg("Elementteihin kohdistuvat risteystyypit määritetty!")
arcpy.SetProgressorPosition(85)
Valmis()
msg("----------------------")
#------------------------------------------------------------------------------------------------------------------------------
#LASKETAAN LIIKENNE-ELEMENTEILLE AIKASAKOT
#------------------------------------------------------------------------------------------------------------------------------

msg("Lasketaan Liikenne-elementeille aikasakot")
arcpy.SetProgressorLabel("AIKASAKKOJEN LASKENTA...Lasketaan aikasakot...")
Aloitus()

#Aikasakot:
Keskiarvo12 = 11.311 / 60
Keskiarvo3 = 9.439 / 60
Keskiarvo456 = 9.362 / 60

Paiva12 = 9.979 / 60
Paiva3 = 6.650 / 60
Paiva456 = 7.752 / 60

Ruuhka12 = 12.195 / 60
Ruuhka3 = 11.199 / 60
Ruuhka456 = 10.633 / 60

#HUOM tyyppi = TYYPPI ei DynTyyppi

#Luodaan datan lukija
Reader = arcpy.UpdateCursor(LiikenneElementit)

#Järjestys pitää miettiä siten, että spesifit tulee ensin ja yleiset vasta myöhemmin!
for row in Reader:
#Elementit jotka ovat Toiminnallista luokkaa 1 tai 2:    
    if row.TOIMINNALL == 1 or row.TOIMINNALL == 2:
        if row.TYYPPI == 8:                                                #Lasketaan rampeille aikasakot
            if row.JuncType3 == 1 and row.KmH < 70 and row.JuncType5 != 2: # Alle 70 kmh tie-elementti leikkaa risteykseen
                row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo12/3)
                row.Keskpva_aa = row.Digiroa_aa + (Paiva12/3)
                row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka12/2)
            elif row.KmH >=70:                                             #Lasketaan kaikille rampeille mediaanihidastuvuus
                row.Kokopva_aa = row.Digiroa_aa * 1.884662
                row.Keskpva_aa = row.Digiroa_aa * 1.667750
                row.Ruuhka_aa = row.Digiroa_aa * 2.022762
            else:
                row.Kokopva_aa = row.Digiroa_aa + ((Keskiarvo12/3)*2)
                row.Keskpva_aa = row.Digiroa_aa + ((Paiva12/4)*4)
                row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka12/2)
        elif row.JuncType5 == 0 and row.KmH >= 70:                         #Lasketaan kaikille yli 70 kmh teille 1.1 tai 1.2 kerroin. Kannattaa tarvittaessa poistaa
            row.Kokopva_aa = row.Digiroa_aa * 1.1
            row.Keskpva_aa = row.Digiroa_aa
            row.Ruuhka_aa = row.Digiroa_aa * 1.2
        elif row.JuncType == 1 or row.JuncType5 ==2:                       #Liikennevaloristeyksille ja risteyksille, mihin leikkaa kaksi risteystä samassa tieluokassa aikasakko lasketaan aikasakko samaan tie-elementtiin 
            row.Kokopva_aa = row.Digiroa_aa + Keskiarvo12
            row.Keskpva_aa = row.Digiroa_aa + Paiva12
            row.Ruuhka_aa = row.Digiroa_aa + Ruuhka12
        elif row.TYYPPI == 4 and row.JuncType5 !=0:                        #Liikenneympyröissä sakotetaan vain 3/4, 2/3 tai 1/2 aikasakko
            row.Kokopva_aa = row.Digiroa_aa + ((Keskiarvo12/3)*2)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva12/2)
            row.Ruuhka_aa = row.Digiroa_aa + ((Ruuhka12/4)*3)
        elif row.JuncType3 == 1 and row.KmH < 70 and row.TYYPPI != 8 and row.JuncType5 != 2: #Tie-elementtiin, mikä liittyy toiseen tie-elementtini lasketaan 1/3 tai 1/2 aikasakko
            row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo12/3)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva12/4)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka12/2)
        elif row.JuncType2 == 1 or row.JuncType4 == 1 and row.JuncType5 != 2: #Normaalisti laskettavat risteykset
            row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo12/2)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva12/2)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka12/2)

        elif row.JuncType3 == 1 and row.KmH >= 70 and row.JuncType5 != 2:  #Yli 70 kmh teille leikkaavaan tie-elementtiin, mikä ei ole ramppi lasketaan 1/2, 1/3 tai 1/4 aikasakko
            row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo12/3)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva12/4)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka12/2)
        
        else:
            row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo12 / 4) 
            row.Keskpva_aa = row.Digiroa_aa + (Paiva12 / 4)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka12 / 4)
                    
#Elementit jotka ovat Toiminnallista luokkaa 3:        
    elif row.TOIMINNALL == 3:
        if row.TYYPPI == 8:                                                #Lasketaan rampeille aikasakot
            if row.JuncType3 == 1 and row.KmH < 70 and row.JuncType5 != 2: # Alle 70 kmh tie-elementti leikkaa risteykseen
                row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo3/3)
                row.Keskpva_aa = row.Digiroa_aa + (Paiva3/3)
                row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka3/2)
            elif row.KmH >=70:                                             #Lasketaan kaikille rampeille mediaanihidastuvuus
                row.Kokopva_aa = row.Digiroa_aa * 1.884662
                row.Keskpva_aa = row.Digiroa_aa * 1.667750
                row.Ruuhka_aa = row.Digiroa_aa * 2.022762
            else:
                row.Kokopva_aa = row.Digiroa_aa + ((Keskiarvo3/3)*2)
                row.Keskpva_aa = row.Digiroa_aa + ((Paiva3/4)*3)
                row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka3/2)
        elif row.JuncType5 == 0 and row.KmH >= 70:                         #Lasketaan kaikille yli 70 kmh teille 1.1 tai 1.2 kerroin. Kannattaa tarvittaessa poistaa
            row.Kokopva_aa = row.Digiroa_aa * 1.1
            row.Keskpva_aa = row.Digiroa_aa
            row.Ruuhka_aa = row.Digiroa_aa * 1.2
        elif row.JuncType == 1 or row.JuncType5 ==2:                       #Liikennevaloristeyksille ja risteyksille, mihin leikkaa kaksi risteystä samassa tieluokassa aikasakko lasketaan aikasakko samaan tie-elementtiin 
            row.Kokopva_aa = row.Digiroa_aa + Keskiarvo3
            row.Keskpva_aa = row.Digiroa_aa + Paiva3
            row.Ruuhka_aa = row.Digiroa_aa + Ruuhka3
        elif row.TYYPPI == 4 and row.JuncType5 !=0:                        #Liikenneympyröissä sakotetaan vain 3/4, 2/3 tai 1/2 aikasakko 
            row.Kokopva_aa = row.Digiroa_aa + ((Keskiarvo3/3)*2)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva3/2)
            row.Ruuhka_aa = row.Digiroa_aa + ((Ruuhka3/4)*3)
        elif row.JuncType3 == 1 and row.KmH < 70 and row.TYYPPI != 8 and row.JuncType5 != 2: #Tie-elementtiin, mikä liittyy toiseen tie-elementtini lasketaan 1/3 tai 1/2 aikasakko
            row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo3/3)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva3/4)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka3/2)
        elif row.JuncType2 == 1 or row.JuncType4 == 1 and row.JuncType5 != 2: #Normaalisti laskettavat risteykset
            row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo3/2)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva3/2)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka3/2)
        elif row.JuncType3 == 1 and row.KmH >= 70 and row.JuncType5 != 2:  #Yli 70 kmh teille leikkaavaan tie-elementtiin, mikä ei ole ramppi lasketaan 1/2, 1/3 tai 1/4 aikasakko
            row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo3/3)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva3/4)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka3/2)

        else:
            row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo3 / 4) 
            row.Keskpva_aa = row.Digiroa_aa + (Paiva3 / 4)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka3 / 4)
                
#Elementit jotka ovat Toiminnallista luokkaa 4,5 tai 6:
    elif row.TOIMINNALL == 4 or row.TOIMINNALL == 5 or row.TOIMINNALL == 6:
        if row.TYYPPI == 8:                                                #Lasketaan rampeille aikasakot
            if row.JuncType3 == 1 and row.KmH < 70 and row.JuncType5 != 2: # Alle 70 kmh tie-elementti leikkaa risteykseen
                row.Kokopva_aa = row.Digiroa_aa + ((Keskiarvo456/3)*2)
                row.Keskpva_aa = row.Digiroa_aa + ((Paiva456/3)*4)
                row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka456/2)
            elif row.KmH >=70:                                             #Lasketaan kaikille rampeille mediaanihidastuvuus
                row.Kokopva_aa = row.Digiroa_aa * 1.884662
                row.Keskpva_aa = row.Digiroa_aa * 1.667750
                row.Ruuhka_aa = row.Digiroa_aa * 2.022762
            else:
                row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo456/3)
                row.Keskpva_aa = row.Digiroa_aa + (Paiva456/4)
                row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka456/2)
        elif row.JuncType5 == 0 and row.KmH >= 70:                         #Lasketaan kaikille yli 70 kmh teille 1.1 tai 1.2 kerroin. Kannattaa tarvittaessa poistaa
            row.Kokopva_aa = row.Digiroa_aa * 1.1
            row.Keskpva_aa = row.Digiroa_aa
            row.Ruuhka_aa = row.Digiroa_aa * 1.2
        elif row.JuncType == 1 or row.JuncType5 ==2:                       #Liikennevaloristeyksille ja risteyksille, mihin leikkaa kaksi risteystä samassa tieluokassa aikasakko lasketaan aikasakko samaan tie-elementtiin 
            row.Kokopva_aa = row.Digiroa_aa + Keskiarvo456
            row.Keskpva_aa = row.Digiroa_aa + Paiva456
            row.Ruuhka_aa = row.Digiroa_aa + Ruuhka456
        elif row.TYYPPI == 4 and row.JuncType5 !=0:                        #Liikenneympyröissä sakotetaan vain 3/4, 2/3 tai 1/2 aikasakko
            row.Kokopva_aa = row.Digiroa_aa + ((Keskiarvo456/3)*2)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva456/2)
            row.Ruuhka_aa = row.Digiroa_aa + ((Ruuhka456/4)*3)
        elif row.JuncType3 == 1 and row.KmH < 70 and row.TYYPPI != 8 and row.JuncType5 != 2: #Tie-elementtiin, mikä liittyy toiseen tie-elementtini lasketaan 1/3 tai 1/2 aikasakko
            row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo456/3)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva456/4)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka456/2)
        elif row.JuncType2 == 1 or row.JuncType4 == 1 and row.JuncType5 != 2: #Normaalisti laskettavat risteykset
            row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo456/2)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva456/2)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka456/2)
        elif row.JuncType3 == 1 and row.KmH >= 70 and row.JuncType5 != 2:  #Yli 70 kmh teille leikkaavaan tie-elementtiin, mikä ei ole ramppi lasketaan 1/2, 1/3 tai 1/4 aikasakko
            row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo456/3)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva456/4)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka456/2)

        else:
            row.Kokopva_aa = row.Digiroa_aa  + (Keskiarvo456 / 4)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva456 / 4)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka456 / 4)


    else:                                                                  #Muille toiminnallisille luokille lasketaan nopeusrajoituksen mukainen läpiajoaika
        row.Kokopva_aa = row.Digiroa_aa
        row.Keskpva_aa = row.Digiroa_aa
        row.Ruuhka_aa = row.Digiroa_aa

        
    Reader.updateRow(row)
    del row
del Reader
###########################
arcpy.SetProgressorPosition(90)
#Poistetaan tiedostosta turhat kentät:
arcpy.DeleteField_management(LiikenneElementit, "JuncType;JuncType2;JuncType3;JuncType4;JuncType5;DynTyyppi")

msg("Aikasakot laskettu!")
arcpy.SetProgressorPosition(95)
Valmis()
msg("----------------------")
msg("Build Network Dataset")
arcpy.SetProgressorLabel("AIKASAKKOJEN LASKENTA...Build Network Dataset...")
Aloitus()
#Buildataan NetworkDataset uudestaan, jolloin se on heti valmis käytettäväksi:
arcpy.BuildNetwork_na(NetworkData)
Valmis()
arcpy.SetProgressorPosition(100)

msg("----------------------")
msg("VALMIS! Nyt käyttämääsi Network Datasettiin on laskettu todenmukaisemmat läpiajoajat sarakkeisiin: Kokopva_aa, Keskpva_aa sekä Ruuhka_aa.")
msg("Network Dataset on nyt valmis käytettäväksi reititysanalyyseihin.")
msg("Halutessasi voit suorittaa 4. työvaiheen, jossa otetaan matka-ajan lisäksi huomioon kävelyyn sekä parkkipaikan etsintään kuluva aika (Kokonaismatkaketju).")
msg("----------------------")
