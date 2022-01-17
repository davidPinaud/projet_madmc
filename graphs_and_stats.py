#Auteur : David PINAUD
#Description : fichier permettant de grapher les résultats des appels en utilisant les logs

import argparse
from fileinput import filename
from multiprocessing.sharedctypes import Value
import os
import ast
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
def all_RL_elici_logs(aggregation_function:str):
    if aggregation_function in ["SP","OWA","Choquet"]:
        dirname = os.path.dirname(__file__)
        allLogs=[]
        for file_name in os.listdir(dirname+f"/logs_RL_elici/{aggregation_function}"):
            if file_name.endswith(".txt"):
                log_file_path=os.path.join(dirname+f"/logs_RL_elici/{aggregation_function}", file_name)
                elems_in_filename=file_name.split("_")

                log={
                    "aggregation_function":aggregation_function,
                    "n":int(elems_in_filename[3]),
                    "p":int(elems_in_filename[5])
                }
                with open(log_file_path) as elicitation_log:
                    temp=elicitation_log.readline().strip()
                    temp=temp.replace('<','"')
                    temp=temp.replace('>','"')
                    if(len(temp)!=0):
                        temp=ast.literal_eval(temp)
                        return {**log,**temp}
                    else:
                        return None
    else:
        return None
def all_elicitation_logs(aggregation_function:str):
    if aggregation_function in ["SP","OWA","Choquet"]:
        dirname = os.path.dirname(__file__)
        allLogs=[]
        for file_name in os.listdir(dirname+f"/logs_{aggregation_function}"):
            if file_name.endswith(".txt"):
                log_file_path=os.path.join(dirname+f"/logs_{aggregation_function}", file_name)

                elems_in_filename=file_name.split("_")

                log={
                    "aggregation_function":aggregation_function,
                    "n":int(elems_in_filename[2]),
                    "p":int(elems_in_filename[4])
                }
                with open(log_file_path) as elicitation_log:
                    line=elicitation_log.readline()
                    while line:
                        line=line.strip()
                        if(line=="log"):
                            PLS_log=elicitation_log.readline().strip()
                            if(len(PLS_log)!=0):
                                log["PLS_log"]=ast.literal_eval(PLS_log)
                            elicitation_log.readline()
                            line=elicitation_log.readline()
                            continue
                        if(line=="Evaluations"):
                            Evaluations=elicitation_log.readline().strip()
                            log["Evaluations"]=ast.literal_eval(Evaluations)
                            elicitation_log.readline()
                            line=elicitation_log.readline()
                            continue
                        if(line=="solution_optimale_estimee"):
                            solution_optimale_estimee=elicitation_log.readline().strip()
                            log["solution_optimale_estimee"]=ast.literal_eval(solution_optimale_estimee)
                            elicitation_log.readline()
                            line=elicitation_log.readline()
                            continue
                        if(line=="nb_question"):
                            nb_question=elicitation_log.readline().strip()
                            log["nb_question"]=int(nb_question)
                            elicitation_log.readline()
                            line=elicitation_log.readline()
                            continue
                        if(line=="valeur_sol_estimee"):
                            valeur_sol_estimee=elicitation_log.readline().strip()
                            log["valeur_sol_estimee"]=float(valeur_sol_estimee)
                            elicitation_log.readline()
                            line=elicitation_log.readline()
                            continue
                        if(line=="decideur"):
                            decideur=elicitation_log.readline().strip()
                            log["decideur"]=ast.literal_eval(decideur)
                            elicitation_log.readline()
                            line=elicitation_log.readline()
                            continue
                        if(line=="solution_optimale"):
                            solution_optimale=elicitation_log.readline().strip()
                            log["solution_optimale"]=ast.literal_eval(solution_optimale)
                            elicitation_log.readline()
                            line=elicitation_log.readline()
                            continue
                        if(line=="valeur_sol_optimale"):
                            valeur_sol_optimale=elicitation_log.readline().strip()
                            log["valeur_sol_optimale"]=ast.literal_eval(valeur_sol_optimale)
                            elicitation_log.readline()
                            line=elicitation_log.readline()
                            continue
                        if(line=="duree"):
                            duree=elicitation_log.readline().strip()
                            log["duree"]=float(duree)
                            elicitation_log.readline()
                            line=elicitation_log.readline()
                            continue
                        if(line=="gap(%)"):
                            gap=elicitation_log.readline().strip()
                            log["gap"]=float(gap)
                            elicitation_log.readline()
                            line=elicitation_log.readline()
                            continue
                allLogs.append(log)
        return allLogs
    else:
        print("elicitation_name doit être égal à SP,OWA ou Choquet")
        return None

