# Solution [x1,x2,...,xn]: liste telle que l'élément à l'indice i est le booléen qui indique si l'objet i est dans la solution ou non
# objets {id_objet : [w, v1,v2, ... ,vp] ...}= liste des objets de l'instance, un dictionnaire avec comme clé l'indice de l'objet et comme valeur le poids w ainsi que les valeurs des critères de l'objet v1, ... , vp

#Auteur : David PINAUD
#Description : fichier permettant de lancer un Pareto Local Search pour une problème
# de sac à dos multi-objectif


import random as rand
from copy import deepcopy
import os
import datetime
from time import perf_counter
from instance_loader import getInstance

def getEvaluation(solution:list,objets:dict):
    """Retourne l'évaluation d'une solution donnée

    Parameters
    ----------
    solution : list
        liste telle que l'élément à l'indice i est le booléen qui indique si l'objet i est dans la solution ou non
    objets : dict
        les objets de l'instance

    Returns
    -------
    list
        l'évaluation de la solution
    """
    nb_critères=len(list(objets.values())[0])-1
    perf=[0 for _ in range(nb_critères)] #la performance d'une solution est initialisé à 0 pour tous les critères
    for (id_objet,caracteristiques_objet) in objets.items(): #pour tous les objets
        for (i,v_i) in enumerate(caracteristiques_objet[1:]): #on ajoute sa contribution (s'il est pris dans la sol) dans la performance sur chaque critère
            perf[i]+=v_i*solution[id_objet]
    return perf

def isDomFaible(sol1:list,sol2:list,objets:dict)->bool:
    """retourne Vrai si sol1>=sol2 (dominance faible au sens de Pareto, en maximisation)

    Parameters
    ----------
    sol1 : list
        solution 1 à comparer
    sol2 : list
        solution 2 à comparer

    Returns
    -------
    bool
        True si sol1>=sol2, False sinon
    """
    perf1=getEvaluation(sol1,objets)
    perf2=getEvaluation(sol2,objets)
    for critere_i_Sol1,critere_i_Sol2 in zip(perf1,perf2):
        if(critere_i_Sol1<critere_i_Sol2):
            return False
    return True

def isDom(sol1:list,sol2:list,objets:dict)->bool:
    """retourne Vrai si sol1>sol2 (dominance au sens de Pareto, en maximisation)

    Parameters
    ----------
    sol1 : list
        solution 1 à comparer
    sol2 : list
        solution 2 à comparer

    Returns
    -------
    bool
        True si sol1>sol2, False sinon
    """
    perf1=getEvaluation(sol1,objets)
    perf2=getEvaluation(sol2,objets)
    hasOneBigger=False
    for critere_i_Sol1,critere_i_Sol2 in zip(perf1,perf2):
        if(critere_i_Sol1<critere_i_Sol2):
            return False
        if(critere_i_Sol1>critere_i_Sol2): #la sol1 est meilleure strictement sur un critère
            hasOneBigger=True
    return True if hasOneBigger else False

def isDomStrict(sol1:list,sol2:list,objets:dict)->bool:
    """retourne Vrai si sol1>>sol2 (dominance forte au sens de Pareto, en maximisation)

    Parameters
    ----------
    sol1 : list
        solution 1 à comparer
    sol2 : list
        solution 2 à comparer

    Returns
    -------
    bool
        True si sol1>>sol2, False sinon
    """
    perf1=getEvaluation(sol1,objets)
    perf2=getEvaluation(sol2,objets)
    for critere_i_Sol1,critere_i_Sol2 in zip(perf1,perf2):
        if(critere_i_Sol1<=critere_i_Sol2):
            return False
    return True

def isRealisable(solution:list, W:int, objets:dict):
    """Test si une solution est réalisable ou non

    Parameters
    ----------
    solution : list
        une solution a tester
    W : int
        poids max du sac à dos
    objets : dict
        la liste des objets de l'instance

    Returns
    -------
    bool
        True si la solution est réalisable et False sinon
    """
    return getPoidsSol(solution, objets)<=W

def getPoidsSol(solution:list, objets:dict):
    """Retoune le poids d'une solution (somme des poids des objets pris)

    Parameters
    ----------
    solution : list
        liste des booleens qui indique si un objet est pris ou pas
    objets : dict
        dictionnaire des objets

    Returns
    -------
    float
        poids de l'objet
    """
    poidsSolution=0
    for i,xi in enumerate(solution):
        poidsSolution+=objets[i][0]*xi
    return poidsSolution

