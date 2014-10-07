# -*- coding: iso-8859-1 -*-
#------------------------------
# METROPACCESS-DIGIROAD
# MetropAccess-tutkimushanke
# HELSINGIN YLIOPISTO
# Koodi: Henrikki Tenkanen
#-------------------------------
# 5. Palvelualueen laskenta
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
import sys
import time
import string
import os

#Pametrit:
Facilities = arcpy.GetParameterAsText(0)
IndKohteet = arcpy.GetParameterAsText(1)
SortPlace = arcpy.GetParameterAsText(2)
NetworkData = arcpy.GetParameterAsText(3)
LiikenneElementti = arcpy.GetParameterAsText(4)
Nimi = arcpy.GetParameterAsText(5)
Impedanssi = arcpy.GetParameterAsText(6)
Breaks = arcpy.GetParameterAsText(7)
Pysakointi = arcpy.GetParameterAsText(8)
Kavely = int(arcpy.GetParameterAsText(9))
RinDisk = arcpy.GetParameterAsText(10)
Suunta = arcpy.GetParameterAsText(11)
Details = arcpy.GetParameterAsText(12)
Overlap = arcpy.GetParameterAsText(13)
Trim = arcpy.GetParameterAsText(14)
TrimCut = arcpy.GetParameterAsText(15)
#Lines = arcpy.GetParameterAsText(16) #Voidaan lisätä tarvittaessa parametriksi, tällöin tämä pitää lisätä myös käyttöliittymän viimeiseksi kysyttäväksi parametriksi!


#Environment määritykset:
temp = arcpy.GetSystemEnvironment("TEMP")
mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd, "*")[0]

env.workspace = temp

#Haetaan ArcGis versio:
for key, value in arcpy.GetInstallInfo().iteritems():
    if key == "Version":
        ArcVersio = value

#Luodaan suoritusinfopalkki
arcpy.SetProgressor("step", "PALVELUALUE LASKENTA...Tarkistukset ennen laskentaa...", 0, 100, 5) 

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

#Metodit/määritykset:

arcpy.overwriteOutputs = True

def AddLayerToMap(addLayer):
 mxd = arcpy.mapping.MapDocument("CURRENT")
 df = arcpy.mapping.ListDataFrames(mxd, "*")[0]
 arcpy.mapping.AddLayer(df, addLayer, "TOP")
 arcpy.RefreshActiveView()
 arcpy.RefreshTOC()
 del mxd, df, addLayer

def AddLayerToGroup(addLayer, Group):
 mxd = arcpy.mapping.MapDocument("CURRENT")
 df = arcpy.mapping.ListDataFrames(mxd, "*")[0]
 targetGroupLayer = arcpy.mapping.ListLayers(mxd, Group, df)[0]
 arcpy.mapping.AddLayerToGroup(df, targetGroupLayer, addLayer, "TOP")
 arcpy.RefreshActiveView()
 arcpy.RefreshTOC()
 del mxd, df, addLayer

def SetName(Layer, Name):
 mxd = arcpy.mapping.MapDocument("CURRENT")
 df = arcpy.mapping.ListDataFrames(mxd, "*")[0]
 Kohde = arcpy.mapping.ListLayers(mxd, Layer, df)[0]
 Kohde.name = Name
 arcpy.RefreshActiveView()
 arcpy.RefreshTOC()
 del mxd, df, Kohde


def ExDel(haettava):
    if arcpy.Exists(haettava):
        arcpy.Delete_management(haettava)

msg("------------------------------")
msg("METROPACCESS-DIGIROAD")
msg("MetropAccess-tutkimushanke")
msg("HELSINGIN YLIOPISTO")
msg("-------------------------------")
msg("5. Palvelualueen laskenta")
msg("-------------------------------")

time.sleep(2.5)

#---------------------------------------------------
#TARKISTUKSET
#---------------------------------------------------

#Tarkistetaan Network Datasetin muuttujat
msg("Tarkistetaan Network Dataset")
Aloitus()

desc = arcpy.Describe(NetworkData)
attributes = desc.attributes
NDparams = []
for attribute in attributes:
    NDparams.append(attribute.name)

NDPath = desc.path
LiikenneElementit = NDPath + "\\" + desc.edgeSources[0].name + ".shp" #Parsitaan sourcedatan (Liikenne_Elementit) polku ja nimi

arcpy.SetProgressorPosition(5)

Haettava = ["Digiroa_aa", "Kokopva_aa", "Keskpva_aa", "Ruuhka_aa", "Pituus"]
Nro = 0
Accumulation = []
for x in range(5):
    if Haettava[Nro] in NDparams:
        Accumulation.append(Haettava[Nro])
        Nro += 1
    else:
        Nro += 1