def get_all_PLS_logs():
    """Permet de récuperer tous les logs générés par les fontions PLS et PLS2

    Returns
    -------
    list
        liste des logs de PLS et PLS2 
        les logs sont des dictionnaires de la forme 
        {
            "logType" : str                     # type de PLS utilisé (PLS ou PLS2)
            "non_domines_approx" : list         # approximation de l'ensemble des non dominés calculé par PLS ou PLS2
            "fonction_de_voisinage" : str       # nom de la fonction de voisinage utilisé
            "objets" : dict                     # objets du problème du sac à dos
            "W" : int                           # capacité du sac à dos  du problème du sac à dos
            "execution_time" : float            # temps d'éxécution de PLS ou PLS2
            "n" : int                           # nombre d'objet dans le problème
            "p" : int                           # nombre d'objectifs dans le problème
        }
    """
    dirname = os.path.dirname(__file__)
    allLogs=[]
    for file_name in os.listdir(dirname+"/logs"):
        if file_name.endswith(".txt"):
            file_elems=file_name.split("_")
            if(file_elems[0]=="PLS1" or file_elems[0]=="PLS2"):
                file_characteristic={
                    "PLS_type":file_elems[0],
                    "n":int(file_elems[2]),
                    "p":int(file_elems[4]),
                }
                log={}
                log_file_path=os.path.join(dirname+"/logs", file_name)
                with open(log_file_path) as PLS_log:
                    line=PLS_log.readline()
                    while line:
                        line=line.strip()
                        if(line=="logType"):
                            logType=PLS_log.readline().strip()
                            log["logType"]=file_characteristic["PLS_type"]
                            PLS_log.readline()
                            line=PLS_log.readline()
                            continue
                        if(line=="non_domines_approx"):
                            non_domines_approx=ast.literal_eval(PLS_log.readline())
                            log["non_domines_approx"]=non_domines_approx
                            PLS_log.readline()
                            line=PLS_log.readline()
                            continue
                        if(line=="fonction de voisinage"):
                            fonction_de_voisinage=PLS_log.readline().strip()
                            log["fonction_de_voisinage"]=fonction_de_voisinage
                            PLS_log.readline()
                            line=PLS_log.readline()
                            continue
                        if(line=="objets"):
                            objets=ast.literal_eval(PLS_log.readline())
                            log["objets"]=objets
                            PLS_log.readline()
                            line=PLS_log.readline()
                            continue
                        if(line=="capacité max"):
                            W=int(float(PLS_log.readline()))
                            log["W"]=W
                            PLS_log.readline()
                            line=PLS_log.readline()
                            continue
                        if(line=="duree"):
                            execution_time=float(PLS_log.readline())
                            log["duree"]=execution_time
                            PLS_log.readline()
                            PLS_log.readline()
                            line=PLS_log.readline()
                            continue
                        if(line=="n"):
                            n=int(float(PLS_log.readline()))
                            log["n"]=n
                            PLS_log.readline()
                            PLS_log.readline()
                            line=PLS_log.readline()
                            continue
                        if(line=="p"):
                            p=int(float(PLS_log.readline()))
                            log["p"]=p
                            PLS_log.readline()
                            line=PLS_log.readline()
                            continue
                allLogs.append(log)
    return allLogs

