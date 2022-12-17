#encoding:utf-8
from main.models import Artista, Etiqueta
from django.shortcuts import render, get_object_or_404
from main import populateDB
from django.contrib.auth.decorators import login_required
from django.db.models import Max
import shelve
from main.recommendations import  transformPrefs, getRecommendations, topMatches, sim_distance,calculateSimilarItems, top_artist_tags, top_user_tags, compute_similarities
from django.conf import settings
from main.models import UsuarioArtista
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect



def loadDict(request):
    # matriz de usuarios y puntuaciones a cada a items
    shelf = shelve.open("dataRS")

    artistsTags = top_artist_tags()
    userTags = top_user_tags(artistsTags)
    perfilesParecidos = compute_similarities(artistsTags, userTags)

    shelf['UserTags']=artistsTags
    shelf['ArtistTags']=userTags
    shelf['PerfilesParecidos']=perfilesParecidos
    shelf.close()
    
    mensaje = 'Se han cargado la matriz y la matriz invertida '
    return render(request, 'message.html',{'titulo':'FIN DE CARGA DEL RS','mensaje':mensaje,'STATIC_URL':settings.STATIC_URL})

def top_artists_user(self):
    usuarioArtistas = []
    q = self.GET.get("q")
    if q is not None:
        usuarioArtistas = UsuarioArtista.objects.filter(IdUsuario = int(q)).order_by('IdUsuario', '-TiempoEscucha')[:5]
    return render(self, 'usuarioartistas.html',{'usuarioArtistas':usuarioArtistas})

def top_artist_tags(self):
    q = self.GET.get("q")
    shelf = shelve.open("dataRS")
    etiquetas = []
    etiquetasTrad = []
    artistTags = []
    if q is not None:
        artistTags = shelf['ArtistTags']
        etiquetas = artistTags[int(q)]
        for e in etiquetas:
            etiquetasTrad.append(Etiqueta.objects.get(IdTag = e))
    return render(self, 'etiquetasArtista.html',{'etiquetasArtista':etiquetasTrad})

def recomendaciones(self):
    q = self.GET.get("q")
    shelf = shelve.open("dataRS")
    perfilesParecidos = []
    perfiles = []
    perfilesTrad = []
    if q is not None:
        perfilesParecidos = shelf['PerfilesParecidos']
        perfiles = perfilesParecidos[int(q)]
        for e in perfiles:
            perfilesTrad.append(Artista.objects.get(IdArtista = e[0]))

    return render(self, 'recomendaciones.html',{'perfiles':perfilesTrad})

@login_required(login_url='/ingresar')
def cargar(request):
    if populateDB.populate():
        artista = Artista.objects.all().count()
        etiqueta = Etiqueta.objects.all().count()

        informacion="Datos cargados correctamente\n" + "Artistas: " + str(artista) + " ; " + "Etiqueta: " + str(etiqueta)
    else:
        informacion="ERROR en la carga de datos"
    return render(request, 'carga.html', {'inf':informacion})

def ingresar(request):
    formulario = AuthenticationForm()
    if request.method=='POST':
        formulario = AuthenticationForm(request.POST)
        usuario=request.POST['username']
        clave=request.POST['password']
        acceso=authenticate(username=usuario,password=clave)
        if acceso is not None:
            if acceso.is_active:
                login(request, acceso)
                return (HttpResponseRedirect('/cargar'))
            else:
                return render(request, 'mensaje_error.html',{'error':"USUARIO NO ACTIVO",'STATIC_URL':settings.STATIC_URL})
        else:
            return render(request, 'mensaje_error.html',{'error':"USUARIO O CONTRASEÑA INCORRECTOS",'STATIC_URL':settings.STATIC_URL})
                     
    return render(request, 'ingresar.html', {'formulario':formulario, 'STATIC_URL':settings.STATIC_URL})

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