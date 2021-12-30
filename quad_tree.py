
#Auteur : David PINAUD
#Description : Essai d'implémentation de quad_tree (non complet)

def isDom(perf1,perf2):
    """true if perf1>perf2 (dom pareto)

    Parameters
    ----------
    perf1 : list
        vecteur performance
    perf2 : list
        vecteur performance

    Returns
    -------
    bool
        True si perf1 domine perf2, False sinon
    """
    hasOneBigger=False
    for critere_i_Sol1,critere_i_Sol2 in zip(perf1,perf2):
        if(critere_i_Sol1<critere_i_Sol2):
            return False
        if(critere_i_Sol1>critere_i_Sol2): #la sol1 est meilleure strictement sur un critère
            hasOneBigger=True
    return True if hasOneBigger else False

def dfs_1(visited, node, noeud_a_tester):
    """DFS récursif qui permet de mettre à jour l'attribut toAdd du noeuds à tester pour savoir si on doit le rajouter à l'arbre ou non (on le rajoute que s'il n'est pas dominé)

    Parameters
    ----------
    visited : set
        les noeuds visités pendant le DFS
    node : Noeud
        noeud courant à regarder
    noeud_a_tester : Noeud
        noeud à tester
    """
    if node not in visited and noeud_a_tester.toAdd:
        if(isDom(node.vecteur_performance,noeud_a_tester.vecteur_performance)):
            noeud_a_tester.toAdd=False
        visited.add(node)
        for enfant in node.enfants:
            dfs_1(visited, enfant, noeud_a_tester)

def dfs_2(visited, node, noeud_a_tester):
    """DFS récursif qui permet de mettre à jour l'attribut toAdd du noeuds à tester pour savoir si on doit le rajouter à l'arbre ou non (on le rajoute que s'il n'est pas dominé)

    Parameters
    ----------
    visited : set
        les noeuds visités pendant le DFS
    node : Noeud
        noeud courant à regarder
    noeud_a_tester : Noeud
        noeud à tester
    """
    if node not in visited and not node.toRemove:
        if(isDom(noeud_a_tester.vecteur_performance,node.vecteur_performance)):
            node.toRemove=True
        visited.add(node)
        for enfant in node.enfants:
            dfs_2(visited, enfant, noeud_a_tester)


class Noeud:
    def __init__(self,vecteur_performance,rootLocal,index) -> None:
        self.vecteur_performance=vecteur_performance
        self.enfants=[]
        self.index=index #id du noeuds dans objets
        self.parent=None #un seul
        #self.rootLocal=rootLocal #l'endroit ou on commen l'algo
        #self.k=[1 if critere_i>=self.rootLocal.vecteur_performance[i] else 0 for i,critere_i in enumerate(self.vecteur_performance)]
        self.k=None
        self.toAdd=True #à ajouter au graphe ou non, on le bascule à False dans isDominatedInTree si il est dominé par un noeud dans le quad tree
        self.toRemove=False #à enlever du graphe ou non, on le bascule à True dans whoIsDominatedInTreeBy quand le noeud est dominé par le noeud à tester
