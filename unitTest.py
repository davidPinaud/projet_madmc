from ast import parse
from instance_loader import getInstance, getInstance_withRandomSelection
from PLS import *
import numpy as np

def test_1_mise_a_jour_ens_potentiellement_efficace(verbose=False):
    """test si quand un candidat non dominé par les sols pot eff arrive, on le rajoute bien et on efface bien les nouveaux dominées
    """
    ens_pot_efficace, hasChanged=mise_a_jour_ens_potentiellement_efficace(ens_pot_efficace_test1,solution_realisable_test1,objets_test)
    if(verbose):
        print("\navant candidature",ens_pot_efficace_test1, "candidat : ",solution_realisable_test1)
        print("après candidature, hasChanged : ", hasChanged," et nouvel ens :",ens_pot_efficace,"\n")
    return hasChanged==True and ens_pot_efficace==[solution_realisable_test1]

def test_2_mise_a_jour_ens_potentiellement_efficace(verbose=False):
    """test si quand un candidat dominé par au moins un sol pot eff arrive, on le rajoute pas et on efface rien
    """
    ens_pot_efficace, hasChanged=mise_a_jour_ens_potentiellement_efficace(ens_pot_efficace_test2,solution_realisable_test2,objets_test)
    if(verbose):
        print("\navant candidature",ens_pot_efficace_test2, "candidat : ",solution_realisable_test2)
        print("après candidature, hasChanged : ", hasChanged," et nouvel ens :",ens_pot_efficace,"\n")
    return hasChanged==False and ens_pot_efficace==[solution_realisable_test1]

def test_isDomFaible():
    """test la dominance faible de pareto >=
    """
    cond= True==isDomFaible(solution_realisable_test1,solution_realisable_test2,objets_test)
    cond = cond and False==isDomFaible(solution_realisable_test2,solution_realisable_test1,objets_test)
    cond = cond and False==isDomFaible(solution_realisable_test2,solution_realisable_test3,objets_test)
    cond = cond and False==isDomFaible(solution_realisable_test3,solution_realisable_test2,objets_test)
    return cond

def test_isDom():
    """test la dominance de pareto >
    """
    cond= True==isDom(solution_realisable_test1,solution_realisable_test2,objets_test)
    cond = cond and False==isDom(solution_realisable_test2,solution_realisable_test1,objets_test)
    cond = cond and False==isDomStrict(solution_realisable_test2,solution_realisable_test3,objets_test)
    cond = cond and False==isDomStrict(solution_realisable_test3,solution_realisable_test2,objets_test)
    return cond

def test_isDomStrict():
    """test la dominance stricte de pareto >>
    """
    cond=True==isDomStrict(solution_realisable_test1,solution_realisable_test2,objets_test)
    cond = cond and False==isDomStrict(solution_realisable_test2,solution_realisable_test1,objets_test)
    cond = cond and False==isDomStrict(solution_realisable_test2,solution_realisable_test3,objets_test)
    cond = cond and False==isDomStrict(solution_realisable_test3,solution_realisable_test2,objets_test)
    return cond

def test_basique():
    """Permet de tester si les fonctions basiques et utilitaires ont les bons comportements
    """
    print(f"\n\n****DONNÉES DU TEST****\n\n\
    objets_test {objets_test}\n\
    W_test {W_test}\n\
    Solution non réalisable 1 : {solution_non_realisable_test1} de poids {getPoidsSol(solution_non_realisable_test1,objets_test)}\n\
    Solution non réalisable 2 : {solution_non_realisable_test2} de poids {getPoidsSol(solution_non_realisable_test2,objets_test)}\n\
    Solution réalisable 1 : {solution_realisable_test1} de poids {getPoidsSol(solution_realisable_test1,objets_test)} de performance {getEvaluation(solution_realisable_test1,objets_test)}\n\
    Solution réalisable 2 : {solution_realisable_test2} de poids {getPoidsSol(solution_realisable_test2,objets_test)} de performance {getEvaluation(solution_realisable_test2,objets_test)}\n\
    Solution réalisable 3 : {solution_realisable_test3} de poids {getPoidsSol(solution_realisable_test3,objets_test)} de performance {getEvaluation(solution_realisable_test3,objets_test)}\n")

    ####Appels tests#####
    print("test_isDomFaible", test_isDomFaible())
    print("test_isDom",test_isDom())
    print("test_isDomStrict",test_isDomStrict())
    print("test_1_mise_a_jour_ens_potentiellement_efficace",test_1_mise_a_jour_ens_potentiellement_efficace())
    print("test_2_mise_a_jour_ens_potentiellement_efficace",test_2_mise_a_jour_ens_potentiellement_efficace())
    print(f"genererSolutionInitiale {genererSolutionInitiale(objets_test,W_test)}")
    print(f"voisinage de {solution_realisable_test3} : {voisinage(solution_realisable_test3,objets_test,W_test)}")

def test_PLS(objets_test, W_test):
    """Permet de tester les deux formes de

    Parameters
    ----------
    objets_test : dict
        objets du problème du sac à dos
    W_test : int
        capacité du problème du sac à dos
    """
    nb_solution_dans_popInit=20
    pop_init=genererPopulationInitiale(nb_solution_dans_popInit,objets_test,W_test)
    #print(f"\ngenererPopulationInitiale {pop_init}, longueur {len(pop_init)}")
    # print(f"PLS {PLS(pop_init,voisinage,objets_test,W_test)}")
    # print(f"PLS {PLS2(pop_init,voisinage,objets_test,W_test)}")
    PLS(pop_init,voisinage,objets_test,W_test)
    PLS2(pop_init,voisinage,objets_test,W_test)

######## TEST BASIQUE ########
        ###Instance####
n=2
p=2
objets_test, W_test=getInstance(n,p)
objets_test, W_test,indices_from_objets_random_dict_to_objets=getInstance_withRandomSelection(n,p) #choix aléatoire des objets
    ###Données Test####
solution_non_realisable_test1=[1,0,1,1,0]
solution_non_realisable_test2=[0,0,1,1,1]
solution_realisable_test1=[1,0,0,1,1]
solution_realisable_test2=[0,1,0,0,1]
solution_realisable_test3=[0,0,1,0,1]
ens_pot_efficace_test1=[solution_realisable_test2,solution_realisable_test3]
ens_pot_efficace_test2=[solution_realisable_test1]

if __name__== "__main__":
    
    # test_basique()

    #test_PLS(objets_test, W_test)
    ######## Générer les logs de PLS ########
    for n in range(52,101):
        for p in range(1,5):
            if n%2==1:
                print(f"n {n} p {p}")
                objets_test, W_test=getInstance(n,p)
                test_PLS(objets_test, W_test)


    