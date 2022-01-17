#Auteur : David PINAUD
#Description : fichier permettant de grapher les résultats des appels en utilisant les logs

import os
import ast
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
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
                allLogs.append(log)
    return allLogs

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

# plot_PLS_executionTimes_wrt_n_and_p()
# plot_PLS_executionTimes_wrt_n_and_p_3D()