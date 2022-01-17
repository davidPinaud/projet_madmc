from audioop import maxpp
import datetime
import enum
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
from elicitation_ponderee import getMR,listEquals


class Capacite():
    """Wrapper pour un dictionnaire qui représente une capacité
    """
    def __init__(self,p) -> None:
        self.cap={}
        self.p=p
    def set_cap(self,A:list,value):
        self.cap[repr(A)]=value
    def get_value(self,A:list):
        """renvoi la capacité pour l'ensemble A

        Parameters
        ----------
        A : list
            ensemble pour lequel on veut le capacité

        Returns
        -------
        float
            la capacité de A
        """
        if repr(A) in self.cap.keys():
            return self.cap[repr(A)]
        else:
            print(f"PAS DE CAPACITÉ POUR LA VALEUR {A}")
            return None
    def __repr__(self):
        return str(self.cap)

def getChoquetValue(capacite,x):
    """Fonction qui retourne la valeur de Choquet d'une solution x avec la capacité "capacite"

    Parameters
    ----------
    capacite : capacite
        capacité pour laquelle calculer la valeur de Choquet
    x : list
        une solution à évaluer

    Returns
    -------
    float
        Valeur de choquet de x avec la capacité capacite
    """
    choquet_x=0
    p=len(x)
    for i,x_i in enumerate(x):
        if(i==0):
            choquet_x+=x_i #( on doit faire x1 normalement mais ça sert à rien)
        else:
            choquet_x+=(x_i-x[i-1])*capacite.get_value(list(range(i,p)))
    return choquet_x

def domChoquet(capacite,x,y):
    """retourne un booleen à vrai si x domine y au sens de choquet avec la capacite donnée

    Parameters
    ----------
    capacite : capacite
        capacité pour laquelle calculer la valeur de Choquet
    x : list
        une solution à comparer
    y : list
        une solution à comparer

    Returns
    -------
    boolean
        True si x domine y au sens de choquet avec la capacite donnée, False sinon
    """
    return getChoquetValue(capacite,x)>=getChoquetValue(capacite,y)

def getAllSet(p):
    """Retourne tous les sous ensemble de l'ensemble {0,1,..,p-1}

    Parameters
    ----------
    p : int
        taille du plus grand ensemble que prendra la capacité
    Returns
    -------
    list of list
        listes correpondantx aux sous ensemble de l'ensemble {0,1,..,p-1}
    """
    E=[]
    for k in range(0,p+1):
        A_de_taille_k=list(iter.combinations(range(p),k))
        E+=A_de_taille_k
    return [list(e) for e in E]

def getRandomCapacite(p:int):
    """Retourne une capacité totalement aléatoire

    Parameters
    ----------
    p : int
        taille du plus grand ensemble que prendra la capacité

    Returns
    -------
    capacite
        une capacité aléatoire
    """
    capacite=Capacite(p)
    capacite.set_cap([],0)
    values=[rand.random() for _ in range(2**p-2)]
    values.sort()
    i=0
    for k in range(1,p):
        A_de_taille_k=list(iter.combinations(range(p),k))
        local_values=values.copy()[i:i+len(A_de_taille_k)]
        i+=len(local_values)
        rand.shuffle(local_values)
        for j,A in enumerate(A_de_taille_k):
            capacite.set_cap(list(A),local_values[j])
    capacite.set_cap(list(range(p)),1)
    return capacite

