#encoding:utf-8
from main.models import Artista, Etiqueta, UsuarioArtista, UsuarioEtiquetaArtista
from datetime import datetime

path = "data"

def populate():
    artistas = populateArtista()
    etiquetas = populateEtiqueta()
    populateUsuarioArtista(artistas)
    populateUsuarioEtiquetaArtista(artistas, etiquetas)
   
    return True

def populateArtista():
    Artista.objects.all().delete()
    
    lista=[]

    artistas = {}


    with open(path+"\\artists.dat", "r",encoding="ISO-8859-1") as f:
        next(f)
        for line in f:
            splits = line.split("\t")
            artista = Artista(IdArtista= int(splits[0].strip()),nombre= str(splits[1].strip()), Url= str(splits[2].strip()), PictureUrl= str(splits[3].strip()))
            artistas[artista.IdArtista] = artista
            lista.append(artista)
    
    Artista.objects.bulk_create(lista)  # bulk_create hace la carga masiva para acelerar el proceso
    
    return artistas

def populateEtiqueta():
    Etiqueta.objects.all().delete()
    
    lista=[]

    etiquetas = {}
    with open(path+"\\tags.dat", "r",encoding="ISO-8859-1") as f:
        next(f)
        for line in f:
            splits = line.split("\t")
            etiqueta = Etiqueta(IdTag= int(splits[0].strip()),TagValue= str(splits[1].strip()))
            etiquetas[etiqueta.IdTag] = etiqueta
            lista.append(etiqueta)
    
    Etiqueta.objects.bulk_create(lista)  # bulk_create hace la carga masiva para acelerar el proceso
    
    return etiquetas

def populateUsuarioArtista(artistas):
    UsuarioArtista.objects.all().delete()
    
    lista=[]

    with open(path+"\\user_artists.dat", "r",encoding="ISO-8859-1") as f:
        next(f)
        for line in f:
            splits = line.split("\t")
            lista.append(UsuarioArtista(IdUsuario= int(splits[0].strip()),IdArtista= artistas[int(splits[1].strip())] , TiempoEscucha= int(splits[2].strip()) ))
    
    UsuarioArtista.objects.bulk_create(lista)  # bulk_create hace la carga masiva para acelerar el proceso
    
    return UsuarioArtista.objects.count()

def populateUsuarioEtiquetaArtista(artistas, etiquetas):
    UsuarioEtiquetaArtista.objects.all().delete()
    
    lista=[]

    with open(path+"\\user_taggedartists.dat", "r",encoding="ISO-8859-1") as f:
        next(f)
        for line in f:
            splits = line.split("\t")
            try:
                lista.append(UsuarioEtiquetaArtista(IdUsuario= int(splits[0].strip()),IdArtista= artistas[int(splits[1].strip())], IdTag= etiquetas[int(splits[2].strip())], Dia= int(splits[3].strip()), Mes= int(splits[4].strip()), Ano= int(splits[5].strip()) ))
            except: 
                pass
    UsuarioEtiquetaArtista.objects.bulk_create(lista)  # bulk_create hace la carga masiva para acelerar el proceso
    
    return UsuarioEtiquetaArtista.objects.count()