def mise_a_jour_ens_potentiellement_efficace(ens_pot_efficace:list,candidat_a_lajout:list,objets:dict, dominance=isDom):
    """Fonction qui permet de mettre à jour la liste des potentiellements efficaces
    quand un nouveau candidat arrive (une nouvelle solution peut être potentiellement efficace)

    Parameters
    ----------
    ens_pot_efficace : list de list
        liste des solutions potentiellements efficaces courante
    candidat_a_lajout : list
        solution candidate
    dominance : func
        la dominance à considérer
    Returns
    -------
    list de list, bool
        la liste des solutions potentiellement efficace mis à jour et un booleen qui indique si cette liste a changé.
    """
    if(len(ens_pot_efficace)==0):
        ens_pot_efficace.append(candidat_a_lajout)
        return ens_pot_efficace, True
    elif(candidat_a_lajout in ens_pot_efficace):
        return ens_pot_efficace,False
    else:

        for solution_pot_efficace in ens_pot_efficace: #on cherche une solution potentiellement efficace qui domine le candidat
            if(dominance(solution_pot_efficace,candidat_a_lajout,objets)): #si il y en a une, candidat n'est pas potentiellement efficace
                return ens_pot_efficace,False
        
        #si on ne trouve une telle solution, candidat est potentiellement efficace
        ens_pot_efficace.append(candidat_a_lajout)
        
        toRemove=[]
        for solution_pot_efficace in ens_pot_efficace: #on regarde si la nouvelle solution potentiellement efficace domine des solutions dans l'ensemble des potentiellements efficace
            if(dominance(candidat_a_lajout,solution_pot_efficace,objets)):#si c'est le cas, ils sont dominés, donc non potentiellement efficace
                toRemove.append(solution_pot_efficace)
        ens_pot_efficace_a_jour=[sol for sol in ens_pot_efficace if sol not in toRemove]
        
        return ens_pot_efficace_a_jour, True
            
def voisinage(solution:list, objets:dict, W:int):
    """Fonction qui renvoie les voisins d'une solution en faisant des échanges 1-1 et en remplissant l'espace qui reste avec des objets qui rentrent dans le sac.

    Parameters
    ----------
    solution : list
        la solution pour laquelle on veut le voisinage
    objets : dict
        les objets de l'instance
    W : int
        la capacité du sac à dos

    Returns
    -------
    list
        liste des voisins de la solution
    """
    voisinage=set()
    poids_solution=getPoidsSol(solution,objets)
    objetsAEnlever=[i for i in range(len(solution)) if solution[i]==1] #les objets pris dans solution
    # print(f"solution : {solution}\n")
    # print(f"poids_solution : {poids_solution}\n")
    # print(f"objets : {objets}\n")

    for objet_a_enlever in objetsAEnlever:
        for objet_candidat,values in objets.items():
            if objet_candidat not in objetsAEnlever :
                # print(f"objet_a_enlever : {objet_a_enlever}\n")
                # print(f"objet_candidat : {objet_candidat}\n")
                # print(f"values : {values}\n")
                if poids_solution-objets[objet_a_enlever][0]+values[0]<=W:
                    # print("in1")
                    solution_temp=solution.copy()
                    solution_temp[objet_a_enlever]=0
                    solution_temp[objet_candidat]=1
                    # print(f"solution_temp : {solution_temp}\n")
                    # print(f"poids_solution_temp : {poids_solution-objets[objet_a_enlever][0]+values[0]} ou {getPoidsSol(solution_temp,objets)}\n")
                    # print(f"W : {W}\n")
                    poids_sol_temp=poids_solution-objets[objet_a_enlever][0]+values[0]
                    objets_candidats_restant=[i for i in range(len(solution)) if solution_temp[i]==0]
                    # print(f"objets_candidats_restant : {objets_candidats_restant}\n")
                    while(len(objets_candidats_restant)):
                        # print("in2")
                        candidat=rand.choice(objets_candidats_restant)
                        # print(f"candidat : {candidat}\n")
                        objets_candidats_restant.remove(candidat)
                        if(poids_sol_temp+objets[candidat][0]<=W):
                            # print("in3")
                            poids_sol_temp+=objets[candidat][0]
                            solution_temp[candidat]=1
                            # print(f"solution_temp : {solution_temp}\n")
                            # print(f"poids_solution_temp : {poids_sol_temp} ou {getPoidsSol(solution_temp,objets)}\n")
                            # print(f"W : {W}\n")
                    voisinage.add(tuple(solution_temp))
                    #print(f"voisinage de {solution}: {voisinage}\n")
    return [list(voisin) for voisin in voisinage]

