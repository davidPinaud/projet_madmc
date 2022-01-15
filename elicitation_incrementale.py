from graphs_and_stats import get_all_PLS_logs
import gurobipy as gp
from gurobipy import GRB
import random as rand
import numpy as np
import itertools as iter
from PLS import getEvaluation
import ast
import time
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
    sum=np.sum(poids)
    poids=[pi/sum for pi in poids]
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

def listEquals(l1,l2):
    for i,j in zip(l1,l2):
        if i!=j:
            return False
    return True
def getMR(PMR,x):
    max_regret=""
    for y,value in PMR[repr(x)].items():
        regret,m=value
        if max_regret=="":
            max_regret=(ast.literal_eval(y),(regret,m))
        else:
            max_regret=max_regret if max_regret[1][0]>regret else (ast.literal_eval(y),(regret,m))
    return max_regret #doublet (solution,(regret,m))

def elicitation_incrementale_somme_ponderee(p:int,X:list,nb_pref_connues:int,MMRlimit=0.001):
    #Poids réels du décideur
    decideur=getRandomPoids(p)
    print(f"décideur {decideur}")
    print(f"nb_pref_connues = {nb_pref_connues}")
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
    
    start=time.time()
    print(f"itération n°1")
    MMR=one_question_elicitation_somme_ponderee(X,preference,decideur)  #MMR de la forme (x,(y,(regret,model)))
    print(f"x : {MMR[0]}\ny : {MMR[1][0]} : regret : {MMR[1][1][0]}")
    nb_question=1

    while(MMR[1][1][0]>MMRlimit):
        print(f"\nitération n° {nb_question+1}\n")
        MMR=one_question_elicitation_somme_ponderee(X,preference,decideur)
        print(f"x : {MMR[0]}\ny : {MMR[1][0]} : regret : {MMR[1][1][0]}")
        nb_question+=1

    
    valeurOPT=0
    for p,x_i in zip(decideur,ast.literal_eval(MMR[0])):
        valeurOPT+=float(p)*x_i
    print(f"\nFIN:\nx : {MMR[0]}\ny : {MMR[1][0]}\nregret : {MMR[1][1][0]}\nvaleurOPT : {valeurOPT}\nnbQuestion : {nb_question} ")
    print(f"durée totale {time.time()-start}")
    for v in MMR[1][1][1].getVars():
       print(f"{v} = {v.x}")
    return MMR[0],nb_question,valeurOPT

def one_question_elicitation_somme_ponderee(X,preference,decideur):
    p=len(decideur) #nb de critère
    PMR={}
    for x in X:
        PMR[repr(x)]={}
    for x in X: #calcul de PMR(x,y) pour chaque couple de solutions restantes
        for y in X:
            if not listEquals(x,y):
                x=np.array(x)
                y=np.array(y)
                # Create a new model
                m = gp.Model(f"PMR_{x}_{y}")
                # Create variables
                w = m.addMVar(shape=p,vtype=GRB.CONTINUOUS, name="w")
                # Set objective
                m.setObjective((y @ w) - (x @ w), GRB.MAXIMIZE)
                # Add constraints:
                for i,(x_pref,y_pref) in enumerate(preference):
                    x_pref=np.array(x_pref)
                    y_pref=np.array(y_pref)
                    m.addConstr(x_pref @ w >= y_pref @ w,f"contrainte_{i}")

                l=[np.zeros(p) for _ in range(p)]
                for i,t in enumerate(l):
                    t[i]=1
                    m.addConstr(t @ w<=1)
                    m.addConstr(0<=t @ w)
                m.addConstr(np.ones(p) @ w==1)
                # Optimize model
                m.Params.LogToConsole = 0
                m.optimize()
                # print(f"x={x}\n")
                # print(f"y={y}\n")
                # print(m.display())
                if m.status == GRB.INFEASIBLE:
                    print("MODÈLE INFAISABLE")
                elif(m.status==GRB.OPTIMAL):
                    #print(f"Valeur Obj = {m.ObjVal}")
                    #for v in m.getVars():
                    #    print(f"{v} = {v.x}")
                    PMR[repr(list(x))][repr(list(y))]=(m.ObjVal,m) #regret
    

    MR={} #dictionnaire de doublet (solution,(regret,model)) = (y,(regret de prendre x au lieu de y,model))
    for x in X:
        MR[repr(x)]=getMR(PMR,x)
    # print("PMR",PMR.items())
    # print("\nMR",MR.items())
    MMR=min(MR.items(), key=lambda x:x[1][1][0]) # de la forme (x,(y,(regret,model)))

    x_etoile=ast.literal_eval(MMR[0])
    y_etoile=MMR[1][0]

    if domSommePonderee(decideur,x_etoile,y_etoile):
        preference.append((x_etoile,y_etoile))
    elif domSommePonderee(decideur,y_etoile,x_etoile):
        preference.append((y_etoile,x_etoile))
    else:
        pass
    return MMR
    
