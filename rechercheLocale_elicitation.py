#Auteur : David PINAUD

import ast
from time import perf_counter
import os
import datetime
from PLS import getEvaluation,genererSolutionInitiale,voisinage
from instance_loader import getInstance
import numpy as np
from elicitation_ponderee import elicitation_incrementale_somme_ponderee,getRandomPoids,getSommePondereeValue
from elicitation_OWA import elicitation_incrementale_OWA
from elicitation_choquet import elicitation_incrementale_choquet,getRandomCapacite,getChoquetValue
import copy
from graphs_and_stats import all_RL_elici_logs
import gurobipy as gp
from gurobipy import GRB


def rechercheLocale_plus_elicitation(objets, W, sol_init:list,voisinage,n:int,p:int,elicitation_name:str,verbose=True,pourMoyenne=False): #Approximation des points non-dominés
    #set up
    print(("\n\n"))
    
    if elicitation_name in ["SP","OWA","Choquet"]:
        if(verbose):
            print(f"\nElicitation avec {elicitation_name}, n={n}, p={p}")
        if elicitation_name=="SP":
            decideur=getRandomPoids(p)
            return compute_RL_plus_elicitation(sol_init,voisinage,n,p,elicitation_incrementale_somme_ponderee,objets,W,decideur,getSommePondereeValue,verbose,elicitation_name,pourMoyenne)
        elif elicitation_name=="OWA":
            decideur=getRandomPoids(p)
            decideur.sort(reverse=True)
            return compute_RL_plus_elicitation(sol_init,voisinage,n,p,elicitation_incrementale_OWA,objets,W,decideur,getSommePondereeValue,verbose,elicitation_name,pourMoyenne)
        elif elicitation_name=="Choquet":
            decideur=getRandomCapacite(p)
            return compute_RL_plus_elicitation(sol_init,voisinage,n,p,elicitation_incrementale_choquet,objets,W,decideur,getChoquetValue,verbose,elicitation_name,pourMoyenne)
    else:
        print("elicitation_name doit être égal à SP,OWA ou Choquet")
        return None

