#Auteur : David PINAUD
#Description : fichier permettant de récuperer une instance du problème du sac à dos multi-objectifs en fonction du nombre d'objet et d'objectifs voulu

import numpy as np
import os
import random as rand

def getInstance(n=20,p=3):
    """Retourne une instance de sac à dos composé des n PREMIERS objets dans le fichier
    et des p PREMIERS critères
    La capacité W est calculée selon les éléments choisis

    Parameters
    ----------
    n : int, optional
        nombre d'objets à prendre dans l'instance, by default 20
    p : int, optional
        nombre de critères à prendre dans l'instance, by default 3
    Returns
    -------
    dict, int
        dictionnaire avec comme clé l'indice de l'objet et comme valeur le poids ainsi que les critères de l'objet et la capacité du sac à dos
    """
    objets=dict()
    if(n>200):
        n=200
    elif(n<=0):
        return objets

    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'data.txt')
    with open(filename) as data:
        index=0
        W=0
        for _ in range(4):
            data.readline()
        for line in data:
            elements_in_line=[int(elem) if i>0 else elem for i,elem in enumerate(line.split())]
            objets[index]=elements_in_line[1:p+2] #key=index, value=[w v1 v2 ... vp] (p+1 éléments)
            W+=elements_in_line[1]
            index+=1
            if index==n: #on s'arrête quand on a n objets
                break
    W=np.floor(W/2)
    return objets,W

def getInstance_withRandomSelection(n=20,p=3):
    """Retourne une instance de sac à dos composé de n objets CHOISIS AU HASARD dans le fichier
    et de p PREMIERS critères.
    La capacité W est calculée selon les éléments choisis

    Parameters
    ----------
    n : int, optional
        nombre d'objets à prendre dans l'instance, by default 20
    p : int, optional
        nombre de critères à prendre dans l'instance, by default 3
    Returns
    -------
    dict, int
        dictionnaire avec comme clé l'indice de l'objet et comme valeur le poids ainsi que les critères de l'objet et la capacité du sac à dos
    """
    objets=dict()
    if(n>200):
        n=200
    elif(n<=0):
        return objets

    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'data.txt')
    with open(filename) as data:
        index=0
        W=0
        for _ in range(4):
            data.readline()
        index=0
        for line in data:
            if(line.split()[0]=="i"):
                elements_in_line=[int(elem) if i>0 else elem for i,elem in enumerate(line.split())]
                objets[index]=elements_in_line[1:p+2] #key=index, value=[w v1 v2 ... vp] (p+1 éléments)
                index+=1
        objets_random=rand.sample(list(objets.items()),n)
        objets_random_dict={}
        i=0
        indices_from_objets_random_dict_to_objets={}
        for (index,elems) in objets_random:
            objets_random_dict[i]=elems
            indices_from_objets_random_dict_to_objets[i]=index
            W+=objets_random_dict[i][0]
            i+=1
    W=np.floor(W/2)
    return objets_random_dict,W,indices_from_objets_random_dict_to_objets


    