def get_one_PLS_log(logtype,n,p):
    """Permet de récuperer tous un des logs générés par les fontions PLS et PLS2

    Parameters
    ----------
    logtype: str
        PLS1 ou PLS2, quel PLS a crée ce log
    n:int
        nombre d'objets voulu
    p:int
        nombre de critère voulu
    Returns
    -------
    dict
        log qui vérifie les conditions demandées
        les logs sont des dictionnaires de la forme 
        {
            "logType" : str                     # type de PLS utilisé (PLS ou PLS2)
            "non_domines_approx" : list         # approximation de l'ensemble des non dominés calculé par PLS ou PLS2
            "fonction_de_voisinage" : str       # nom de la fonction de voisinage utilisé
            "objets" : dict                     # objets du problème du sac à dos
            "W" : int                           # capacité du sac à dos  du problème du sac à dos
            "execution_time" : float            # temps d'éxécution de PLS ou PLS2
            "n" : int                           # nombre d'objet dans le problème
            "p" : int                           # nombre d'objectifs dans le problème
        }
    """
    dirname = os.path.dirname(__file__)
    for file_name in os.listdir(dirname+"/logs"):
        if file_name.endswith(".txt"):
            file_elems=file_name.split("_")
            if(file_elems[0]==logtype and file_elems[2]==str(n) and file_elems[4]==str(p) ):
                file_characteristic={
                    "PLS_type":file_elems[0],
                    "n":int(file_elems[2]),
                    "p":int(file_elems[4]),
                }
                log={}
                log_file_path=os.path.join(dirname+"/logs", file_name)
                with open(log_file_path) as PLS_log:
                    line=PLS_log.readline()
                    while line:
                        line=line.strip()
                        if(line=="logType"):
                            logType=PLS_log.readline().strip()
                            log["logType"]=file_characteristic["PLS_type"]
                            PLS_log.readline()
                            line=PLS_log.readline()
                            continue
                        if(line=="non_domines_approx"):
                            non_domines_approx=ast.literal_eval(PLS_log.readline())
                            log["non_domines_approx"]=non_domines_approx
                            PLS_log.readline()
                            line=PLS_log.readline()
                            continue
                        if(line=="fonction de voisinage"):
                            fonction_de_voisinage=PLS_log.readline().strip()
                            log["fonction_de_voisinage"]=fonction_de_voisinage
                            PLS_log.readline()
                            line=PLS_log.readline()
                            continue
                        if(line=="objets"):
                            objets=ast.literal_eval(PLS_log.readline())
                            log["objets"]=objets
                            PLS_log.readline()
                            line=PLS_log.readline()
                            continue
                        if(line=="capacité max"):
                            W=int(float(PLS_log.readline()))
                            log["W"]=W
                            PLS_log.readline()
                            line=PLS_log.readline()
                            continue
                        if(line=="execution_time"):
                            execution_time=float(PLS_log.readline())
                            log["execution_time"]=execution_time
                            PLS_log.readline()
                            PLS_log.readline()
                            line=PLS_log.readline()
                            continue
                        if(line=="n"):
                            n=int(float(PLS_log.readline()))
                            log["n"]=n
                            PLS_log.readline()
                            PLS_log.readline()
                            line=PLS_log.readline()
                            continue
                        if(line=="p"):
                            p=int(float(PLS_log.readline()))
                            log["p"]=p
                            PLS_log.readline()
                            line=PLS_log.readline()
                            continue
                return(log)