#Tarkistetaan, että impedanssi on olemassa:
if len(Accumulation) == 0:
    VL = arcpy.ListFields(LiikenneElementit, Impedanssi)
    VC = len(VL)
    if VC == 1:
        Accumulation.append(Impedanssi)  #Käytetään käyttäjän omaa impedanssikenttää laskentaan ja Accumulaatio kenttänä.
        msg("Käyttäjän määrittelemä impedanssi!")
    else:
        virhe("VIRHE! Määriteltyä impedanssia ei löydy Liikenne_Elementti -taulusta. Tarkista, että muuttuja on todella olemassa \nja että Impedanssikentän kirjoitusasu täsmää käytettävän muuttujan kanssa. ")
else:
    if Impedanssi in Accumulation:
        msg("Impedanssi määritetty.")
    else:
        VL = arcpy.ListFields(LiikenneElementit, Impedanssi)
        VC = len(VL)
        if VC == 1:
            Accumulation.append(Impedanssi)
            msg("Käyttäjän määrittelemä impedanssi!")
        else:
            virhe("VIRHE! Määriteltyä impedanssia ei löydy Network Datasetistä. Tarkista, että muuttuja on todella olemassa \nja että Impedanssikentän kirjoitusasu täsmää käytettävän muuttujan kanssa. ")


#Tarkistetaan että Group-layerit löytyvät:
polku = os.path.dirname(os.path.realpath(__file__)) #Määritetään python skriptin polku
Lyrpolku = polku + "\\" + "lyr"

SAGroup = Lyrpolku + "\\" + "Service_Areas.lyr"
AikaGroup = Lyrpolku + "\\" + "Sort_by_Time.lyr"
KohdeGroup = Lyrpolku + "\\" + "Sort_by_Facility.lyr"

if os.path.isdir(Lyrpolku) != True:
    teksti = "Kansiota: " + Lyrpolku + " ei löydy! Tarkista, että kansioon: " + polku + ", on sijoitettu MetropAccess-Digiroad työkalun mukana tuleva lyr-kansio tiedostoineen."
    virhe(teksti)
if os.path.isfile(SAGroup) != True:
    teksti = "Kansiosta: " + Lyrpolku + " ei löydy tarvittavaa tiedostoa 'Service_Areas.lyr'! Tarkista, että MetropAccess-Digiroad työkalun mukana tullut tiedosto varmasti löytyy kansiosta."
    virhe(teksti)
if os.path.isfile(AikaGroup) != True:
    teksti = "Kansiosta: " + Lyrpolku + " ei löydy tarvittavaa tiedostoa 'Sort_by_Time.lyr'! Tarkista, että MetropAccess-Digiroad työkalun mukana tullut tiedosto varmasti löytyy kansiosta."
    virhe(teksti)
if os.path.isfile(KohdeGroup) != True:
    teksti = "Kansiosta: " + Lyrpolku + " ei löydy tarvittavaa tiedostoa 'Sort_by_Facility.lyr'! Tarkista, että MetropAccess-Digiroad työkalun mukana tullut tiedosto varmasti löytyy kansiosta."
    virhe(teksti)

Valmis()
arcpy.SetProgressorPosition(10)
msg("----------------------------")

#-------------------------------------------------
#MÄÄRITETÄÄN PROJEKTIOT SAMAAN
#-------------------------------------------------

arcpy.SetProgressorLabel("PALVELUALUE LASKENTA...Tarkistetaan koordinaattijärjestelmät...")
msg("Tarkistetaan koordinaattijärjestelmät")
Aloitus()

#Tarkistetaan ND-projektio:
Desc = arcpy.Describe(NetworkData)
NDProjektio = Desc.spatialReference.factoryCode

if NDProjektio == 3067 or NDProjektio == 2391 or NDProjektio == 2392 or NDProjektio == 2393 or NDProjektio == 2394 or NDProjektio == 104129:
    msg("Tarkistettiin liikenneverkon projektio.")
else:
    virhe("Tieverkkoaineiston tulee olla projisoituna joko EUREF_FIN_TM35FIN:iin, GCS_EUREF_FIN:iin tai Finland_Zone_1, 2, 3 tai -4:ään (KKJ). Muuta Liikenne_elementti.shp projektio johonkin näistä Project -työkalulla, luo uusi Network Dataset perustuen tähän uuteen projisoituun LiikenneElementti -tiedostoon ja aja työkalu uudelleen.")

del Desc

#Tarkistetaan laskettavien kohteiden prjektio:

Desc = arcpy.Describe(Facilities)
Projektio = Desc.spatialReference.Name
FactCode = Desc.spatialReference.factoryCode
Proj = Projektio[:8]
FPath = temp + "\\" + "FacilitiesProj.shp"

#Luodaan spatial reference perustuen NetworkDatan SR:een:
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

msg("Määritettiin Spatial Reference")

