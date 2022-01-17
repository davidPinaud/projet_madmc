import datetime
import json
import os
from graphs_and_stats import get_one_PLS_log
import gurobipy as gp
from gurobipy import GRB
import random as rand
import numpy as np
import itertools as iter
from PLS import getEvaluation
import ast
import time
from elicitation_ponderee import getMR,getRandomPoids,domSommePonderee,listEquals,getSommePondereeValue

    
def elicitation_incrementale_OWA(p:int,X:list,nb_pref_connues:int,MMRlimit=0.001,decideur=None):
    """Permet de lancer l'élicitation incrémentale des préférences d'un décideur choisis au hasard
    dont les préférences sont représentés par un OWA. On fait l'hypothèse qu'on connait un nombre 
    "nb_pref_connues" de préférences du décideur et que les ses poids (au décideur) sont décroissant (on cherche donc des solutions équitables)

    Parameters
    ----------
    p : int
        nombre de critère
    X : list
        liste des solutions à considérer, ce sont des solutions potentiellement pareto optimales calculés avec PLS
    nb_pref_connues : int
        nombre de préférences connues du décideur
    MMRlimit : float, optional
        limite sur laquelle on arrête l'élicitation, cette valeur doit être supérieure ou égale à 0
        car quand MMR<0, cela voudrait dire qu'il existe une solution que l'on regrettera jamais de prendre
        c'est à dire que c'est la solution optimale, by default 0.001

    Returns
    -------
    list, int, float, list
        La solution optimale estimée, le nombre de question posé,
         la valeur pour le décideur de la solution optimale estimée et les poids du décideur
    """
    #Poids réels du décideur
    if decideur==None:
        decideur=getRandomPoids(p)
    decideur.sort(reverse=True)
    print(f"décideur {decideur}")
    if(len(X)==1):
        print("Une seule solution possible dans X ! C'est l'optimal")
        valeurOPT=0
        X[0].sort()
        for p,x_i in zip(decideur,X[0]):
            valeurOPT+=float(p)*x_i
        return repr(X[0]),0,valeurOPT,decideur,0
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
    print(f"Question : \nx : {MMR[0]}\ny : {MMR[1][0]}\nregret : {MMR[1][1][0]}")
    nb_question=1

    while(MMR[1][1][0]>MMRlimit):
        print(f"\nitération n° {nb_question+1}\n")
        MMR=one_question_elicitation_OWA(X,preference,decideur)
        print(f"Question : \nx : {MMR[0]}\ny : {MMR[1][0]}\nregret : {MMR[1][1][0]}")
        nb_question+=1

    
    valeurOPT=0
    for p,x_i in zip(decideur,ast.literal_eval(MMR[0])):
        valeurOPT+=float(p)*x_i
    print(f"\nFIN:\nx : {MMR[0]}\ny : {MMR[1][0]}\nregret : {MMR[1][1][0]}\nvaleurOPT : {valeurOPT}\nnbQuestion : {nb_question}\n")
    duree=time.time()-start
    print(f"durée totale {duree}")
    for v in MMR[1][1][1].getVars():
       print(f"{v} = {v.x}")
    print(f"décideur {decideur}")
    return MMR[0],nb_question,valeurOPT,decideur,duree


def one_question_elicitation_OWA(X,preference,decideur):
    """Permet de :
    - calculer les PMR
    - en déduire les MR
    - en déduire le MMR
    - en déduire la question, la poser et agir en conséquences sur l'espaces des poids
    C'est en fait une étape de l'élicitation : trouver la meilleure question qui va le plus 
    couper l'espace des poids et la poser.

    Parameters
    ----------
    X : list
        liste de toutes les solutions potentiellement pareto optimale trouvées avec PLS
    preference : list
        liste de doublet qui indique les préférences du décideur entre des solutions de X
    decideur : list
        liste des poids du décideur

    Returns
    -------
    tuple
        renvoi un tuple de la forme (x,(y,(regret,modèle))) avec x le MMR, y le "meilleur adversaire de x"
        (celui auquel il faut poser la question au décideur s'il préfère x ou y), regret le regret de prendre x
        au lieu de y et modèle le modèle (PL) qui a permi de calculer ce regret
    """
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