class Quad_tree:
    def __init__(self,nb_critere) -> None:
        self.noeuds=[]
        self.nb_critere=nb_critere
        self.toReinsert=[]
    
    def hasZeroesOrOnesInAtLeastAllLocationsThatkDoes(self,k,k_to_test,value):
        """compare les valeurs des successorship de deux noeuds, 
        quand value = 0 : sert à voir s'il faut regarder dans le sous arbre de racine du noeud correpondant au successorship k 
        pour savoir si le noeud correspondant à k_to_test est dominé ou non
        quand value = 1 : sert à voir s'il faut regarder dans le sous arbre de racine du noeud correpondant au successorship k 
        pour savoir s'il y a des noeuds du sous arbre dominé par le noeud correspondant à k_to_test
        Parameters
        ----------
        k : list
            successorship d'un noeud dans le graphe
        k_to_test : list
            successorship de noeud candidat
        value : int
            valeur binaire

        Returns
        -------
        bool
            True si k a des 0 (ou 1) partout où k_to_test a des 0 (ou 1), False sinon
        """
        for k_i,k_to_test_i in zip(k,k_to_test):
            if(k_i==value and k_to_test_i!=value):
                return False
        return True

    
    def isCandidateDominatedInTree(self,noeud_a_tester):
        """Fonction qui test si un certain noeuds est dominé dans le Quad-tree en regardant aussi les sous arbres

        Parameters
        ----------
        noeud_a_tester : Noeud
            le noeud à tester

        Returns
        -------
        bool
            True s'il est dominé, False sinon
        """
        root_of_subtrees_to_check=[root for root in noeud_a_tester.parent.enfants if self.hasZeroesInAtLeastAllLocationsThatkDoes(noeud_a_tester.k,root.k,0)] # on trouve quels noeuds enfant du parent du noeud à tester qu'il faut considérer comme racine d'un sous arbre à considerer pour le test de domination sur le noeud à tester
        for root in root_of_subtrees_to_check: #on lance des DFS pour essayer de trouver dans les sous arbres si il y a un noeuds qui domine le noeud à tester
            visited = set()
            dfs_1(visited,root,noeud_a_tester)
            if(not noeud_a_tester.toAdd):
                return True
        return False #Si on n'a trouvé aucune dominance

    def isCandidateDominatedInTree_Version2(self,noeud_a_tester):
        """Fonction qui test si un certain noeuds est dominé dans le Quad-tree en ne regardant que les enfants du rootLocal

        Parameters
        ----------
        noeud_a_tester : Noeud
            le noeud à tester

        Returns
        -------
        bool
            True s'il est dominé, False sinon
        """
        child_to_check=[child for child in noeud_a_tester.rootLocal.enfants if self.hasZeroesInAtLeastAllLocationsThatkDoes(noeud_a_tester.k,child.k,0)] # on trouve quels noeuds enfant du parent du noeud à tester qu'il faut considérer comme racine d'un sous arbre à considerer pour le test de domination sur le noeud à tester
        for child in child_to_check: #on lance des DFS pour essayer de trouver dans les sous arbres si il y a un noeuds qui domine le noeud à tester
            if(isDom(child.vecteur_performance,noeud_a_tester.vecteur_performance)):
                noeud_a_tester.toAdd=False
                return True
        return False #Si on n'a trouvé aucune dominance
    
    def deleteDominatedInTreeByCandidate(self,noeud_a_tester):
        root_of_subtrees_to_check=[root for root in noeud_a_tester.parent.enfants if self.hasZeroesInAtLeastAllLocationsThatkDoes(noeud_a_tester.k,root.k,1)]
        for root in root_of_subtrees_to_check:
            visited = set()
            dfs_2(visited,root,noeud_a_tester)
        for node in self.noeuds:
            if node.toRemove :
                node.parent.enfants.remove(node)
                for enfant in node.enfants:
                    self.toReinsert.append(enfant)
                    enfant.parent=None
                node.parent=None
    
    def update_tree(self,candidate):
        if not self.isCandidateDominatedInTree(candidate):
            self.deleteDominatedInTreeByCandidate(candidate)
            exists_same_successorship=False
            for child in candidate.parent.enfants:
                if(child.k==candidate.k):
                    exists_same_successorship=True
                    if not isDom(child.vecteur_performance,candidate.vecteur_performance): #si le candidat n'est pas dominé par y
                        pass
        

# def update_tree(nodeToInsert,quadTree):
#     #Step 1
#     y=quadTree.root
#     #Step 2
#     nodeToInsert.k=[1 if critere_i>=y.vecteur_performance[i] else 0 for i,critere_i in enumerate(nodeToInsert.vecteur_performance)]
#     if nodeToInsert.k==[1 for _ in nodeToInsert.vecteur_performance] or nodeToInsert.vecteur_performance==y.vecteur_performance:
#         return quadTree
#     elif nodeToInsert.k==[0 for _ in nodeToInsert.vecteur_performance]:
        




    
#ne pas oublier : l'arbre est domination free