def compute_RL_plus_elicitation(sol_init:list,voisinage,n:int,p:int,elicitation_function,objets, W, decideur,valeur_function,verbose=True,elicitation_name="",pourMoyenne=False):
    
    MMRlimit=0.001
    log_all_iteration={
        "parameters" : {
            "sol_init":sol_init,
            "objets":objets,
            "voisinage":voisinage,
            "n":n,
            "p":p,
            "elicitation_function":elicitation_name,
            "W":W,
            "decideur":decideur,
            "valeur_function":valeur_function
        }
    }
    ite_counter=0
    sol_courante=sol_init.copy()
    optNotFound=True
    ite_limit=100
    sol_courante_avant=None
    while(optNotFound and ite_counter<ite_limit):
    #=====================start itération=====================
        t1_start = perf_counter()
        log_one_iteration={}
        #génération des voisin de la meilleure sol courante
        list_voisin=voisinage(sol_courante,objets, W)
        list_voisin.append(sol_courante) #la solution courante doit être dans la liste pour pouvoir être comparée
        #calculer les évaluations des voisins et en garder une trace de quel performance est relié à quel voisin
        eval_to_sol={}
        sol_to_eval={}
        X=[]
        for sol in list_voisin:
            eval=getEvaluation(sol,objets)
            X.append(eval)
            sol_to_eval[repr(sol)]=eval
            if(eval not in list(eval_to_sol.keys())):
                if (elicitation_name=="OWA" or elicitation_name=="Choquet"):
                    eval.sort()
                    eval_to_sol[repr(eval)]=sol
                else:
                    eval_to_sol[repr(eval)]=sol
            else:
                print("\n\n\nERREUR: deux solutions on exactement les mêmes performances\n\n\n")
                return None
        #calculer nombre de préférences connus du décideur
        nb_pref_connues=max(int(np.floor(len(list_voisin)*0.20)),min(p+2,len(X)-1))
        #elicitation
        solution_OPT_estimee,nb_question,valeur_sol_opt_estimee,decideur,duree=elicitation_function(p,X,nb_pref_connues,MMRlimit,decideur)

        t1_stop = perf_counter()

        #logger l'iteration
        log_one_iteration["sol_courante"]=sol_courante
        log_one_iteration["perf_sol_courante"]=sol_to_eval[repr(sol_courante)]
        log_one_iteration["valeur_sol_courante"]=valeur_function(decideur,getEvaluation(sol_courante,objets))

        if(solution_OPT_estimee in eval_to_sol.keys()):
            log_one_iteration["sol_solution_OPT_estimee"]=eval_to_sol[solution_OPT_estimee]
        else:
            temp=ast.literal_eval(solution_OPT_estimee).copy()
            temp.reverse()
            solution_OPT_estimee=repr(temp)
            print("\n\nkeys",eval_to_sol.keys())
            log_one_iteration["sol_solution_OPT_estimee"]=eval_to_sol[solution_OPT_estimee]
        log_one_iteration["solution_OPT_estimee"]=solution_OPT_estimee
        log_one_iteration["valeur_sol_opt_estimee"]=valeur_sol_opt_estimee

        log_one_iteration["eval_to_sol"]=eval_to_sol
        log_one_iteration["sol_to_eval"]=sol_to_eval

        log_one_iteration["nb_pref_connues"]=nb_pref_connues
        log_one_iteration["nb_question"]=nb_question
        log_one_iteration["dureeElicitation"]=duree
        log_one_iteration["dureeIteration"]=t1_stop-t1_start
        if(sol_courante_avant is not None and eval_to_sol[solution_OPT_estimee]==sol_courante_avant):#phénomène d'oscillation
            if verbose:
                print("\n\n=======Optimum trouvé=======\n\n")
            optNotFound=False
            log_one_iteration["changement_sol_courante"]=False
        elif(eval_to_sol[solution_OPT_estimee]==sol_courante):#on a trouvé le opt
            if verbose:
                print("\n\n=======Optimum trouvé=======\n\n")
            optNotFound=False
            log_one_iteration["changement_sol_courante"]=False
        else: #la solution trouvée est meilleure que la solution courante, on change de solution courante
            if verbose:
                print(f"\n\n=======Changement de solution courante, maintenant ={eval_to_sol[solution_OPT_estimee]} d'évaluation {solution_OPT_estimee} et de valeur {valeur_sol_opt_estimee}=======\n\n")
            sol_courante_avant=sol_courante
            sol_courante=eval_to_sol[solution_OPT_estimee]
            log_one_iteration["changement_sol_courante"]=True

        log_all_iteration[ite_counter]=log_one_iteration
        ite_counter+=1
        
    if verbose:
        print(f"\n\nUne solution localement optimale a été trouvée :{sol_courante} de performance {solution_OPT_estimee} et de valeur {log_one_iteration['valeur_sol_courante']} en {ite_counter} itération(s)")
        
    #=====================end itération=====================

    dirname = os.path.dirname(__file__)
    date=str(datetime.datetime.now()).replace(" ", "")
    if pourMoyenne :
        filename = os.path.join(dirname+f"/logs_RL_elici/{elicitation_name}_pour_moyenne", f"RL_elici_n_{n}_p_{p}_f_{elicitation_name}_{date}.txt")
    else:
        filename = os.path.join(dirname+f"/logs_RL_elici/{elicitation_name}", f"RL_elici_n_{n}_p_{p}_f_{elicitation_name}_{date}.txt")
    if(elicitation_name=="SP"):
        real_opt,real_solution_opt=getRealOptSolutionSP(objets,W,p,n,decideur)
    elif(elicitation_name=="OWA"):
        real_opt,real_solution_opt=getRealOptSolutionOWA(objets,W,p,n,decideur)
    else:
        real_opt,real_solution_opt=getRealOptSolutionChoquet(objets,W,p,n,decideur)
    real_gap=100-float(log_one_iteration["valeur_sol_opt_estimee"])*100/real_opt
    log_all_iteration["real_opt"]=real_opt
    log_all_iteration["real_solution_opt"]=real_solution_opt
    log_all_iteration["real_gap"]=real_gap
    print(f"\ngap : {max(0,real_gap)}<-------\n")
    log=open(filename,'w+')
    log.write(repr(log_all_iteration))
    log.close()
    print(f"=====FIN ELICITATION AVEC {elicitation_name}======\n\n")
    return sol_courante,solution_OPT_estimee,log_one_iteration['valeur_sol_courante'],ite_counter,log_all_iteration,decideur

