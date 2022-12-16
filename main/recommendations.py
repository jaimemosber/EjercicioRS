#encoding:utf-8
from main.models import UsuarioEtiquetaArtista, UsuarioArtista
from math import sqrt
from django.db.models import Count
from collections import Counter

def top_artist_tags():
    # Calcula el conjunto de diez etiquetas más frecuentes de cada artista
    artists = {}
    anterior = -1
    suma = 1
    for e in UsuarioEtiquetaArtista.objects.values('IdArtista','IdTag').annotate(tag_count=Count('IdTag')).order_by('IdArtista','-tag_count'):
        if e['IdArtista'] == anterior and suma <= 10:
            artists[e['IdArtista']].add(e['IdTag'])
            suma = suma + 1
        else:
            artists[e['IdArtista']] = set([e['IdTag']])
            suma = 1
            anterior = e['IdArtista']
    return artists
    
def top_user_tags(artist_tags):
    # Calcula el conjunto de  etiquetas de los cinco artistas más esc. de cada user
    usuarios = {}
    anterior = -1
    suma = 1
    for e in UsuarioArtista.objects.values('IdUsuario', 'IdArtista','TiempoEscucha').order_by('IdUsuario','-TiempoEscucha'):
        if e['IdUsuario'] == anterior and suma <= 5:
            if e['IdArtista'] in artist_tags.keys():
                usuarios[e['IdUsuario']].union(artist_tags[e['IdArtista']])
                suma = suma + 1
        else:
            if e['IdArtista'] in artist_tags.keys():
                usuarios[e['IdUsuario']] = set(artist_tags[e['IdArtista']])
                suma = 1
                anterior = e['IdUsuario']
    return usuarios

def compute_similarities(artist_tags, user_tags):
    res = {}
    for u in user_tags:
        top_artists = {}
        for a in artist_tags:
            top_artists[a] = dice_coefficient(user_tags[u], artist_tags[a])
        res[u] = Counter(top_artists).most_common(20)
    return res 

# Returns a distance-based similarity score for person1 and person2
def sim_distance(prefs, person1, person2):
    # Get the list of shared_items
    si = {}
    for item in prefs[person1]: 
        if item in prefs[person2]: si[item] = 1

        # if they have no ratings in common, return 0
        if len(si) == 0: return 0

        # Add up the squares of all the differences
        sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2) 
                    for item in prefs[person1] if item in prefs[person2]])
        
        return 1 / (1 + sum_of_squares)

# Returns the Pearson correlation coefficient for p1 and p2
def sim_pearson(prefs, p1, p2):
    # Get the list of mutually rated items
    si = {}
    for item in prefs[p1]: 
        if item in prefs[p2]: si[item] = 1

    # if they are no ratings in common, return 0
    if len(si) == 0: return 0

    # Sum calculations
    n = len(si)

    # Sums of all the preferences
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    # Sums of the squares
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])	

    # Sum of the products
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

    # Calculate r (Pearson score)
    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if den == 0: return 0

    r = num / den

    return r

# Returns the best matches for person from the prefs dictionary. 
# Number of results and similarity function are optional params.
def topMatches(prefs, person, n=5, similarity=sim_pearson):
    scores = [(similarity(prefs, person, other), other) 
                for other in prefs if other != person]
    scores.sort()
    scores.reverse()
    return scores[0:n]

# Gets recommendations for a person by using a weighted average of every other user's rankings
def getRecommendations(prefs, person, similarity=sim_pearson):
    totals = {}
    simSums = {}
    for other in prefs:
        # don't compare me to myself
        if other == person: continue
        sim = similarity(prefs, person, other)
        # ignore scores of zero or lower
        if sim <= 0: continue
        for item in prefs[other]:
            # only score movies I haven't seen yet
            if item not in prefs[person] or prefs[person][item] == 0:
                # Similarity * Score
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim
                # Sum of similarities
                simSums.setdefault(item, 0)
                simSums[item] += sim

    # Create the normalized list
    rankings = [(total / simSums[item], item) for item, total in totals.items()]
    # Return the sorted list
    rankings.sort()
    rankings.reverse()
    return rankings

def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
    
            # Flip item and person
            result[item][person] = prefs[person][item]
    return result


def calculateSimilarItems(prefs, n=10):
    # Create a dictionary of items showing which other items they
    # are most similar to.
    result = {}
    # Invert the preference matrix to be item-centric
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs:
        # Status updates for large datasets
        c += 1
        if c % 100 == 0: print ("%d / %d" % (c, len(itemPrefs)))
        # Find the most similar items to this one
        scores = topMatches(itemPrefs, item, n=n, similarity=sim_distance)
        result[item] = scores
    return result

def getRecommendedItems(prefs, itemMatch, user):
    userRatings = prefs[user]
    scores = {}
    totalSim = {}
    # Loop over items rated by this user
    for (item, rating) in userRatings.items():
        # Loop over items similar to this one
        for (similarity, item2) in itemMatch[item]:
            print (item2)
            # Ignore if this user has already rated this item
            if item2 in userRatings: continue
            # Weighted sum of rating times similarity
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating
            # Sum of all the similarities
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity

    # Divide each total score by total weighting to get an average
    try:
        rankings = [(score / totalSim[item], item) for item, score in scores.items()]
    except ZeroDivisionError:
        rankings = []

    # Return the rankings from highest to lowest
    rankings.sort()
    rankings.reverse()
    return rankings

def dice_coefficient(set1, set2):
    return 2 * len(set1.intersection(set2)) / (len(set1) + len(set2))