def genererSolutionInitiale(objets:dict,W:int):
    """Génère une solution initiale pour PLS qui prends les meilleurs objets au sens d'un rapport de performance = somme pondérée des critères/poids
    tant qu'on ne dépasse pas la capacité du sac à dos. la pondération est aléatoire.

    Parameters
    ----------
    objets : dict
        les objets de l'instance du problème
    W : int
        la capacité du sac à dos

    Returns
    -------
    list
        une solution intiale pour PLS
    """
    sol_initiale=[0 for _ in objets.keys()]
    rapport_de_performance=[]

    nb_critères=len(list(objets.values())[0])-1
    ponderation=[rand.randint(1,10) for _ in range(nb_critères)]
    sumPonderation=sum(ponderation)
    ponderation=[p/sumPonderation for p in ponderation]

    for key,value in objets.items():
        rapport_de_performance.append([key,sum(value[i]*ponderation[i-1] for i in range(1,len(value)))/value[0]])
    rapport_de_performance.sort(key=lambda x:x[1],reverse=True)
    for key,_ in rapport_de_performance:
        if getPoidsSol(sol_initiale,objets)+objets[key][0]<W:
            sol_initiale[key]=1
    return sol_initiale

def genererPopulationInitiale(nbIndividuMax:int,objets:dict,W:int):
    """Fonction qui permet de générer une population initiale de solutions réalisables.

    Parameters
    ----------
    nbIndividuMax : int
        nombre d'invidu maximal dans cette population
    objets : dict
        les objets du problème
    W : int
        la capacité maximale du sac à dos

    Returns
    -------
    list
        liste de solutions réalisable du problème
    """
    pop=set()
    countdown=100
    while(len(pop)<nbIndividuMax and countdown>=0): #on essaye de génerer une population initiale de taille maximale de nbIndividuMax
        countdown-=1
        oldLen=len(pop)
        pop.add(tuple(genererSolutionInitiale(objets,W)))
        if(len(pop)>oldLen): #à chaque fois qu'on a un nouvel individu on laisse countdown itération au programme pour qu'il essait d'en trouver un autre
            countdown=100
    return [list(sol) for sol in pop]

def PLS(pop_init:list,voisinage,objets:dict,W:int): #Approximation des points non-dominés
    """Implémentation de l'algorithme Pareto Local Search avec une mise à jour de l'ensemble
    approximant l'ensemble des non dominés faite de façon forte brute.
    Enregistre aussi les résultats dans un fichier log.

    Parameters
    ----------
    pop_init : list
        liste de solutions sur lequel commencer la recherche locale
    voisinage : function
        fonction de voisinage d'une solution
    objets : dict
        les objets du problème
    W : int
        capacité maximale du sac à dos

    Returns
    -------
    list
        Une approximation de l'ensemble des non dominés
    """
    t1_start = perf_counter()
    non_domines_approx=deepcopy(pop_init)
    P=deepcopy(pop_init)
    Pa=[]
    t=0
    while(len(P)):
        #print(f"X_E : {non_domines_approx} de taille {len(non_domines_approx)}\nP : {P} de taille {len(P)}\n")
        for p in P:
            for p_voisin in voisinage(p,objets,W):
                if(not isDom(p,p_voisin,objets) and getEvaluation(p,objets)!=getEvaluation(p_voisin,objets)):
                    non_domines_approx,hasChanged=mise_a_jour_ens_potentiellement_efficace(non_domines_approx,p_voisin,objets)
                    if hasChanged:
                        Pa,_=mise_a_jour_ens_potentiellement_efficace(Pa,p_voisin,objets)
        P=deepcopy(Pa)
        Pa=[]
    t1_stop = perf_counter()
    dirname = os.path.dirname(__file__)
    date=str(datetime.datetime.now()).replace(" ", "")
    filename = os.path.join(dirname+"/logs", f"PLS1_n_{len(objets)}_p_{len(list(objets.values())[0])-1}_{date}.txt")
    log=open(filename,'w+')
    log.write("logType\nPLS1\n\n")
    log.write("non_domines_approx\n")
    log.write(str(non_domines_approx))
    log.write("\n\n")
    log.write("fonction de voisinage\n")
    log.write(voisinage.__name__)
    log.write("\n\n")
    log.write("objets\n")
    log.write(str(objets))
    log.write("\n\n")
    log.write("capacité max\n")
    log.write(str(W))
    log.write("\n\n")
    log.write("execution_time\n")
    log.write(f"{t1_stop-t1_start}\n")
    log.write("\n\n")
    log.write("n\n")
    log.write(f"{len(objets.values())}\n")
    log.write("\n\n")
    log.write("p\n")
    log.write(f"{len(list(objets.values())[0])-1}\n")
    log.close()
    return non_domines_approx

