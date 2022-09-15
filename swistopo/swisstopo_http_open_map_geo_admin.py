# Copyright (c) 2017  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import c4d
import webbrowser
import urllib
from pprint import pprint

CONTAINER_ORIGIN = 1026473

#valeurs du pixel selon zoom carte zoom = 0 -> 1px = 650m
#selon https://api3.geo.admin.ch/services/sdiservices.html#wmts
zoom = [650,
        500,
        250,
        100,
        50,
        20,
        10,
        5,
        2.5,
        2,
        1,
        0.5,
        0.25,
        0.1,]


defpage = "https://map.geo.admin.ch/?lang=fr"


def url_swissmap(url):
    """renvoie l'url longue si c'est un raccourci
       l'url si c'est déjà une url longue
       on None si ce n'est pas une url map.geo.admin"""
    pref_courte = 'https://s.geo.admin.ch/'
    len_pref_courte = len(pref_courte)

    if len(url)> len_pref_courte and url[:len_pref_courte] == pref_courte:
        with urllib.request.urlopen(url) as f:
            url_full = f.geturl()
            return url_full

    # traitement de l'url
    pref_url_longue = 'https://map.geo.admin.ch/'
    len_pref_url_longue = len(pref_url_longue)

    if len(url)> len_pref_url_longue and url[:len_pref_url_longue] == pref_url_longue:
        return url

    return False

def get_info_from_url(url):
    dico = {}
    if len(url.split('?'))==2:
        req = url.split('?')[1]
        for part in req.split('&'):
            key,val = part.split('=')
            if key == 'layers' :
                val = val.split(',')
            elif key == 'layers_opacity':
                val = [float(v) for v in val.split(',')]
            elif key == 'layers_visibility' :
                val = [bool(v) for v in val.split(',')]
            elif key == 'layers_timestamp':
                # pour les voyages temporels
                #la date est sous la forme 18641231 -> on récupère que l'année
                val = [int(v[:4]) for v in val.split(',') if v]
            elif key in ['E','N','zoom']:
                val = float(val)
            dico[key] = val
    return dico

class Dialog(c4d.gui.GeDialog):

    ID_HTML = 1000
    ID_URL = 1001
    ID_BTON_VIEW_TO_HTML = 1002
    ID_BTON_HTML_TO_VIEW = 1003
    ID_BTON_TO_WEBBROWSER = 1004

    TXT_BTON_VIEW_TO_HTML = 'depuis la vue de dessus'
    TXT_BTON_HTML_TO_VIEW = 'vers la vue de dessus'
    TXT_BTON_TO_WEBBROWSER = 'vers le navigateur'

    TXT_MSG_NO_URL_IN_CLIPBOARD = """Il n'y a pas d'url map.geo.admin valide.\n Cliquez d'abord sur "Ouvrir le menu", puis "Partager" et "Copier le lien." """

    def __init__(self):
        c4d.gui.GeDialog.__init__(self)
        self.AddGadget(c4d.DIALOG_NOMENUBAR, 0)

    def CreateLayout(self):
        self.SetTitle("Web Browser")
        self.GroupBegin(0, c4d.BFH_SCALEFIT, 0, 3)
        self.GroupBorderSpace(2, 2, 2, 0)
        self.AddGadget(c4d.DIALOG_PIN, 0)
        self.AddEditText(self.ID_URL, c4d.BFH_SCALEFIT)
        self.GroupBegin(0, c4d.BFH_SCALEFIT, 3, 0)
        self.AddButton(self.ID_BTON_VIEW_TO_HTML,c4d.BFH_LEFT, initw=200, inith=20, name=self.TXT_BTON_VIEW_TO_HTML)
        self.AddButton(self.ID_BTON_HTML_TO_VIEW,c4d.BFH_CENTER, initw=200, inith=20, name=self.TXT_BTON_HTML_TO_VIEW)
        self.AddButton(self.ID_BTON_TO_WEBBROWSER,c4d.BFH_RIGHT, initw=200, inith=20, name=self.TXT_BTON_TO_WEBBROWSER)
        self.GroupEnd()
        self.GroupEnd()
        self.b = self.AddCustomGui(self.ID_HTML, c4d.CUSTOMGUI_HTMLVIEWER, "",
            c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 200, 200)
        return True

    def InitValues(self):
        self.SetString(self.ID_URL, defpage)
        self.Command(1, None)
        return True

    def Command(self, wid, bc):
        if wid == c4d.DLG_OK:  # Enter pressed
            url = self.GetString(self.ID_URL)
            self.b.SetUrl(url, c4d.URL_ENCODING_UTF16)

        if wid == self.ID_BTON_VIEW_TO_HTML:
            pass

        #BOUTON -> VUE
        if wid == self.ID_BTON_HTML_TO_VIEW:
            #on récupère le presse-papier
            url = c4d.GetStringFromClipboard()
            #s'il y a du texte on regarde si c'est bien une url swisstopo
            if url:
                url = url_swissmap(url)
                if url:
                    dico = get_info_from_url(url)
                    est,nord = dico.get('E',None), dico.get('N',None)

                    if est and nord:
                        centre = c4d.Vector(est,0,nord)
                        #si le doc n'est pas georef on le georef avec le centre

                        if not doc[CONTAINER_ORIGIN]:
                            #TODO -> passer le doc en mètres
                            doc[CONTAINER_ORIGIN] = centre

                        origine = doc[CONTAINER_ORIGIN]
                        
                        bd = doc.GetActiveBaseDraw()
                        secu = 0
                        while bd:
                            if bd.GetName() == 'Top':
                                break
                            bd = bd.GetNext()
                            secu+=1
                            if secu > 10: break
                        if not bd :
                            print("pas de vue de haut")
                        else:
                            cam = bd.GetEditorCamera()
                            cam.SetAbsPos(centre-origine)
                            c4d.EventAdd()
                            #c4d.CallCommand(1058396) # #$02carte nationale 25'000

                    return True
            c4d.gui.MessageDialog(self.TXT_MSG_NO_URL_IN_CLIPBOARD)

        if wid == self.ID_BTON_TO_WEBBROWSER:
            #on récupère le presse-papier
            url = c4d.GetStringFromClipboard()
            #s'il y a du texte on regarde si c'est bien une url swisstopo
            if url:
                if url_swissmap(url):
                    webbrowser.open(url)
                    return True
            c4d.gui.MessageDialog(self.TXT_MSG_NO_URL_IN_CLIPBOARD)

        return True

dlg = Dialog()
dlg.Open(c4d.DLG_TYPE_ASYNC)