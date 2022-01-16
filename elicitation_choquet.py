import enum
from graphs_and_stats import get_all_PLS_logs
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
    choquet_x=0
    p=len(x)
    for i,x_i in enumerate(x):
        if(i==0):
            choquet_x+=x_i #( on doit faire x1 normalement mais ça sert à rien)
        else:
            choquet_x+=(x_i-x[i-1])*capacite.get_value(list(range(i,p+1)))
    return choquet_x

def domChoquet(capacite,x,y):
    return getChoquetValue(capacite,x)>=getChoquetValue(capacite,y)

def getAllSet(p):
    E=[]
    for k in range(0,p+1):
        A_de_taille_k=list(iter.combinations(range(p),k))
        E+=A_de_taille_k
    return E

def getRandomCapacite(p:int):
    capacite=Capacite(p)
    capacite.set_cap([],0)
    capacite.set_cap(list(range(p)),1)

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

    return capacite

def elicitation_incrementale_choquet(p:int,X:list,nb_pref_connues:int,MMRlimit=0.001):
    #Poids réels du décideur
    decideur=getRandomCapacite(p)
    print(f"décideur {decideur}")
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
    print(f"x : {MMR[0]}\ny : {MMR[1][0]} : regret : {MMR[1][1][0]}")
    nb_question=1

    while(MMR[1][1][0]>MMRlimit):
        print(f"\nitération n° {nb_question+1}\n")
        MMR=one_question_elicitation_choquet(X,preference,decideur)
        print(f"x : {MMR[0]}\ny : {MMR[1][0]} : regret : {MMR[1][1][0]}")
        nb_question+=1

    
    valeurOPT=0
    for p,x_i in zip(decideur,ast.literal_eval(MMR[0])):
        valeurOPT+=float(p)*x_i
    print(f"\nFIN:\nx : {MMR[0]}\ny : {MMR[1][0]}\nregret : {MMR[1][1][0]}\nvaleurOPT : {valeurOPT}\nnbQuestion : {nb_question} ")
    print(f"durée totale {time.time()-start}")
    for v in MMR[1][1][1].getVars():
       print(f"{v} = {v.x}")
    #print(f"décideur {decideur}")
    return MMR[0],nb_question,valeurOPT


def one_question_elicitation_choquet(X,preference,decideur):
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
                for A in E:
                    m.addVar(vtype=GRB.CONTINUOUS, name=f"{A}")
                # Set objective
                choquet_y=0
                choquet_x=0
                for i,y_i in enumerate(x):
                    if(i==0):
                        choquet_y+=y_i #( on doit faire x1 normalement mais ça sert à rien)
                    else:
                        choquet_y+=(y_i-x[i-1])*m.getVarByName(f"{list(range(i,p+1))}")
                for i,x_i in enumerate(x):
                    if(i==0):
                        choquet_x+=x_i #( on doit faire x1 normalement mais ça sert à rien)
                    else:
                        choquet_x+=(x_i-x[i-1])*m.getVarByName(f"{list(range(i,p+1))}")
                m.setObjective(choquet_y-choquet_x, GRB.MAXIMIZE)
                # Add constraints:
                for i,(x_pref,y_pref) in enumerate(preference):
                    x_pref=np.array(x_pref)
                    y_pref=np.array(y_pref)
                    for i,y_i in enumerate(y_pref):
                        if(i==0):
                            choquet_y+=y_i #( on doit faire x1 normalement mais ça sert à rien)
                        else:
                            choquet_y+=(y_i-x[i-1])*m.getVarByName(f"{list(range(i,p+1))}")
                    for i,x_i in enumerate(x_pref):
                        if(i==0):
                            choquet_x+=x_i #( on doit faire x1 normalement mais ça sert à rien)
                        else:
                            choquet_x+=(x_i-x[i-1])*m.getVarByName(f"{list(range(i,p+1))}")
                    m.addConstr(choquet_x >= choquet_y,f"contrainte_{i}")

                m.addConstr(m.getVarByName(f"{[]}")==0)
                m.addConstr(m.getVarByName(f"{list(range(p+1))}")==0)

                ####JUSQUA ICI C'EST BON
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
    # p=4
    # n=18
    # for log in get_all_PLS_logs():
    #     if(log["logType"]=="PLS1" and log["n"]==n and log["p"]==p):
    #         nonDom=log["non_domines_approx"]
    #         objets=log["objets"]
    #         X=[getEvaluation(sol,objets) for sol in nonDom]
    #         break



    # elicitation_incrementale_somme_ponderee(p,X,nb_pref_connues=int(np.floor(len(nonDom)*0.20)))
    # #elicitation_incrementale_OWA(p,X,nb_pref_connues=int(np.floor(len(nonDom)*0.20)))



