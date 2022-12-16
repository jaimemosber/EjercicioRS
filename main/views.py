#encoding:utf-8
from main.models import Artista, Etiqueta
from django.shortcuts import render, get_object_or_404
from main import populateDB
from django.contrib.auth.decorators import login_required
from django.db.models import Max
import shelve
from main.recommendations import  transformPrefs, getRecommendations, topMatches, sim_distance,calculateSimilarItems
from django.conf import settings



def loadDict():
    Prefs={}   # matriz de usuarios y puntuaciones a cada a items
    shelf = shelve.open("dataRS.dat")
    ratings = Puntuacion.objects.all()
    for ra in ratings:
        user = ra.idUsuario.id
        itemid = ra.idPelicula.id
        rating = ra.puntuacion
        Prefs.setdefault(user, {})
        Prefs[user][itemid] = rating
    shelf['Prefs']=Prefs
    shelf['ItemsPrefs']=transformPrefs(Prefs)
    shelf.close()


def cargar(request):
    if populateDB.populate():
        artista = Artista.objects.all().count()
        etiqueta = Etiqueta.objects.all().count()

        informacion="Datos cargados correctamente\n" + "Artistas: " + str(artista) + " ; " + "Etiqueta: " + str(etiqueta)
    else:
        informacion="ERROR en la carga de datos"
    return render(request, 'carga.html', {'inf':informacion})

#muestra los títulos de las recetas que están registradas
def inicio(request):

    return render(request, 'inicio.html')


def loadRS(request):
    loadDict()
    mensaje = 'Se han cargado la matriz y la matriz invertida '
    return render(request, 'message.html',{'titulo':'FIN DE CARGA DEL RS','mensaje':mensaje,'STATIC_URL':settings.STATIC_URL})


def recommentFilm(self, id=None):
    q = self.GET.get("q")
    rankings=[]
    if q is not None:
        shelf = shelve.open("dataRS.dat")
        Prefs = shelf['Prefs']
        shelf.close()

        rankings = getRecommendations(Prefs, int(q))
        puntuadas=Puntuacion.objects.all().values().filter(idUsuario=int(q))
        pelis=[p['idPelicula_id'] for p in puntuadas]

        lista=[]
        for r in rankings:
            if r[1] not in pelis:
                lista.append(r)
        peliculas=[]
        for l in lista[:2]:
            peliculas.append(Pelicula.objects.get(pk=l[1]))



    return render(self, 'recomendarPeli.html',{'recomendaciones':peliculas})
def similarFilm(self, id=None):
    q = self.GET.get("q")
    similar=[]
    lista=[]
    if q is not None:
        shelf = shelve.open("dataRS.dat")
        Prefs = shelf['ItemsPrefs']
        shelf.close()

        similar = topMatches(Prefs, int(q),n=3,similarity=sim_distance)
        for l in similar:
            lista.append(Pelicula.objects.get(pk=l[1]))

    return render(self, 'pelissimilares.html',{'recomendaciones':lista})

def pelisPuntuadas(self, id=None):
    q = self.GET.get("q")

    if q is not None:

        rankings=Puntuacion.objects.all().values().filter(idUsuario=int(q))

        lista = []

        peliculas = []
        for l in rankings:
            peliculas.append(Pelicula.objects.get(pk=l['idPelicula_id']))

    return render(self, 'pelissimilares.html',{'recomendaciones':peliculas})