def PLS2(pop_init:list,voisinage,objets:dict,W:int):
    """Implémentation de l'algorithme Pareto Local Search avec une mise à jour de l'ensemble
    approximant l'ensemble des non dominés faite de façon forte brute.
    Enregistre aussi les résultats dans un fichier log.

    Version 2 un peu plus efficace.

    Parameters
    ----------
    pop_init : list
        liste de solutions sur lequel commencer la recherche locale
    voisinage : function
        fonction de voisinage d'une solution
    objets : dict
        les objets du problème
    W : int
        capacité maximale du sac à dos

    Returns
    -------
    list
        Une approximation de l'ensemble des non dominés
    """
    t1_start = perf_counter()
    non_domines_approx=deepcopy(pop_init)
    P=deepcopy(pop_init)
    Pa=[]
    while(len(P)):
        #print(f"X_E : {non_domines_approx} de taille {len(non_domines_approx)}\nP : {P} de taille {len(P)}\n")
        for p in P:
            LN=[]
            for p_voisin in voisinage(p,objets,W):
                if(not isDom(p,p_voisin,objets)):
                    LN,_=mise_a_jour_ens_potentiellement_efficace(LN,p_voisin,objets)
            for p_voisin in LN:
                non_domines_approx,hasChanged=mise_a_jour_ens_potentiellement_efficace(non_domines_approx,p_voisin,objets)
                if hasChanged:
                    Pa,_=mise_a_jour_ens_potentiellement_efficace(Pa,p_voisin,objets)
        P=deepcopy(Pa)
        Pa=[]
    t1_stop = perf_counter()
    dirname = os.path.dirname(__file__)
    date=str(datetime.datetime.now()).replace(" ", "")
    filename = os.path.join(dirname+"/logs", f"PLS2_n_{len(objets)}_p_{len(list(objets.values())[0])-1}_{date}.txt")
    log=open(filename,'w+')
    log.write("logType\nPLS2\n\n")
    log.write("non_domines_approx\n")
    log.write(str(non_domines_approx))
    log.write("\n\n")
    log.write("fonction de voisinage\n")
    log.write(voisinage.__name__)
    log.write("\n\n")
    log.write("objets\n")
    log.write(str(objets))
    log.write("\n\n")
    log.write("capacité max\n")
    log.write(str(W))
    log.write("\n\n")
    log.write("execution_time\n")
    log.write(f"{t1_stop-t1_start}\n")
    log.write("\n\n")
    log.write("n\n")
    log.write(f"{len(objets.values())}\n")
    log.write("\n\n")
    log.write("p\n")
    log.write(f"{len(list(objets.values())[0])-1}\n")
    log.close()
    return non_domines_approx

if __name__== "__main__":
    n=15
    p=3
    objets_test, W_test=getInstance(n,p)
    nb_solution_dans_popInit=20
    pop_init=genererPopulationInitiale(nb_solution_dans_popInit,objets_test,W_test)
    print(f"\n\nn={n} p={p}\npopulation initiale : {pop_init}, longueur {len(pop_init)}")
    print(f"non dominés de PLS1 : {PLS(pop_init,voisinage,objets_test,W_test)}")
    print(f"non dominés de PLS2 : {PLS2(pop_init,voisinage,objets_test,W_test)}")
    print("Logs sauvegardés dans ./logs")
    