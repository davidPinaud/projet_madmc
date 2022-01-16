import json
from time import perf_counter
import os
import datetime
from PLS import getEvaluation,genererSolutionInitiale,voisinage
from instance_loader import getInstance
import numpy as np
from elicitation_ponderee import elicitation_incrementale_somme_ponderee,getRandomPoids,getSommePondereeValue
from elicitation_OWA import elicitation_incrementale_OWA
from elicitation_choquet import elicitation_incrementale_choquet,getRandomCapacite,getChoquetValue

def rechercheLocale_plus_elicitation(objets, W, sol_init:list,voisinage,n:int,p:int,elicitation_name:str,verbose=True): #Approximation des points non-dominés
    #set up
    print(("\n\n"))
    
    if elicitation_name in ["SP","OWA","Choquet"]:
        if(verbose):
            print(f"\nElicitation avec {elicitation_name}")
        if elicitation_name=="SP":
            decideur=getRandomPoids(p)
            return compute_RL_plus_elicitation(sol_init,voisinage,n,p,elicitation_incrementale_somme_ponderee,objets,W,decideur,getSommePondereeValue,verbose)
        elif elicitation_name=="OWA":
            decideur=getRandomPoids(p)
            decideur.sort(reverse=True)
            return compute_RL_plus_elicitation(sol_init,voisinage,n,p,elicitation_incrementale_OWA,objets,W,decideur,getSommePondereeValue,verbose)
        elif elicitation_name=="Choquet":
            decideur=getRandomCapacite(p)
            return compute_RL_plus_elicitation(sol_init,voisinage,n,p,elicitation_incrementale_choquet,objets,W,decideur,getChoquetValue,verbose)
    else:
        print("elicitation_name doit être égal à SP,OWA ou Choquet")
        return None

def compute_RL_plus_elicitation(sol_init:list,voisinage,n,p:int,elicitation_function,objets, W, decideur,valeur_function,verbose=True):
    
    MMRlimit=0.001
    log_all_iteration={
        "parameters" : {
            "sol_init":sol_init,
            "voisinage":voisinage,
            "p":p,
            "elicitation_function":elicitation_function,
            "W":W,
            "decideur":decideur,
            "valeur_function":valeur_function
        }
    }
    ite_counter=0
    sol_courante=sol_init.copy()
    optNotFound=True
    while(optNotFound):
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
                eval_to_sol[repr(eval)]=sol
            else:
                print("\n\n\nERREUR: deux solutions on exactement les mêmes performances\n\n\n")
                return None
        #calculer nombre de préférences connus du décideur
        nb_pref_connues=int(np.floor(len(list_voisin)*0.20))
        #elicitation
        solution_OPT_estimee,nb_question,valeur_sol_opt_estimee,decideur,duree=elicitation_function(p,X,nb_pref_connues,MMRlimit,decideur)

        t1_stop = perf_counter()

        #logger l'iteration
        log_one_iteration["sol_courante"]=sol_courante
        log_one_iteration["perf_sol_courante"]=sol_to_eval[repr(sol_courante)]
        log_one_iteration["valeur_sol_courante"]=valeur_function(decideur,sol_courante)

        log_one_iteration["sol_solution_OPT_estimee"]=eval_to_sol[solution_OPT_estimee]
        log_one_iteration["solution_OPT_estimee"]=solution_OPT_estimee
        log_one_iteration["valeur_sol_opt_estimee"]=valeur_sol_opt_estimee

        log_one_iteration["eval_to_sol"]=eval_to_sol
        log_one_iteration["sol_to_eval"]=sol_to_eval

        log_one_iteration["nb_pref_connues"]=nb_pref_connues
        log_one_iteration["nb_question"]=nb_question
        log_one_iteration["dureeElicitation"]=duree
        log_one_iteration["dureeIteration"]=t1_stop-t1_start

        if(eval_to_sol[solution_OPT_estimee]==sol_courante):#on a trouvé le opt
            if verbose:
                print("\n\n=======Optimum trouvé=======\n\n")
            optNotFound=False
            log_one_iteration["changement_sol_courante"]=False
        else: #la solution trouvée est meilleure que la solution courante, on change de solution courante
            if verbose:
                print(f"\n\n=======Changement de solution courante, maintenant ={eval_to_sol[solution_OPT_estimee]} d'évaluation {solution_OPT_estimee} et de valeur {valeur_sol_opt_estimee}=======\n\n")
            sol_courante=eval_to_sol[solution_OPT_estimee]
            log_one_iteration["changement_sol_courante"]=True

        log_all_iteration[ite_counter]=log_one_iteration
        ite_counter+=1
        
    if verbose:
        print(eval_to_sol)
        print(f"\n\nUne solution localement optimale a été trouvée :{sol_courante} de performance {solution_OPT_estimee} et de valeur {log_one_iteration['valeur_sol_courante']}\n\
en {ite_counter} itération(s)")
        
    #=====================end itération=====================

    dirname = os.path.dirname(__file__)
    date=str(datetime.datetime.now()).replace(" ", "")
    filename = os.path.join(dirname+"/logs_RL_elici", f"RL_elici_n_{n}_p_{p}_f_{elicitation_function}_{date}.txt")
    log=open(filename,'w+')
    log.write(repr(log_all_iteration))
    log.close()
    return sol_courante,solution_OPT_estimee,log_one_iteration['valeur_sol_courante'],ite_counter,log_all_iteration,decideur


if __name__== "__main__":
    n=30
    p=3
    objets, W=getInstance(n,p)
    sol_init=genererSolutionInitiale(objets, W)
    rechercheLocale_plus_elicitation(objets, W, sol_init,voisinage,n,p,elicitation_name="SP",verbose=True)
    #rechercheLocale_plus_elicitation(objets, W, sol_init,voisinage,n,p,elicitation_name="OWA",verbose=True)
    #rechercheLocale_plus_elicitation(objets, W, sol_init,voisinage,n,p,elicitation_name="Choquet",verbose=True)