#Määritetään Laskettaville kohteille sama projektio, jos NetworkData on EUREF_FIN_TM35FIN:issä tai GCS_EUREF_FIN:issä:
if NDProjektio == 3067 or NDProjektio == 104129:
    if NDProjektio != FactCode:
        if FactCode >= 2391 and FactCode <= 2394:
            transform_method = "KKJ_To_EUREF_FIN"
        elif FactCode == 3067:
            transform_method = ""
        elif Proj == "WGS_1984" or FactCode == 4326: #Projected WGS_1984 tai GCS_WGS_1984
            transform_method = "EUREF_FIN_To_WGS_1984"
        elif Proj == "ETRS_198":
            transform_method = "EUREF_FIN_To_ETRS_1989"
        else:
            virhe("Laskettavat kohteet tulee olla projisoituna johonkin seuraavista koordinaatistoista: KKJ, EUREF_FIN, WGS_1984, ETRS_1989")
                           
        env.workspace = temp
        if arcpy.Exists("FacilitiesProj.shp"):
            arcpy.Delete_management("FacilitiesProj.shp")
        arcpy.Project_management(Facilities, FPath, sr, transform_method) #Määritetään Destinationit samaan koordinaatistoon
        Facilities = FPath
        msg("Laskettavien kohteiden projektio vaihdettiin samaksi kuin Network Datalla. Luotiin kopio tiedostosta.")

#Määritetään laskettaville kohteille sama projektio, jos NetworkData on KKJ:ssa:
elif NDProjektio == 2391 or NDProjektio == 2392 or NDProjektio == 2393 or NDProjektio == 2394:
    if NDProjektio != FactCode: #Jos NetworkData ja kohdepisteet ovat eri KKJ:ssa projisoidaan ne samaan.
        if FactCode >= 2391 and FactCode <= 2394:
            transform_method = ""
        elif Proj == "WGS_1984" or FactCode == 4326: #Projected WGS_1984 tai GCS_WGS_1984
            transform_method = "KKJ_To_WGS_1984_2_JHS153"
        elif Proj == "ETRS_198":
            transform_method = "KKJ_To_ETRS_1989_2"
        else:
            virhe("Kohdepisteet tulee olla projisoituna johonkin seuraavista koordinaatistoista:")
            virhe("KKJ, EUREF_FIN, WGS_1984, ETRS_1989")
        
        env.workspace = temp
        if arcpy.Exists("FacilitiesProj.shp"):
            arcpy.Delete_management("FacilitiesProj.shp")
        arcpy.Project_management(Facilities, FPath, sr, transform_method) #Määritetään Destinationit samaan koordinaatistoon
        Facilities = FPath
        msg("Laskettavien kohteiden projektio vaihdettiin samaksi kuin Network Datalla. Luotiin kopio tiedostosta.")

arcpy.SetProgressor("step", "PALVELUALUE LASKENTA...Tarkistetaan koordinaattijärjestelmät...", 0, 100, 5)
arcpy.SetProgressorPosition(15)    
Valmis()
msg("----------------------------")

#-------------------------------------------------------------------------------------
#Luodaan kantakaupunki polygoni jos kävelyaika parkkipaikalle halutaan ottaa huomioon:
#-------------------------------------------------------------------------------------

if int(Kavely) > 0 and Pysakointi != "0":
    
    #Luodaan kantakaupunki polygoni:

    #Määritetään polygonien kulmien koordinaatit:
    coordList = [[387678.024778,6675360.99039],[387891.53396,6670403.35286],[383453.380944,6670212.21613],[383239.871737,6675169.85373],[387678.024778,6675360.99039]] #Koordinaatit ovat EUREF_FIN_TM35FIN:issä
    point = arcpy.Point()
    array = arcpy.Array()

    #Lisätään koordinaatit Arrayhin:
    for coordPair in coordList:
        point.X = coordPair[0]
        point.Y = coordPair[1]
        array.add(point)

    Kantakaupunki = arcpy.Polygon(array)

    arcpy.SetProgressor("step", "PALVELUALUE LASKENTA...Tarkistetaan koordinaattijärjestelmät...", 0, 100, 5)
    arcpy.SetProgressorPosition(20)  

    #Määritetään Spatial Reference:
    sr = arcpy.SpatialReference()
    sr.factoryCode = 3067
    sr.create()

    env.workspace = temp

    #Luodaan kantakaupunki tiedosto:
    Kantis = "Kantakaupunki.shp"
    ExDel(Kantis)
    arcpy.Select_analysis(Kantakaupunki, Kantis)

    #Määritetään kantakaupungille projektio:
    arcpy.DefineProjection_management(Kantis, sr)

    #Määritetään kantakaupungin projektio samaan kuin Network Datan:

    KantisPath = temp + "\\" + "KantisProj.shp"

    ExDel("DestinationsProj.shp")
    ExDel("OriginsProj.shp")
    ExDel("KantisProj.shp")

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

    if NDProjektio == 104129:
        arcpy.Project_management(Kantis, KantisPath, sr, "") #Määritetään kantakaupunki samaan koordinaatistoon
        Kantakaupunki = KantisPath

    elif NDProjektio == 2391 or NDProjektio == 2392 or NDProjektio == 2393 or NDProjektio == 2394:
        arcpy.Project_management(Kantis, KantisPath, sr, "KKJ_To_EUREF_FIN") #Määritetään kantakaupunki samaan koordinaatistoon
        Kantakaupunki = KantisPath



#------------------------------------------
#PARAMETRIEN TARKISTUS
#------------------------------------------