def plot_PLS_executionTimes_wrt_n_and_p():
    """Permet de plotter 2 graphes avec les temps d'éxécutions de PLS et PLS2 en fonction de n et p et leurs moyennes
    """
    allLogs=get_all_PLS_logs()
    ####PLS1
    allPLS1logs=[log for log in allLogs if log["logType"]=="PLS1"]
    allPLS1logs_n=np.array([[log["n"],log["execution_time"]] for log in allPLS1logs])
    allPLS1logs_p=np.array([[log["p"],log["execution_time"]] for log in allPLS1logs])

    max_n_1=int(float(max([log[0] for log in allPLS1logs_n])))
    PLS1_mean_n=[]
    for n in range(1,max_n_1+1):
        PLS1_mean_n.append([n,np.mean([log[1] for log in allPLS1logs_n if log[0]==n])])
    PLS1_mean_n=np.array(PLS1_mean_n)

    max_p_1=int(float(max([log[1] for log in allPLS1logs_p])))
    PLS1_mean_p=[]
    for p in range(1,max_p_1+1):
        PLS1_mean_p.append([p,np.mean([log[1] for log in allPLS1logs_p if log[0]==p])])
    PLS1_mean_p=np.array(PLS1_mean_p)
    ####PLS2
    allPLS2logs=[log for log in allLogs if log["logType"]=="PLS2"]
    allPLS2logs_n=np.array([[log["n"],log["execution_time"]] for log in allPLS2logs])
    allPLS2logs_p=np.array([[log["p"],log["execution_time"]] for log in allPLS2logs])

    max_n_2=int(float(max([log[0] for log in allPLS2logs_n])))
    PLS2_mean_n=[]
    for n in range(1,max_n_2+1):
        PLS2_mean_n.append([n,np.mean([log[1] for log in allPLS2logs_n if log[0]==n])])
    PLS2_mean_n=np.array(PLS2_mean_n)

    max_p_2=int(float(max([log[1] for log in allPLS2logs_n])))
    PLS2_mean_p=[]
    for p in range(1,max_p_2+1):
        PLS2_mean_p.append([p,np.mean([log[1] for log in allPLS2logs_p if log[0]==p])])
    PLS2_mean_p=np.array(PLS2_mean_p)
    
    ####pplot
    fig, axs = plt.subplots(ncols=2, nrows=1, figsize=(5.5, 3.5),
                        constrained_layout=True)

    #par rapport à n
    axs[0].scatter(allPLS1logs_n[:,0],allPLS1logs_n[:,1],c='r',label="temps exec PLS1",s=0.7)
    axs[0].plot(PLS1_mean_n[:,0],PLS1_mean_n[:,1],c='r',label="moy temps exec PLS1")
    axs[0].scatter(allPLS2logs_n[:,0],allPLS2logs_n[:,1],c='b',label="temps exec PLS2",s=0.7)
    axs[0].plot(PLS2_mean_n[:,0],PLS2_mean_n[:,1],c='b',label="moy temps exec PLS2")
    axs[0].set_xlabel("n")
    axs[0].set_ylabel("Temps d'éxécution (s)")

    #par rapport à p
    axs[1].scatter(allPLS1logs_p[:,0],allPLS1logs_p[:,1],c='r',label="temps exec PLS1",s=0.7)
    axs[1].plot(PLS1_mean_p[:,0],PLS1_mean_p[:,1],c='r',label="moy temps exec PLS1")
    axs[1].scatter(allPLS2logs_p[:,0],allPLS2logs_p[:,1],c='b',label="temps exec PLS2",s=0.7)
    axs[1].plot(PLS2_mean_p[:,0],PLS2_mean_p[:,1],c='b',label="moy temps exec PLS2")
    axs[1].set_xlabel("p")
    axs[1].set_ylabel("Temps d'éxécution (s)")
    
    axs[0].legend()
    axs[1].legend()
    fig.suptitle("Temps d'éxécution (s) de PLS1 et PLS2 en fonction de n et p")
    plt.show()