def elicitation_incrementale_OWA(p:int,X:list,nb_pref_connues:int,MMRlimit=0.001):
    #Poids réels du décideur
    decideur=getRandomPoids(p)
    decideur.sort(reverse=True)
    print(f"décideur {decideur}")
    print(f"nb_pref_connues = {nb_pref_connues}")
    for x in X:
        x.sort()
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
    
    start=time.time()
    print(f"itération n°1")
    MMR=one_question_elicitation_OWA(X,preference,decideur)  #MMR de la forme (x,(y,(regret,model)))
    print(f"x : {MMR[0]}\ny : {MMR[1][0]} : regret : {MMR[1][1][0]}")
    nb_question=1

    while(MMR[1][1][0]>MMRlimit):
        print(f"\nitération n° {nb_question+1}\n")
        MMR=one_question_elicitation_OWA(X,preference,decideur)
        print(f"x : {MMR[0]}\ny : {MMR[1][0]} : regret : {MMR[1][1][0]}")
        nb_question+=1

    
    valeurOPT=0
    for p,x_i in zip(decideur,ast.literal_eval(MMR[0])):
        valeurOPT+=float(p)*x_i
    print(f"\nFIN:\nx : {MMR[0]}\ny : {MMR[1][0]}\nregret : {MMR[1][1][0]}\nvaleurOPT : {valeurOPT}\nnbQuestion : {nb_question} ")
    print(f"durée totale {time.time()-start}")
    for v in MMR[1][1][1].getVars():
       print(f"{v} = {v.x}")
    return MMR[0],nb_question,valeurOPT


def one_question_elicitation_OWA(X,preference,decideur):
    p=len(decideur) #nb de critère
    PMR={}
    for x in X:
        PMR[repr(x)]={}
    for x in X: #calcul de PMR(x,y) pour chaque couple de solutions restantes
        for y in X:
            if not listEquals(x,y):
                x=np.array(x)
                y=np.array(y)
                # Create a new model
                m = gp.Model(f"PMR_{x}_{y}")
                # Create variables
                w = m.addMVar(shape=p,vtype=GRB.CONTINUOUS, name="w")
                # Set objective
                m.setObjective((y @ w) - (x @ w), GRB.MAXIMIZE)
                # Add constraints:
                for i,(x_pref,y_pref) in enumerate(preference):
                    x_pref=np.array(x_pref)
                    y_pref=np.array(y_pref)
                    m.addConstr(x_pref @ w >= y_pref @ w,f"contrainte_{i}")

                l=[np.zeros(p) for _ in range(p)]
                for i,t in enumerate(l):
                    t[i]=1
                    m.addConstr(t @ w<=1)
                    m.addConstr(0<=t @ w)
                m.addConstr(np.ones(p) @ w==1)
                for i in range(p-1):
                    m.addConstr(w[i]>=w[i+1])
                # Optimize model
                m.Params.LogToConsole = 0
                m.optimize()
                # print(f"x={x}\n")
                # print(f"y={y}\n")
                # print(m.display())
                if m.status == GRB.INFEASIBLE:
                    print("MODÈLE INFAISABLE")
                elif(m.status==GRB.OPTIMAL):
                    #print(f"Valeur Obj = {m.ObjVal}")
                    #for v in m.getVars():
                    #    print(f"{v} = {v.x}")
                    PMR[repr(list(x))][repr(list(y))]=(m.ObjVal,m) #regret
    

    MR={} #dictionnaire de doublet (solution,(regret,model)) = (y,(regret de prendre x au lieu de y,model))
    for x in X:
        MR[repr(x)]=getMR(PMR,x)
    # print("PMR",PMR.items())
    # print("\nMR",MR.items())
    MMR=min(MR.items(), key=lambda x:x[1][1][0]) # de la forme (x,(y,(regret,model)))

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
    p=4
    n=30
    for log in get_all_PLS_logs():
        if(log["logType"]=="PLS1" and log["n"]==n and log["p"]==p):
            nonDom=log["non_domines_approx"]
            objets=log["objets"]
            X=[getEvaluation(sol,objets) for sol in nonDom]
            break
    
    #elicitation_incrementale_somme_ponderee(p,X,nb_pref_connues=int(np.floor(len(nonDom)*0.20)))
    elicitation_incrementale_OWA(p,X,nb_pref_connues=int(np.floor(len(nonDom)*0.20)))