msg("Tarkistetaan parametrit")
arcpy.SetProgressor("step", "PALVELUALUE LASKENTA...Tarkistetaan parametrit...", 0, 100, 5)
arcpy.SetProgressorPosition(20)
Aloitus()

#Tarkistetaan kohteiden erotus:

if str(IndKohteet) == 'true':

    msg("Laskettavat kohteet halutaan erikseen")
    arcpy.SetProgressorLabel("PALVELUALUE LASKENTA...Luodaan kohde-layerit...")
    #Tehdään jokaisesta kohteen rivistä oma Feature layerinsä:
    FacilFeat = "FacilFeat"
    ExDel(FacilFeat)

    arcpy.MakeFeatureLayer_management(Facilities, FacilFeat, "", temp, "")   #Tehdään Laskettavista kohteista oma feature layerinsä

    rivit = int(arcpy.GetCount_management(FacilFeat).getOutput(0)) #Katsotaan montako kohdetta löytyy

    #Alustetaan nimet ja indeksi:
    i = 0
    FNimi = "Kohde_" + str(i) #Alustetaan kohteen nimi
    FaciPath = "Kohde_" + str(i) + ".shp" #Kohdetiedosto
    FaciList = [[],[]]               #Luodaan kohteille lista
    Step = 30.0 / rivit
    Progress = 20
        
    msg("Luodaan kohde-layerit")
    
    if rivit > 1:               #Tehdään Feature-layerit vain, jos tiedostossa on kohteita enemmän kuin yksi
        for rivi in range(rivit):
            ExDel(FaciPath)
            FID = "FID = " + str(i)
            arcpy.Select_analysis(FacilFeat, FaciPath, FID) #Valitaan jokainen tiedoston rivi yksi kerrallaan
            FaciList[0].append(FNimi) #Lisätään kohteen nimi listaan
            
            #Jos halutaan ottaa kävely parkkipaikalle huomioon merkitään kohteelle tieto onko se kantakaupungissa vai sen ulkopuolella:
            if int(Kavely) > 0:
                ExDel(FNimi) 
                arcpy.MakeFeatureLayer_management(Facilities, FNimi, FID, temp, "")

                #Katsotaan onko piste kantakaupungin sisällä:
                arcpy.SelectLayerByLocation_management(FNimi, "INTERSECT", Kantakaupunki, "", "NEW_SELECTION")

                #Katsotaan onko rivi valittuna vai ei:
                desc = arcpy.Describe(FNimi)
                Valinta = desc.FIDSet
                del desc
                
                if Valinta == "": #Jos piste ei ole kantakaupungin sisällä annetaan arvoksi 1
                    FaciList[1].append(0)
                else: #Jos piste on kantakaupungin sisällä annetaan arvoksi 0
                    FaciList[1].append(1)

            #Päivitykset:
            i += 1
            FNimi = "Kohde_" + str(i) #Päivitetään kohteen nimi
            FaciPath = "Kohde_" + str(i) + ".shp" #Päivitetään kohdetiedosto
            FID = "FID = " + str(i) #Päivitetään ehto
            Progress = Progress + Step
            arcpy.SetProgressorPosition(Progress)

arcpy.SetProgressorPosition(50)
msg("----------------------------")        

#--------------------------------
#Tarkistetaan Breaks arvot:

if Breaks.find(",") == -1: #Tarkistetaan onko pilkkuja
    True
else:
    Breaks = Breaks.replace(",", " ") #Korvataan pilkut whitespacella
if Breaks.find("  ") == -1: #Tarkistetaan onko liian pitkiä välejä
    True
else:
    Breaks = Breaks.replace("  ", " ") #Korvataan liian pitkät välit 1:llä whitespacella
if Breaks.find("   ") == -1: #Tarkistetaan onko liian pitkiä välejä
    True
else:
    Breaks = Breaks.replace("   ", " ") #Korvataan liian pitkät välit 1:llä whitespacella
#--------------------------------

#Tarkistetaan suunta:

if Suunta == "Pois laskettavista kohteista":
    Suunta = "TRAVEL_FROM" #The service area is created in the direction away from the facilities. 
elif Suunta == "Kohti laskettavia kohteita":
    Suunta = "TRAVEL_TO"   #The service area is created in the direction towards the facilities.
else:
    Suunta = "TRAVEL_FROM" #The service area is created in the direction away from the facilities. 

#--------------------------------

#Tarkistetaan Polygonin piirtotarkkuus:
if Details == "1":
    Details = "SIMPLE_POLYS"
elif Details == "2":
    Details = "DETAILED_POLYS"
elif Details == "3":
    Details = "NO_POLYS"
else:
    Details = "SIMPLE_POLYS"

#--------------------------------    

#Tarkistetaan kuinka polygonit halutaan piirtää:
PolyInd = 0 #Triggerin oletus
if RinDisk == "1": #Tehdään erilliset Layerit jokaisesta polygonista (hitaampi laskenta - analyysien kannalta järkevämpi)
    PolyInd = 1      #Määritetään triggeri, että aletaan suorittamaan erillisten Service Areoiden laskentaa
    RinDisk = "DISKS" #Tekee ainoastaan yhden Service Area layerin - Service area ei sisällä lähempänä lähtöpistettä sijaitsevia vyöhykkeitä (rinkulat)
