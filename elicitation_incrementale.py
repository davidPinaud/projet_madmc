from graphs_and_stats import get_all_PLS_logs
import gurobipy as gp
from gurobipy import GRB
import random as rand
import numpy as np
import itertools as iter
from PLS import getEvaluation
import ast
#normaliser : diviser par le premier maximum regret


def getRandomPoids(p:int):
    """retourne un vecteur de p poids au hasard normalisé à 1

    Parameters
    ----------
    p : int
        le nombre de poids dans le vecteur

    Returns
    -------
    list
        liste de p poids
    """
    poids=[rand.random() for _ in range(p)]
    max=np.max(poids)
    poids=[pi/max for pi in poids]
    return poids

def domSommePonderee(poids,x,y):
    """Retourne un booleen qui indique la préférence entre deux solutions x et y selon la somme pondérée par les poids "poids

    Parameters
    ----------
    poids : list
        pondération
    x : list
        solution 1 à comparer
    y : list
        solution 2 à comparer

    Returns
    -------
    booleen
        True si x preféré à y, False sinon
    """
    f_x=0
    f_y=0
    for p,x_i in zip(poids,x):
        f_x+=p*x_i
    for p,y_i in zip(poids,y):
        f_y+=p*y_i
    return f_x>f_y

def getMR(PMR,x):
    max_regret=""
    for y,regret in PMR[repr(x)].items():
        if max_regret=="":
            max_regret=(ast.literal_eval(y),regret)
        else:
            max_regret=max_regret if max_regret[1]>regret else (ast.literal_eval(y),regret)
    return max_regret #doublet (solution,regret)

# X: ens des potentiellement non dominés
def elicitation_incrementale_somme_ponderee(p:int,X:list,nb_pref_connues:int,MMRlimit=0):
    #Poids réels du décideur
    decideur=getRandomPoids(p)
    print(f"décideur {decideur}")
    #Création de nb_pref_connues contraintes (préférences connues)
    allPairsSolutions=list(iter.combinations(X,2))
    solution_init_pref=rand.choices(allPairsSolutions,k=nb_pref_connues)
    preference=[] #P
    for x,y in solution_init_pref:
        if domSommePonderee(decideur,x,y):
            preference.append((x,y))
        elif domSommePonderee(decideur,y,x):
            preference.append((y,x))
        else:
            pass
    
    
    MMR=one_question_elicitation_somme_ponderee(X,allPairsSolutions,preference,decideur)
    nb_question=1
    while(MMR[1][1]>MMRlimit):
        print(f"x : {MMR[0]}\ny : {MMR[1][0]} : regret : {MMR[1][1]}")
        MMR=one_question_elicitation_somme_ponderee(X,allPairsSolutions,preference,decideur)
        nb_question+=1

    valeurOPT=0
    for p,x_i in zip(decideur,MMR[0]):
        valeurOPT+=p*x_i
    return MMR[0],nb_question,valeurOPT

def one_question_elicitation_somme_ponderee(X,allPairsSolutions,preference,decideur):
    p=len(decideur) #nb de critère
    PMR={}
    for x in X:
        PMR[repr(x)]={}
    for x,y in allPairsSolutions: #calcul de PMR(x,y) pour chaque couple de solutions restantes
        x=np.array(x)
        y=np.array(y)
        # Create a new model
        m = gp.Model("elicitation_somme_ponderee")
        # Create variables
        w = m.addMVar(shape=p,vtype=GRB.CONTINUOUS, name="w")
        # Set objective
        m.setObjective((y @ w) - (x @ w), GRB.MAXIMIZE)
        # Add constraints:
        for i,(x_pref,y_pref) in enumerate(preference):
            m.addConstr(x_pref @ w >= y_pref @ w,f"contrainte_{i}")
        # Optimize model
        m.optimize()

        PMR[repr(x)][repr(y)]=m.ObjVal

    MR={} #dictionnaire de doublet (solution,regret) = (y,regret de prendre x au lieu de y)
    for x in X:
        MR[repr(x)]=getMR(PMR,x)
    MMR=min(MR.items(), key=lambda x:x[1][1]) # de la forme (x,(y,regret))

    x_etoile=ast.literal_eval(MMR[0])
    y_etoile=MMR[1][0]

    if domSommePonderee(decideur,x_etoile,y_etoile):
        preference.append((x_etoile,y_etoile))
    elif domSommePonderee(decideur,y_etoile,x_etoile):
        preference.append((y_etoile,x_etoile))
    else:
        pass
    return MMR
    

if __name__== "__main__":
    p=3
    n=21
    for log in get_all_PLS_logs():
        if(log["logType"]=="PLS1" and log["n"]==n and log["p"]==p):
            nonDom=log["non_domines_approx"]
            objets=log["objets"]
            X=[getEvaluation(sol,objets) for sol in nonDom]
            break
    
    elicitation_incrementale_somme_ponderee(p,X,nb_pref_connues=int(np.floor(len(nonDom)*0.20)))