def elicitation_incrementale_choquet(p:int,X:list,nb_pref_connues:int,MMRlimit=0.001,decideur=None):
    """Permet de lancer l'élicitation incrémentale des préférences d'un décideur choisis au hasard
    dont les préférences sont représentés par le critère de choquet. On fait l'hypothèse qu'on connait un nombre 
    "nb_pref_connues" de préférences du décideur

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
        decideur=getRandomCapacite(p)
    print(f"décideur {decideur}")
    if(len(X)==1):
        print("Une seule solution possible dans X ! C'est l'optimal")
        valeurOPT=getChoquetValue(decideur,X[0])
        return repr(X[0]),0,valeurOPT,decideur,0
    print(f"nb_pref_connues = {nb_pref_connues}")
    for x in X:
        x.sort()
    #Création de nb_pref_connues contraintes (préférences connues)
    allPairsSolutions=list(iter.combinations(X,2))
    solution_init_pref=rand.choices(allPairsSolutions,k=nb_pref_connues)
    preference=[] #P
    for x,y in solution_init_pref:
        if domChoquet(decideur,x,y):
            preference.append((x,y))
        elif domChoquet(decideur,y,x):
            preference.append((y,x))
        else:
            pass
    
    start=time.time()
    print(f"itération n°1")
    MMR=one_question_elicitation_choquet(X,preference,decideur)  #MMR de la forme (x,(y,(regret,model)))
    print(f"Question : \nx : {MMR[0]}\ny : {MMR[1][0]}\nregret : {MMR[1][1][0]}")
    nb_question=1

    while(MMR[1][1][0]>MMRlimit):
        print(f"\nitération n° {nb_question+1}\n")
        MMR=one_question_elicitation_choquet(X,preference,decideur)
        print(f"Question : \nx : {MMR[0]}\ny : {MMR[1][0]}\nregret : {MMR[1][1][0]}")
        nb_question+=1

    
    valeurOPT=getChoquetValue(decideur,[float(e) for e in ast.literal_eval(MMR[0])])
    print(f"\nFIN:\nx : {MMR[0]}\ny : {MMR[1][0]}\nregret : {MMR[1][1][0]}\nvaleurOPT : {valeurOPT}\nnbQuestion : {nb_question}\n")
    duree=time.time()-start
    print(f"durée totale {duree}")
    for v in MMR[1][1][1].getVars():
       print(f"{v} = {v.x}")
    #print(f"décideur {decideur}")
    return MMR[0],nb_question,valeurOPT,decideur,duree


def one_question_elicitation_choquet(X,preference,decideur):
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
    p=len(X[0]) #nb de critère
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
                E=getAllSet(p)
                vars={}
                for A in E:
                    vars[repr(A)]=m.addVar(vtype=GRB.CONTINUOUS, name=f"{A}")
                # Set objective
                choquet_y=0
                choquet_x=0
                for i,y_i in enumerate(x):
                    if(i==0):
                        choquet_y+=y_i #( on doit faire x1 normalement mais ça sert à rien)
                    else:
                        #choquet_y+=(y_i-x[i-1])*m.getVarByName(f"{list(range(i,p))}")
                        choquet_y+=(y_i-x[i-1])*vars[repr(list(range(i,p)))]
                for i,x_i in enumerate(x):
                    if(i==0):
                        choquet_x+=x_i #( on doit faire x1 normalement mais ça sert à rien)
                    else:
                        # choquet_x+=(x_i-x[i-1])*m.getVarByName(f"{list(range(i,p))}")
                        choquet_x+=(x_i-x[i-1])*vars[repr(list(range(i,p)))]
                m.setObjective(choquet_y-choquet_x, GRB.MAXIMIZE)
                # Add constraints:
                for i,(x_pref,y_pref) in enumerate(preference):
                    x_pref=np.array(x_pref)
                    y_pref=np.array(y_pref)
                    for i,y_i in enumerate(y_pref):
                        if(i==0):
                            choquet_y+=y_i #( on doit faire x1 normalement mais ça sert à rien)
                        else:
                            choquet_y+=(y_i-x[i-1])*vars[repr(list(range(i,p)))]
                    for i,x_i in enumerate(x_pref):
                        if(i==0):
                            choquet_x+=x_i #( on doit faire x1 normalement mais ça sert à rien)
                        else:
                            choquet_x+=(x_i-x[i-1])*vars[repr(list(range(i,p)))]
                    m.addConstr(choquet_x >= choquet_y,f"contrainte_{i}")

                # m.addConstr(m.getVarByName(f"{[]}")==0)
                # m.addConstr(m.getVarByName(f"{list(range(p))}")==1)
                m.addConstr(vars[repr([])]==0)
                m.addConstr(vars[repr(list(range(p)))]==1)

                for i in range(p):
                    All_A_sans_i=[A for A in E if i not in A]
                    for A in All_A_sans_i:
                        A_avec_i=A.copy()
                        # for index,Ai in enumerate(A_avec_i):#il faut mettre le i au bon endroit sinon il ne vas pas reconnaitre la clé
                        #     if(index == len(A_avec_i)-1):
                        #         A_avec_i.append(i)
                        #         break
                        #     if(Ai<=i and A_avec_i[index+1]>=i):
                        #         A_avec_i.insert(index+1,i)
                        #         break
                        #m.addConstr(m.getVarByName(f"{A}")<=m.getVarByName(f"{A_avec_i}"))
                        A_avec_i.append(i)
                        A.sort()
                        A_avec_i.sort()
                        m.addConstr(vars[repr(A)]<=vars[repr(A_avec_i)])

                
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

    if domChoquet(decideur,x_etoile,y_etoile):
        preference.append((x_etoile,y_etoile))
    elif domChoquet(decideur,y_etoile,x_etoile):
        preference.append((y_etoile,x_etoile))
    else:
        pass
    return MMR


def getSolutionOptChoquet(X:list,capacite_decideur:list):
    """Retourne la solution optimale si les préférences du décideur est
    modélisé par le critère de Choquet

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
    valeursChoquet=[(x,getChoquetValue(capacite_decideur,x)) for x in X]
    return max(valeursChoquet,key=lambda x:x[1])