elif RinDisk == "2":
    RinDisk = "DISKS" #Tekee ainoastaan yhden Service Area layerin - Service area ei sisällä lähempänä lähtöpistettä sijaitsevia vyöhykkeitä (rinkulat)
elif RinDisk == "3":
    RinDisk = "RINGS" #Jokainen Service Area vyöhyke sisältää myös lähempänä lähtöpistettä sijaitsevat vyöhykkeet
else:
    RinDisk = "DISKS"

#--------------------------------

#Tarkistetaan Overlap:
    
if Overlap == "1":
    Overlap = "NO_MERGE" #Kaikille kohteille tehdään omat polygonit, jotka voivat mennä myös päällekkäin.
elif Overlap == "2":
    Overlap = "NO_OVERLAP" #Kaikille kohteille tehdään omat polygonit, jotka eivät voi mennä päällekkäin (Dominanssialue). 
elif Overlap == "3":
    Overlap = "MERGE" #Yhdistää saman Break arvon omaavat polygonit yhteen.
else:
    Overlap = "NO_MERGE"

#--------------------------------

#Tarkistetaan polygonin Trimmaus:

if "Hierarkia" in NDparams and ArcVersio == "10.1": #Jos hierarkiaa käytetään ei voida käyttää Trimmiä
    Trim = "NO_TRIM_POLYS"
elif Trim == "False":
    Trim = "NO_TRIM_POLYS"
elif Trim == "True":
    Trim = "TRIM_POLYS"

#--------------------------------

#Tarkistetaan Trimmaus cutoff:

if Trim == "TRIM_POLYS":
    if int(TrimCut) > 0:
        TrimCut = TrimCut
    else:
        TrimCut = "100"
else:
    TrimCut = "100"

#--------------------------------

#Lines piirto (voi lisätä tarvittaessa parametriksi - huom pitää lisätä tällöin myös käyttöliittymän viimeiseksi parametriksi):

#if Lines == "0":
#    Lines = "NO_LINES"
#elif Lines == "1":
#    Lines = "TRUE_LINES"
#elif Lines == "2":
#    Lines = "TRUE_LINES_WITH_MEASURES"
#else:
    Lines = "NO_LINES"

Valmis()
arcpy.SetProgressorPosition(55)
msg("----------------------------")


#-------------------------------------------------
#LUODAAN SERVICE AREAT
#-------------------------------------------------    


msg("Luodaan palvelualueet")
arcpy.SetProgressorLabel("PALVELUALUE LASKENTA...Luodaan palvelualueet...")
Aloitus()

#Erotetaan Breaks valuet listan alkioiksi:
BreakNimi = string.split(Breaks, " ")
BreakList = string.split(Breaks, " ")
BreakCount = len(BreakList)
Step = 25.0 / BreakCount
Progress = 55