def plot_PLS_executionTimes_wrt_n_and_p_3D():
    """Permet de plotter un graphe en 3D sur le temps d'éxécutions de PLS1 et PLS2 en fonction de n et p
    """
    allLogs=get_all_PLS_logs()
    
    allPLS1logs=[log for log in allLogs if log["logType"]=="PLS1"]
    allPLS2logs=[log for log in allLogs if log["logType"]=="PLS2"]

    allPLS1logs_n_p=np.array([[log["n"],log["p"],log["execution_time"]] for log in allPLS1logs])
    allPLS2logs_n_p=np.array([[log["n"],log["p"],log["execution_time"]] for log in allPLS2logs])

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(allPLS1logs_n_p[:,0],allPLS1logs_n_p[:,1],allPLS1logs_n_p[:,2],s=3,c='r',label="PLS1")
    ax.scatter(allPLS2logs_n_p[:,0],allPLS2logs_n_p[:,1],allPLS2logs_n_p[:,2],s=3,c='b',label="PLS2")

    ax.set_xlabel("n")
    ax.set_ylabel("p")
    ax.set_zlabel("Temps d'éxecution (s)")
    ax.legend()
    plt.show()
def plot_elicitation_executionTimes_wrt_n_and_p_3D():
    allLogs_SD=all_elicitation_logs("SP")
    allLogs_OWA=all_elicitation_logs("OWA")
    allLogs_Choquet=all_elicitation_logs("Choquet")
    n_p_exec_times_SD=[]
    n_p_exec_times_OWA=[]
    n_p_exec_times_Choquet=[]
    for logSD,logOWA,logChoquet in zip(allLogs_SD,allLogs_OWA,allLogs_Choquet):
        n_p_exec_times_SD.append([logSD["n"],logSD["p"],logSD["duree"]])
        n_p_exec_times_OWA.append([logOWA["n"],logOWA["p"],logOWA["duree"]])
        n_p_exec_times_Choquet.append([logChoquet["n"],logChoquet["p"],logChoquet["duree"]])
    n_p_exec_times_SD=np.array(n_p_exec_times_SD)
    n_p_exec_times_OWA=np.array(n_p_exec_times_OWA)
    n_p_exec_times_Choquet=np.array(n_p_exec_times_Choquet)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(n_p_exec_times_SD[:,0],n_p_exec_times_SD[:,1],n_p_exec_times_SD[:,2],s=5,c='r',label="Somme pondérée",marker="o")
    ax.scatter(n_p_exec_times_OWA[:,0],n_p_exec_times_OWA[:,1],n_p_exec_times_OWA[:,2],s=5,c='b',label="OWA",marker="p")
    ax.scatter(n_p_exec_times_Choquet[:,0],n_p_exec_times_Choquet[:,1],n_p_exec_times_Choquet[:,2],s=5,c='g',label="Choquet",marker="^")
    ax.set_xlabel("n")
    ax.set_ylabel("p")
    ax.set_zlabel("Temps d'éxecution (s)")
    ax.legend()
    plt.show()

def plot_elicitation_nbQuestion_wrt_n_and_p_3D():
    allLogs_SD=all_elicitation_logs("SP")
    allLogs_OWA=all_elicitation_logs("OWA")
    allLogs_Choquet=all_elicitation_logs("Choquet")
    n_p_nbQuestion_SD=[]
    n_p_nbQuestion_OWA=[]
    n_p_nbQuestion_Choquet=[]
    for logSD,logOWA,logChoquet in zip(allLogs_SD,allLogs_OWA,allLogs_Choquet):
        n_p_nbQuestion_SD.append([logSD["n"],logSD["p"],logSD["nb_question"]])
        n_p_nbQuestion_OWA.append([logOWA["n"],logOWA["p"],logOWA["nb_question"]])
        n_p_nbQuestion_Choquet.append([logChoquet["n"],logChoquet["p"],logChoquet["nb_question"]])
    n_p_nbQuestion_SD=np.array(n_p_nbQuestion_SD)
    n_p_nbQuestion_OWA=np.array(n_p_nbQuestion_OWA)
    n_p_nbQuestion_Choquet=np.array(n_p_nbQuestion_Choquet)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(n_p_nbQuestion_SD[:,0],n_p_nbQuestion_SD[:,1],n_p_nbQuestion_SD[:,2],s=5,c='r',label="Somme pondérée",marker="o")
    ax.scatter(n_p_nbQuestion_OWA[:,0],n_p_nbQuestion_OWA[:,1],n_p_nbQuestion_OWA[:,2],s=5,c='b',label="OWA",marker="p")
    ax.scatter(n_p_nbQuestion_Choquet[:,0],n_p_nbQuestion_Choquet[:,1],n_p_nbQuestion_Choquet[:,2],s=5,c='g',label="Choquet",marker="^")
    ax.set_xlabel("n")
    ax.set_ylabel("p")
    ax.set_zlabel("nombre de questions")
    ax.legend()
    plt.show()