if __name__== "__main__":
    # p=4
    # n=18
    # for log in get_all_PLS_logs():
    #     if(log["logType"]=="PLS1" and log["n"]==n and log["p"]==p):
    #         nonDom=log["non_domines_approx"]
    #         objets=log["objets"]
    #         X=[getEvaluation(sol,objets) for sol in nonDom]
    #         break
    # elicitation_incrementale_choquet(p,X,nb_pref_connues=int(np.floor(len(nonDom)*0.20)))

    all_p=[5]
    all_n=list(range(5,26))
    for n in all_n:
        for p in all_p:
            log_PLS=get_one_PLS_log("PLS1",n,p)
            nonDom=log_PLS["non_domines_approx"]
            objets=log_PLS["objets"]
            X=[getEvaluation(sol,objets) for sol in nonDom]
            
            solution_optimale_estimee,nb_question,valeur_sol_estimee,decideur,duree=elicitation_incrementale_choquet(p,X,nb_pref_connues=max(int(np.floor(len(nonDom)*0.20)),p+1))
            
            solution_optimale,valeur_sol_optimale=getSolutionOptChoquet(X,decideur)

            solution_optimale=[int(e) for e in solution_optimale]
            solution_optimale_estimee=ast.literal_eval(solution_optimale_estimee)
            solution_optimale_estimee=[int(e) for e in solution_optimale_estimee]
            if(listEquals(solution_optimale,solution_optimale_estimee)):
                print(f"\nOn a trouvé la même solution optimale {solution_optimale} de valeur {valeur_sol_optimale}")
            else:
                print(f"\nLes solutions \"optimale\" et \"optimale estimée\" sont différentes :\n\
        optimale :{solution_optimale} de valeur : {valeur_sol_optimale}\n\
        estimee:{solution_optimale_estimee} de valeur : {valeur_sol_estimee}\n\
        \nSoit un gap de {100-valeur_sol_estimee*100/valeur_sol_optimale} %")
            
            dirname = os.path.dirname(__file__)
            date=str(datetime.datetime.now()).replace(" ", "")
            filename = os.path.join(dirname+"/logs_Choquet", f"Choquet_n_{n}_p_{p}_{date}.txt")
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