if PolyInd == 1: #Katsotaan halutaanko aika-arvo-polygonit erilleen
    msg("Erotetaan aika-arvot omiksi layereikseen")
    
    #--------------------------------------------------------------------------------------
    #AIKA-ARVOT ERIKSEEN (POLYGONIT)
    #--------------------------------------------------------------------------------------
    
    #Lisätään Service Area group Layer kartalle:
    SAGroup = Lyrpolku + "\\" + "Service_Areas.lyr"
    AddLyr = arcpy.mapping.Layer(SAGroup)
    AddLayerToMap(AddLyr)

    #Lisätään Service Area grouppiin Group by Time:
    AikaGroup = Lyrpolku + "\\" + "Sort_by_Time.lyr"
    AddLyr = arcpy.mapping.Layer(AikaGroup)
    AddLayerToGroup(AddLyr, "Service Areas")

            
    if str(SortPlace) == 'true': #Jos halutaan sortata kohteet myös paikan mukaan
        msg("Erotetaan laskettavat paikat omiksi layereikseen")
        KohdeGroup = Lyrpolku + "\\" + "Sort_by_Facility.lyr" #Lisätään Service Area grouppiin Group by Facility
        AddLyr = arcpy.mapping.Layer(KohdeGroup)
        AddLayerToGroup(AddLyr, "Service Areas")


    #Luodaan jokaiselle Breaks-valuelle oma Service-Area layer ja nimetään sen mukaisesti:
    if str(IndKohteet) == 'true'and rivit > 1:
        msg("Lisätään palvelualueet kartalle: sort by Time")

        infoCheck = False 
        for Break in BreakList:

            #Haetaan indeksi:
            i = BreakList.index(Break)
            
            for facility in FaciList[0]:

                #Haetaan indeksi:
                f = FaciList[0].index(facility)

                #Luodaan layer nimi:
                BreakName = BreakNimi[i] + "min_" + Nimi + "_" + facility

                try:
                    arcpy.Delete_management(BreakName)
                except:
                    pass

                Kohde = facility
                Kohde = Kohde.replace("Kohde_", "Facility_")

                #---------------------------------------------------------------------------------------------
                #PYSÄKÖINNIN HUOMIOON OTTAMINEN:
                #---------------------------------------------------------------------------------------------
                if Pysakointi != "0":
                                        
                    #-------------------------------------------------------------------------------------
                    #Määritetään Breaks-arvot uudelleen perustuen pysäköintityyppiin (ja kävelynopeuteen):
                    #-------------------------------------------------------------------------------------
               
                    if Kavely > 0: #Katsotaan halutaanko kävelyä parkkipaikalle ottaa huomioon
                                        
                        KavelySisa = 180.0 / Kavely
                        KavelyUlko = 135.0 / Kavely
                                                
                        #Muutetaan Breaks arvoja ainoastaan, jos niitä ei ole vielä muutettu:
                        if Break == BreakNimi[i]:
                        
                            if FaciList[1][f] == 1: #Katsotaan onko piste kantakaupungin sisällä
                                #Määritetään uudet Breaks-arvot
                                if Pysakointi == "1":
                                    Break = str(int(float(Break) - 0.42 - KavelySisa))
                                elif Pysakointi == "2":
                                    Break = str(int(float(Break) - 0.73 - KavelySisa))
                                elif Pysakointi == "3":
                                    Break = str(int(float(Break) - 0.22 - KavelySisa))
                                elif Pysakointi == "4":
                                    Break = str(int(float(Break) - 0.16 - KavelySisa))

                            elif FaciList[1][f] == 0: #Katsotaan onko piste kantakaupungin ulkopuolella
                                #Määritetään uudet Breaks-arvot
                                if Pysakointi == "1":
                                    Break = str(int(float(Break) - 0.42 - KavelyUlko))
                                elif Pysakointi == "2":
                                    Break = str(int(float(Break) - 0.73 - KavelyUlko))
                                elif Pysakointi == "3":
                                    Break = str(int(float(Break) - 0.22 - KavelyUlko))
                                elif Pysakointi == "4":
                                    Break = str(int(float(Break) - 0.16 - KavelyUlko))

                    else: #Jos kävelyä parkkipaikalle ei haluta ottaa huomioon

                        #Muutetaan Breaks arvoja ainoastaan, jos niitä ei ole vielä muutettu:
                        if Break == BreakNimi[i]:
                            if Pysakointi == "1":
                                Break = str(int(float(Break) - 0.42))
                            elif Pysakointi == "2":
                                Break = str(int(float(Break) - 0.73))
                            elif Pysakointi == "3":
                                Break = str(int(float(Break) - 0.22))
                            elif Pysakointi == "4":
                                Break = str(int(float(Break) - 0.16))
                    #----------------------------------------------------------------------------------------


                #Tehdään ServiceAreaLayer:
                if float(Break) <= 0.0:
                    if infoCheck == False:
                        teksti = "Break arvo: " + Break + ". Palvelualueen raja-arvoksi muodoistui <= 0 minuuttia! Ei laskettu palvelualuetta."
                        msg(teksti)
                        infoCheck = True
                else:
                    
                    #Tehdään ServiceAreaLayer:
                    arcpy.MakeServiceAreaLayer_na(NetworkData, BreakName, Impedanssi, Suunta, Break, Details, Overlap, RinDisk, Lines, "OVERLAP", "NO_SPLIT", "", Accumulation, "ALLOW_DEAD_ENDS_ONLY", "", Trim, TrimCut, "")
                                    
                    #Lisätään yksitellen kohteet Facilityiksi:
                    facility = temp + "\\" + facility + ".shp"
                    desc = arcpy.Describe(facility)
                    arcpy.AddLocations_na(BreakName, "Facilities", facility, "", "1000 Meters", "", "", "MATCH_TO_CLOSEST", "CLEAR", "NO_SNAP", "5 Meters", "EXCLUDE", "")

                                  
                    #Suoritetaan laskenta:
                    arcpy.Solve_na(BreakName)

                    #Lisätään kartalle:
                    
                    Poly = BreakName + "/" + "Polygons"
                    Timesort = BreakNimi[i] + "min_" + Nimi + "_" + Kohde
                    FacRename = arcpy.mapping.Layer(Poly).name = Timesort #Muutetaan nimi

                    AddLyr = arcpy.mapping.Layer(FacRename)
                    Group = "Sort_by_Time"
                    AddLayerToGroup(AddLyr, Group)

                    #Katsotaan halutaanko sortata myös kohteiden mukaan:
                    if str(SortPlace) == 'true':
                        Placesort = Kohde + "_" + Nimi + "_" + BreakNimi[i] + "min"
                        ExDel(Placesort)
                        arcpy.MakeFeatureLayer_management(FacRename, Placesort, "", temp) #Tehdään kopio kohdesorttausta varten

            Progress = Progress + Step
            arcpy.SetProgressorPosition(Progress)
            
        #-----------------------------------------------------------------------
        #KOHDEPAIKAT ERIKSEEN (SORTTAUS)
        #-----------------------------------------------------------------------
        
        if str(SortPlace) == 'true': #Jos halutaan sortata kohteet myös paikan mukaan
            msg("Lisätään palvelualueet kartalle: sort by Facility")

            FacilCount = len(FaciList)
            Step = 20.0 / FacilCount
            Progress = 80
            
            for facility in FaciList[0]:
                for Break in BreakList:
                    Kohde = facility
                    Kohde = Kohde.replace("Kohde_", "Facility_")

                    #Layer-Nimet
                    Timesort = Break + "min_" + Nimi + "_" + Kohde
                    Placesort = Kohde + "_" + Nimi + "_" + Break + "min"
                                    
                    AddLyr = arcpy.mapping.Layer(Placesort)
                    Group = "Sort_by_Facility"
                    AddLayerToGroup(AddLyr, Group)

                    #Määritetään värit:
                    arcpy.ApplySymbologyFromLayer_management(Placesort, Timesort)
                Progress = Progress + Step
                arcpy.SetProgressorPosition(Progress)
                
        #Poistetaan käytetyt facilityt:
        for facility in FaciList[0]:

            facility = temp + "\\" + facility + ".shp"
            ExDel(facility)

        arcpy.SetProgressorPosition(100)
        
        
    #------------------------------------------------------------------------            
    #Jos kohteita ei haluta erottaa tai kohteita on ainoastaan 1 kappale:
    #------------------------------------------------------------------------
    else:
        
        polku = os.path.dirname(os.path.realpath(__file__)) #Määritetään python skriptin polku
        Lyrpolku = polku + "\\" + "lyr"

        #Lisätään Service Area group Layer kartalle:
        SAGroup = Lyrpolku + "\\" + "Service_Areas.lyr"
        AddLyr = arcpy.mapping.Layer(SAGroup)
        AddLayerToMap(AddLyr)

        #Lisätään Service Area grouppiin Group by Time:
        AikaGroup = Lyrpolku + "\\" + "Sort_by_Time.lyr"
        AddLyr = arcpy.mapping.Layer(AikaGroup)
        AddLayerToGroup(AddLyr, "Service Areas")

        msg("Lisätään palvelualueet kartalle: sort by Time")
        
        for Break in BreakList:

            i = BreakList.index(Break)
            
            #Luodaan layer nimi:
            BreakName = BreakNimi[i] + "min_" + Nimi
            ExDel(BreakName)
            
            #Tehdään ServiceAreaLayer:
            arcpy.MakeServiceAreaLayer_na(NetworkData, BreakName, Impedanssi, Suunta, Break, Details, Overlap, RinDisk, Lines, "OVERLAP", "NO_SPLIT", "", Accumulation, "ALLOW_DEAD_ENDS_ONLY", "", Trim, TrimCut, "")
        
            #Lisätään laskettavat kohteet:
            arcpy.AddLocations_na(BreakName, "Facilities", Facilities, "", "1000 Meters", "", "", "MATCH_TO_CLOSEST", "CLEAR", "NO_SNAP", "5 Meters", "EXCLUDE", "")

            #Suoritetaan laskenta:
            arcpy.Solve_na(BreakName)

            #Lisätään kartalle:

            Poly = BreakName + "/" + "Polygons"
            Timesort = BreakNimi[i] + "min_" + Nimi + "."
            FacRename = arcpy.mapping.Layer(Poly).name = Timesort #Muutetaan nimi

            AddLyr = arcpy.mapping.Layer(FacRename)
            Group = "Sort_by_Time"
            AddLayerToGroup(AddLyr, Group)

            Progress = Progress + Step
            arcpy.SetProgressorPosition(Progress)

    arcpy.SetProgressorPosition(100)
    Valmis()
