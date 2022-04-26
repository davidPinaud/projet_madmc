# Projet 
Projet pour la matière MADMC (Modèles et Algorithmes en Décision et Multicritère et Collective) sur l'élicitation de plusieurs modèles multicritères (OWA, Somme pondérée et Intégrale de Choquet) ainsi que l'estimation du front de Pareto avec de la recherche locale.

# Note : 
La verbose n'est qu'une aide pour estimer l'avancée des élicitations, pour voir le résultat complet d'une exécution, veuillez vous rendre sur le log généré, un descriptif sur la structure des logs est fournit dans le rapport.

## Notes de lancement
- Pour lancer PLS:
lancer le fichier PLS.py va lancer pour n=15 et p=3 les deux variantes de PLS codées. Il y aura de la verbose dans la console et les logs seront dans ./logs. Les valeurs de n et de p sont modifiables dans le if __name__== "__main__":

- Pour lancer l'élicitation avec comme agrégateur la somme pondérée:
lancer le fichier elicitation_ponderee.py va lancer pour n=15 et p=4 une élimination incrémentale pour un décideur aléatoire. Il y aura de la verbose dans la console et les logs seront dans ./logs_SP. Les valeurs de n et de p sont modifiables dans le if __name__== "__main__":

- Pour lancer l'élicitation avec comme agrégateur OWA:
lancer le fichier elicitation_OWA.py va lancer pour n=17 et p=4 une élimination incrémentale pour un décideur aléatoire. Il y aura de la verbose dans la console et les logs seront dans ./logs_OWA. Les valeurs de n et de p sont modifiables dans le if __name__== "__main__":

- Pour lancer l'élicitation avec comme agrégateur l'intégrale de Choquet:
lancer le fichier elicitation_choquet.py va lancer pour n=18 et p=4 une élimination incrémentale pour un décideur aléatoire.Il y aura de la verbose dans la console et les logs seront dans ./logs_Choquet. Les valeurs de n et de p sont modifiables dans le if __name__== "__main__":

- Pour lancer la deuxième procédure de résolution:
lancer le fichier rechercheLocale_elicitation.py va lancer pour n=13 et p=3 la méthode pour les 3 différents agrégateur. Il y aura de la verbose dans la console et les logs seront dans ./logs_RL_elici/Choquet, ./logs_RL_elici/SP et ./logs_RL_elici/OWA. Les valeurs de n et de p sont modifiables dans le if __name__== "__main__":

## Test Unitaires :
Lancer unitTest.py, si pas de message d'erreur apparait en console, alors les méthodes testées fonctionnent.

## Afficher les stats et les graphes :
Executer graphs_and_stats.py, les graphes sont interactifs (vous pouvez les tourner, zoomer, etc.)! (une fonction de plot n'est pas appelé : plot_PLS_executionTimes_wrt_n_and_p_3D car elle prends environ 1 minute à s'exécuter dû au grand nombre (>600!) de logs pour PLS1 et PLS2, si vous voulez la lancer, il faut décommenter la dernière ligne du code du fichier)


Les n et p pour ces exécutions ont été choisis de manière à ne pas avoir de trop grosses exécutions.