def getSolutionOptOWA(X:list,poids_decideur:list):
    """Retourne la solution optimale si les préférences du décideur est
    modélisé par un OWA
    Parameters
    ----------
    X : list
        liste de toutes les solutions potentiellement pareto optimale trouvées avec PLS
    poids_decideur : list
        liste des poids du décideur

    Returns
    -------
    tuple
        double de la forme (solution optimale, valeur de la solution optimale pour le décideur)
    """
    for x in X:
        x.sort()
    valeursSP=[(x,getSommePondereeValue(poids_decideur,x)) for x in X]
    return max(valeursSP,key=lambda x:x[1])

if __name__== "__main__":
    # p=4
    # n=18
    # for log in get_all_PLS_logs():
    #     if(log["logType"]=="PLS1" and log["n"]==n and log["p"]==p):
    #         nonDom=log["non_domines_approx"]
    #         objets=log["objets"]
    #         X=[getEvaluation(sol,objets) for sol in nonDom]
    #         break
    all_p=[5]
    all_n=list(range(5,26))
    for n in all_n:
        for p in all_p:
            log_PLS=get_one_PLS_log("PLS1",n,p)
            nonDom=log_PLS["non_domines_approx"]
            objets=log_PLS["objets"]
            X=[getEvaluation(sol,objets) for sol in nonDom]
            
            solution_optimale_estimee,nb_question,valeur_sol_estimee,decideur,duree=elicitation_incrementale_OWA(p,X,nb_pref_connues=int(np.floor(len(nonDom)*0.20)))
            
            solution_optimale,valeur_sol_optimale=getSolutionOptOWA(X,decideur)

            solution_optimale=[int(e) for e in solution_optimale]
            solution_optimale_estimee=ast.literal_eval(solution_optimale_estimee)
            solution_optimale_estimee=[int(e) for e in solution_optimale_estimee]
            if(listEquals(solution_optimale,solution_optimale_estimee)):
                print(f"On a trouvé la même solution optimale {solution_optimale} de valeur {valeur_sol_optimale}")
            else:
                print(f"Les solutions \"optimale\" et \"optimale estimée\" sont différentes :\n\
        optimale :{solution_optimale} de valeur : {valeur_sol_optimale}\n\
        estimee:{solution_optimale_estimee} de valeur : {valeur_sol_estimee}\n\
        \nSoit un gap de {100-valeur_sol_estimee*100/valeur_sol_optimale} %")

            dirname = os.path.dirname(__file__)
            date=str(datetime.datetime.now()).replace(" ", "")
            filename = os.path.join(dirname+"/logs_OWA", f"OWA_n_{n}_p_{p}_{date}.txt")
            log=open(filename,'w+')
            log.write("log\n")
            log.write(json.dumps(log_PLS))
            log.write("\n\n")
            log.write("Evaluations\n")
            log.write(str(X))
            log.write("\n\n")
            log.write("solution_optimale_estimee\n")
            log.write(str(solution_optimale_estimee))
            log.write("\n\n")
            log.write("nb_question\n")
            log.write(str(nb_question))
            log.write("\n\n")
            log.write("valeur_sol_estimee\n")
            log.write(str(valeur_sol_estimee))
            log.write("\n\n")
            log.write("decideur\n")
            log.write(str(decideur))
            log.write("\n\n")
            log.write("solution_optimale\n")
            log.write(str(solution_optimale))
            log.write("\n\n")
            log.write("valeur_sol_optimale\n")
            log.write(str(valeur_sol_optimale))
            log.write("\n\n")
            log.write("duree\n")
            log.write(str(duree))
            log.write("\n\n")
            log.write("gap(%)\n")
            log.write(str(100-valeur_sol_estimee*100/valeur_sol_optimale))
            log.close()
    