#-------------------------------------------------------------------------
#Jos Polygoneja ei haluta erottaa katsotaan halutaanko kohteet erilleen
#-------------------------------------------------------------------------
else:
    arcpy.SetProgressor("step", "SERVICE AREA LASKENTA...Luodaan Service Area Layer...", 0, 100, 5) #Luodaan suoritusinfopalkki
    arcpy.SetProgressorPosition(55)

    polku = os.path.dirname(os.path.realpath(__file__)) #Määritetään python skriptin polku
    Lyrpolku = polku + "\\" + "lyr"

    #Lisätään Service Area group Layer kartalle:
    SAGroup = Lyrpolku + "\\" + "Service_Areas.lyr"
    AddLyr = arcpy.mapping.Layer(SAGroup)
    AddLayerToMap(AddLyr)


    #------------------------------------------
    #Jos kohteet halutaan erottaa:
    #------------------------------------------
    if str(IndKohteet) == 'true' and rivit > 1: #Jos halutaan sortata kohteet paikan mukaan

        msg("Lisätään palvelualueet kartalle: sort by Facility")
        KohdeGroup = Lyrpolku + "\\" + "Sort_by_Facility.lyr" #Lisätään Service Area grouppiin Group by Facility
        AddLyr = arcpy.mapping.Layer(KohdeGroup)
        AddLayerToGroup(AddLyr, "Service Areas")

        #---------------------------------------------------------------------------------------------
        #PYSÄKÖINNIN HUOMIOON OTTAMINEN:
        #---------------------------------------------------------------------------------------------
        if Pysakointi != "0":
            msg("Otetaan pysäköinti huomioon")
            Aloitus()
            
            #-------------------------------------------------------------------------------------
            #Määritetään Breaks-arvot uudelleen perustuen pysäköintityyppiin (ja kävelynopeuteen):
            #-------------------------------------------------------------------------------------
            msg("Otetaan kävely parkkipaikalle huomioon")

            Breaks = "" #Nollataan Breaks-arvot
            for Break in BreakList:

                if Kavely > 0: #Katsotaan halutaanko kävelyä parkkipaikalle ottaa huomioon
                    
            
                    KavelyKeski = 157.5 / Kavely
                                        
                    #Määritetään uudet Breaks-arvot
                    if Pysakointi == "1":
                        Break = str(float(Break) - 0.42 - KavelyKeski)
                    elif Pysakointi == "2":
                        Break = str(float(Break) - 0.73 - KavelyKeski)
                    elif Pysakointi == "3":
                        Break = str(float(Break) - 0.22 - KavelyKeski)
                    elif Pysakointi == "4":
                        Break = str(float(Break) - 0.16 - KavelyKeski)

                   
                else: #Jos kävelyä parkkipaikalle ei haluta ottaa huomioon

                    if Pysakointi == "1":
                        Break = str(float(Break) - 0.42)
                    elif Pysakointi == "2":
                        Break = str(float(Break) - 0.73)
                    elif Pysakointi == "3":
                        Break = str(float(Break) - 0.22)
                    elif Pysakointi == "4":
                        Break = str(float(Break) - 0.16)

                #Lisätään uusi Break-arvo Breaks-stringiin:
                Breaks = Breaks + Break + " "

            Breaks = Breaks[:-1] #Poistetaan ylimääräinen välilyönti lopusta

                #----------------------------------------------------------------------------------------

        FacilCount = len(FaciList)
        Step = 45.0 / FacilCount
        Progress = 55

        for facility in FaciList[0]:

            #Luodaan nimet
            facilName = facility + "_" + Nimi
            Kohde = facility
            Kohde = Kohde.replace("Kohde_", "Facility_")

            f = FaciList[0].index(facility)

            #Luodaan Service Area Layer:
            arcpy.MakeServiceAreaLayer_na(NetworkData, facilName, Impedanssi, Suunta, Breaks, Details, Overlap, RinDisk, Lines, "OVERLAP", "NO_SPLIT", "", Accumulation, "ALLOW_DEAD_ENDS_ONLY", "", Trim, TrimCut, "")
                        
            #Lisätään yksitellen kohteet Facilityiksi:
            Shapefacility = temp + "\\" + facility + ".shp"
            arcpy.AddLocations_na(facilName, "Facilities", Shapefacility, "", "1000 Meters", "", "", "MATCH_TO_CLOSEST", "CLEAR", "NO_SNAP", "5 Meters", "EXCLUDE", "")
                        
            #Suoritetaan laskenta:
            arcpy.Solve_na(facilName)

            Poly = facilName + "/" + "Polygons"
            Placesort = Kohde + "_" + Nimi
            FacRename = arcpy.mapping.Layer(Poly).name = Placesort #Muutetaan nimi

            #Lisätään kartalle:
            AddLyr = arcpy.mapping.Layer(FacRename)
            Group = "Sort_by_Facility"
            AddLayerToGroup(AddLyr, Group)
            Progress = Progress + Step
            arcpy.SetProgressorPosition(Progress)
            
        Valmis()    
        
