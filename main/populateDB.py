#encoding:utf-8
from main.models import Artista, Etiqueta, UsuarioArtista, UsuarioEtiquetaArtista
from datetime import datetime

path = "data"

def populate():
    populateArtista()
    populateEtiqueta()
    populateUsuarioArtista()
    populateUsuarioEtiquetaArtista()
   
    return True

def populateArtista():
    Artista.objects.all().delete()
    
    lista=[]

    with open(path+"\\artists.dat", "r",encoding="ISO-8859-1") as f:
        next(f)
        for line in f:
            splits = line.split("\t")
            lista.append(Artista(IdArtista= int(splits[0].strip()),nombre= str(splits[1].strip()), Url= str(splits[2].strip()), PictureUrl= str(splits[3].strip())))
    
    Artista.objects.bulk_create(lista)  # bulk_create hace la carga masiva para acelerar el proceso
    
    return Artista.objects.count()

def populateEtiqueta():
    Etiqueta.objects.all().delete()
    
    lista=[]

    with open(path+"\\tags.dat", "r",encoding="ISO-8859-1") as f:
        next(f)
        for line in f:
            splits = line.split("\t")
            lista.append(Etiqueta(IdTag= int(splits[0].strip()),TagValue= str(splits[1].strip())))
    
    Etiqueta.objects.bulk_create(lista)  # bulk_create hace la carga masiva para acelerar el proceso
    
    return Etiqueta.objects.count()

def populateUsuarioArtista():
    UsuarioArtista.objects.all().delete()
    
    lista=[]

    with open(path+"\\user_artists.dat", "r",encoding="ISO-8859-1") as f:
        next(f)
        for line in f:
            splits = line.split("\t")
            lista.append(UsuarioArtista(IdUsuario= int(splits[0].strip()),IdArtista= Artista.objects.get(IdArtista= int(splits[1].strip())) , TiempoEscucha= int(splits[2].strip()) ))
    
    UsuarioArtista.objects.bulk_create(lista)  # bulk_create hace la carga masiva para acelerar el proceso
    
    return UsuarioArtista.objects.count()

def populateUsuarioEtiquetaArtista():
    UsuarioEtiquetaArtista.objects.all().delete()
    
    lista=[]

    with open(path+"\\user_taggedartists.dat", "r",encoding="ISO-8859-1") as f:
        next(f)
        for line in f:
            splits = line.split("\t")
            try:
                lista.append(UsuarioEtiquetaArtista(IdUsuario= int(splits[0].strip()),IdArtista= Artista.objects.get(IdArtista= int(splits[1].strip())), IdTag= Etiqueta.objects.get(IdTag = int(splits[2].strip())), Dia= int(splits[3].strip()), Mes= int(splits[4].strip()), Ano= int(splits[5].strip()) ))
            except: 
                pass
    UsuarioEtiquetaArtista.objects.bulk_create(lista)  # bulk_create hace la carga masiva para acelerar el proceso
    
    return UsuarioEtiquetaArtista.objects.count()