def getRealOptSolutionSP(objets,W,p,n,decideur):
    SP_performances=[]
    for poids_et_perf in objets.values():
        SP_performances.append(getSommePondereeValue(decideur,poids_et_perf[1:]))
    SP_performances=np.array(SP_performances)
    poids=np.array([v[0] for v in objets.values()])
    #création du modèle
    m = gp.Model(f"opt_SP")
    x=m.addMVar(shape=n,vtype=GRB.BINARY, name="x")
    m.setObjective((SP_performances @ x), GRB.MAXIMIZE)
    m.addConstr(poids @ x <= W,f"contrainte_poids")
    m.optimize()

    if m.status == GRB.INFEASIBLE:
        print("MODÈLE INFAISABLE")
    elif(m.status==GRB.OPTIMAL):
        print(f"Valeur Obj = {m.ObjVal}")
        for v in m.getVars():
           print(f"{v} = {v.x}")
        #perf_solution_opt=[v.x*perf for v,perf in zip(m.getVars(),SP_performances)]
        perf_solution_opt=[]
        performances=[v[1:] for v in objets.values()]
        for critere in range(p):
            perf=0
            for i,v in enumerate(m.getVars()):
                perf+=int(v.x)*performances[i][critere]
            perf_solution_opt.append(perf)
    return m.ObjVal,perf_solution_opt
def getRealOptSolutionOWA(objets,W,p,n,decideur):
    decideur.sort()
    OWA_performances=[]
    for poids_et_perf in objets.values():
        perf_sorted=poids_et_perf[1:].copy()
        perf_sorted.sort()
        OWA_performances.append(getSommePondereeValue(decideur,perf_sorted))
    OWA_performances=np.array(OWA_performances)
    poids=np.array([v[0] for v in objets.values()])
    #création du modèle
    m = gp.Model(f"opt_SP")
    x=m.addMVar(shape=n,vtype=GRB.BINARY, name="x")
    m.setObjective((OWA_performances @ x), GRB.MAXIMIZE)
    m.addConstr(poids @ x <= W,f"contrainte_poids")
    m.optimize()

    if m.status == GRB.INFEASIBLE:
        print("MODÈLE INFAISABLE")
    elif(m.status==GRB.OPTIMAL):
        print(f"Valeur Obj = {m.ObjVal}")
        for v in m.getVars():
           print(f"{v} = {v.x}")
        #perf_solution_opt=[v.x*perf for v,perf in zip(m.getVars(),OWA_performances)]
        perf_solution_opt=[]
        performances=[v[1:] for v in objets.values()]
        for critere in range(p):
            perf=0
            for i,v in enumerate(m.getVars()):
                perf+=int(v.x)*performances[i][critere]
            perf_solution_opt.append(perf)
    return m.ObjVal,perf_solution_opt
def getRealOptSolutionChoquet(objets,W,p,n,decideur):
    choquetPerformances=[]
    for poids_et_perf in objets.values():
        perf_sorted=poids_et_perf[1:].copy()
        perf_sorted.sort()
        choquetPerformances.append(sum([perf_sorted[0]]+[(perf_sorted[i]-perf_sorted[i-1])*decideur.get_value(list(range(i,p))) for i in range(1,len(perf_sorted))]))
    choquetPerformances=np.array(choquetPerformances)
    poids=np.array([v[0] for v in objets.values()])
    #création du modèle
    m = gp.Model(f"opt_Choquet")
    x=m.addMVar(shape=n,vtype=GRB.BINARY, name="x")
    
    m.setObjective(choquetPerformances @ x, GRB.MAXIMIZE)
    m.addConstr(poids @ x <= W,f"contrainte_poids")
    m.optimize()

    if m.status == GRB.INFEASIBLE:
        print("MODÈLE INFAISABLE")
    elif(m.status==GRB.OPTIMAL):
        print(f"Valeur Obj = {m.ObjVal}")
        for v in m.getVars():
           print(f"{v} = {v.x}")
        #perf_solution_opt=[v.x*perf for v,perf in zip(m.getVars(),OWA_performances)]
        perf_solution_opt=[]
        performances=[v[1:] for v in objets.values()]
        for critere in range(p):
            perf=0
            for i,v in enumerate(m.getVars()):
                perf+=int(v.x)*performances[i][critere]
            perf_solution_opt.append(perf)
    return m.ObjVal,perf_solution_opt

if __name__== "__main__":
    n=13
    p=3
    objets, W=getInstance(n,p)
    sol_init=genererSolutionInitiale(objets, W)
    rechercheLocale_plus_elicitation(objets, W, copy.deepcopy(sol_init),voisinage,n,p,elicitation_name="SP",verbose=True,pourMoyenne=False)
    rechercheLocale_plus_elicitation(objets, W, copy.deepcopy(sol_init),voisinage,n,p,elicitation_name="OWA",verbose=True,pourMoyenne=False)
    rechercheLocale_plus_elicitation(objets, W, copy.deepcopy(sol_init),voisinage,n,p,elicitation_name="Choquet",verbose=True,pourMoyenne=False)