#----------------------------------------------------------------------------------------
#Jos polygoneja eikä kohteita haluta erottaa suoritetaan normaali Service Area laskenta:
#----------------------------------------------------------------------------------------            
    else:

        #Luodaan Service Area Layer:
        arcpy.MakeServiceAreaLayer_na(NetworkData, Nimi, Impedanssi, Suunta, Breaks, Details, Overlap, RinDisk, Lines, "OVERLAP", "NO_SPLIT", "", Accumulation, "ALLOW_DEAD_ENDS_ONLY", "", Trim, TrimCut, "")
        arcpy.SetProgressorPosition(60)
        
        #Lisätään Laskettavat kohteet:
        arcpy.AddLocations_na(Nimi, "Facilities", Facilities, "", "1000 Meters", "", "", "MATCH_TO_CLOSEST", "CLEAR", "NO_SNAP", "5 Meters", "EXCLUDE", "")
        arcpy.SetProgressorPosition(70)
        msg("Lisätään palvelualueet kartalle")

        #Piirretään Layer kartalle:
        AddLyr = arcpy.mapping.Layer(Nimi)
        Group = "Service Areas"
        AddLayerToGroup(AddLyr, Group)
        arcpy.SetProgressorPosition(90)
        
        #Suoritetaan Service Area laskenta:
        arcpy.Solve_na(Nimi)
        arcpy.SetProgressorPosition(100)
        
        Valmis()

    
    