def plot_elicitation_gap_wrt_n_and_p_3D():
    allLogs_SD=all_elicitation_logs("SP")
    allLogs_OWA=all_elicitation_logs("OWA")
    allLogs_Choquet=all_elicitation_logs("Choquet")
    n_p_gap_SD=[]
    n_p_gap_OWA=[]
    n_p_gap_Choquet=[]
    for logSD in allLogs_SD:
        n_p_gap_SD.append([logSD["n"],logSD["p"],logSD["gap"]])
    for logOWA in allLogs_OWA:
        n_p_gap_OWA.append([logOWA["n"],logOWA["p"],logOWA["gap"]])
    for logChoquet in allLogs_Choquet:
        n_p_gap_Choquet.append([logChoquet["n"],logChoquet["p"],logChoquet["gap"]])
    n_p_gap_SD=np.array(n_p_gap_SD)
    n_p_gap_OWA=np.array(n_p_gap_OWA)
    n_p_gap_Choquet=np.array(n_p_gap_Choquet)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(n_p_gap_SD[:,0],n_p_gap_SD[:,1],n_p_gap_SD[:,2],s=5,c='r',label="Somme pondérée",marker="o")
    ax.scatter(n_p_gap_OWA[:,0],n_p_gap_OWA[:,1],n_p_gap_OWA[:,2],s=5,c='b',label="OWA",marker="p")
    ax.scatter(n_p_gap_Choquet[:,0],n_p_gap_Choquet[:,1],n_p_gap_Choquet[:,2],s=5,c='g',label="Choquet",marker="^")
    ax.set_xlabel("n")
    ax.set_ylabel("p")
    ax.set_zlabel("gap en %")
    ax.legend()
    plt.show()

def plot_RL_elicitation_executionTimes_wrt_n_and_p_3D():
    allLogs_SD=all_RL_elici_logs("SP")
    allLogs_OWA=all_RL_elici_logs("OWA")
    allLogs_Choquet=all_RL_elici_logs("Choquet")

    for logSD in allLogs_SD:
        duree=0
        for key,Value in logSD.items():
            if(key!='parameters'):
                i=int(key)
                duree+=float(Value["dureeIteration"])
    for logOWA in allLogs_OWA:
        for i in range(int(logOWA["nb_question"])):
            pass
    for logChoquet in allLogs_Choquet:
        for i in range(int(logChoquet["nb_question"])):
            pass


# plot_PLS_executionTimes_wrt_n_and_p()
# plot_PLS_executionTimes_wrt_n_and_p_3D()
#plot_elicitation_executionTimes_wrt_n_and_p_3D() 
#plot_elicitation_nbQuestion_wrt_n_and_p_3D() #plus p augmente, plus on pose de question
#plot_elicitation_gap_wrt_n_and_p_3D()
#print(all_RL_elici_logs("SP"))

#TODO faire les fonctions pour grapher temps exe, gap et nbQuestion pour elicitation avec recherche locale
#TODO écrire rapport
#TODO preparer prez