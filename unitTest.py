from instance_loader import getInstance
from PLS import *


def test_1_mise_a_jour_ens_potentiellement_efficace():
    """test si quand un candidat non dominé par les sols pot eff arrive, on le rajoute bien et on efface bien les nouveaux dominées
    """
    ens_pot_efficace, hasChanged=mise_a_jour_ens_potentiellement_efficace(ens_pot_efficace_test1,solution_realisable_test1,objets_test)
    return hasChanged==True and ens_pot_efficace==[solution_realisable_test1]

def test_2_mise_a_jour_ens_potentiellement_efficace():
    """test si quand un candidat dominé par au moins un sol pot eff arrive, on le rajoute pas et on efface rien
    """
    ens_pot_efficace, hasChanged=mise_a_jour_ens_potentiellement_efficace(ens_pot_efficace_test2,solution_realisable_test2,objets_test)
    return hasChanged==False and ens_pot_efficace==[solution_realisable_test1]

def test_isDomFaible():
    cond= True==isDomFaible(solution_realisable_test1,solution_realisable_test2,objets_test)
    cond = cond and False==isDomFaible(solution_realisable_test2,solution_realisable_test1,objets_test)
    cond = cond and False==isDomFaible(solution_realisable_test2,solution_realisable_test3,objets_test)
    cond = cond and False==isDomFaible(solution_realisable_test3,solution_realisable_test2,objets_test)
    return cond

def test_isDom():
    cond= True==isDom(solution_realisable_test1,solution_realisable_test2,objets_test)
    cond = cond and False==isDom(solution_realisable_test2,solution_realisable_test1,objets_test)
    cond = cond and False==isDomStrict(solution_realisable_test2,solution_realisable_test3,objets_test)
    cond = cond and False==isDomStrict(solution_realisable_test3,solution_realisable_test2,objets_test)
    return cond

def test_isDomStrict():
    cond=True==isDomStrict(solution_realisable_test1,solution_realisable_test2,objets_test)
    cond = cond and False==isDomStrict(solution_realisable_test2,solution_realisable_test1,objets_test)
    cond = cond and False==isDomStrict(solution_realisable_test2,solution_realisable_test3,objets_test)
    cond = cond and False==isDomStrict(solution_realisable_test3,solution_realisable_test2,objets_test)
    return cond

def test_basiques(objets_test,W_test):

    ####Données Test####
    solution_non_realisable_test1=[1,0,1,1,0]
    solution_non_realisable_test2=[0,0,1,1,1]
    solution_realisable_test1=[1,0,0,1,1]
    solution_realisable_test2=[0,1,0,0,1]
    solution_realisable_test3=[0,0,1,0,1]
    ens_pot_efficace_test1=[solution_realisable_test2,solution_realisable_test3]
    ens_pot_efficace_test2=[solution_realisable_test1]
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
    print(f"voisinage {voisinage(solution_realisable_test3,objets_test,W_test)}")

def test_PLS(objets_test, W_test):
    pop_init=genererPopulationInitiale(20,objets_test,W_test)
    print(f"genererPopulationInitiale {pop_init}, longueur {len(pop_init)}")
    print(f"PLS {PLS(pop_init,voisinage,objets_test,W_test)}")
if __name__== "__main__":
    ####Instance####
    n=8
    p=3
    objets_test, W_test=getInstance(n,p)
    test_PLS(objets_test, W_test)
    
    