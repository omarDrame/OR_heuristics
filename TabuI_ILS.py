# -*- coding: utf-8 -*-
"""
Created on Sat Jan  1 14:59:01 2022

@author: De Romance Flavien
         Dramé Omar
         Fourest Lucas
         Zghidi Abir
"""

import random as rd
import job
import sommet
import ordonnancement
import flowshop
import time as time

# =============================================================================
# Fonctions
# =============================================================================

#Retourne le voisinage acceptable avec en entré
#V un voisinage complet, L une liste tabou et
#un ordonancement
def voisinage_acceptable(V,L,ordo_curr):
    """
    critère d'acceptation : on garde ttes les solutions (des ordo) de V qui
    n'appartiennent pas à  L OU qui vérifient le critère d'aspiration : i.e 
    qui sont meilleures que ordo_curr en terme de durée.
    Cela revient à rejeter ttes les solutions de V appartenant à L ET étant
    moins bien que ord_curr.
    """
    
    d_curr=ordo_curr.duree
    Vp=[]
    for ordo in V:
        if (contains(ordo,L)==False) or (ordo.duree < d_curr):
            Vp.append(ordo)     
    return Vp


#Retourne le voisinage pour un ordonancement donné
def voisinage(ordo):
    
    V=[]
    n_machines = ordo.nombre_machines
    seq=ordo.sequence
    l=len(seq)
    P=toutespaires(l)
    for k in range(len(P)):
        ordo_voisin=permuter(seq, n_machines, P[k][0],P[k][1])
        V.append(ordo_voisin)
    return V

# Dans une sequence de job, permute les jobs 
#à la positioin i et j.
def permuter(sequence_jobs,n_machines,i,j):
    S=sequence_jobs.copy()
    s=S[i]
    S[i]=S[j]
    S[j]=s
    O = ordonnancement.Ordonnancement(n_machines)
    O.ordonnancer_liste_job(S)
    return O
    
# Retourne True si les deux ordonnancements sont identiques
def equals(ordo1,ordo2):
    if ordo2.nombre_machines==ordo2.nombre_machines:
        if ordo1.sequence == ordo2.sequence:
            return True
    return False

# Retourne True si l'odonnancement ordo
# est dans la liste tabu L
def contains(ordo,L):
    for O in L:
        if (equals(O,ordo)):
            return True
    return False
    
    
# Retourne une liste P contenant toutes les combinaisons
# de parité inferieur à l'entier n.
def toutespaires(n):
    P=[]
    for i in range(n-1):
        for j in range(i+1,n):
            P.append([i,j])
    return P

#Retourne une lites S contenant l'ordre 
#des numéros des jobs
def sequence_num(seq):
    S=[]
    for k in range (len(seq)):
        S.append(seq[k].numero)
    return S

#Retoune le meilleur ordonnancement i.e. le plus court
# d'un voisinage d'odonnacement Vp
def best_of(Vp):
    best=Vp[0]
    for O in Vp:
        if O.duree<best.duree:
            best=O
            best.ordonnancer_liste_job(O.sequence)
    return best 

# =============================================================================
# Recherche tabou
# =============================================================================

# Les constantes
N_max_tabou =100  #nombre d'itération max
n_max_tabou = 7  # nombre max d'itération sans amélioration
max_tabou_liste=30  #nombre maximum de valeur dans la liste tabou L

#Heuristique tabou
def tabu(flowshop):
    N=0 #itérations max
    n=0 #itérations sans améliorations max
    #On prend comme solution de départ le NEH
    l0 = flowshop.ordre_NEH()
    #ordo_courant
    ordo_c = ordonnancement.Ordonnancement(flowshop.nombre_machines)
    ordo_c.ordonnancer_liste_job(l0)
    #ordo_optimal
    ordo_opt = ordo_c
    #L est la liste des odro tabu
    L=[ordo_c]
    
    while (N<N_max_tabou) and (n<n_max_tabou):
        N=N+1      
        V=voisinage(ordo_c)
        Vp=voisinage_acceptable(V, L, ordo_c)  
        #On prend le meilleur voisinage de l'ordo_courant
        ordo_c=best_of(Vp)
        #Si l'ordo courant est meilleur que celui enregistré
        #on le garde en mémoire
        if (ordo_c.duree<ordo_opt.duree):
            n=0
            ordo_opt=ordo_c
            ordo_opt.ordonnancer_liste_job(ordo_c.sequence)
        #Sinon on incrémente, une valeur de plus sans amélioration
        elif (ordo_c.duree>=ordo_opt.duree):
            n=n+1
        #Si l'odonnancement courant est hors de L on l'ajoute
        if (contains(ordo_c,L)==False):
            L.append(ordo_c)
        #Si la L est trop grand on supprime la première valeur
        if (len(L)>= max_tabou_liste):
                L.pop(0)            
    return ordo_opt

# =============================================================================
# Recherche ILS
# =============================================================================

# Les constantes
n_max_recherche_local=100 # nb d'iter max de rl 
N_max_ils=100  # nb d'iter max d'ils
n_max_ils=100 # nb iter max d'ils sans amélioration
 
# Non utilisé
def perturbation1(l):
    l0=[]
    for i in range(len(l)):
        l0.append(l[len(l)-1-i])
    return l0

# Pertubation d'une liste de jobs l
# Echange entre 2 paires de valeurs dans la liste
def perturbation2(l):
        l0=[]
        if len(l)==3:
            l0.append(l[2])
            l0.append(l[1])
            l0.append(l[0])
            return l0
        if len(l)>4:
            i=rd.randint(0,len(l)-4)
            j=rd.randint(i+2,len(l)-2)
            l[i],l[j]=l[j],l[i]
            l[i+1],l[j+1]=l[j+1],l[i+1]
            return l

    
        
#☻Retourne un ordo minimum local 
def recherche_local(flowshop,l0):
    n=0 #itérations sans améliorations max
    ordo_c = ordonnancement.Ordonnancement(flowshop.nombre_machines)
    ordo_opt=ordonnancement.Ordonnancement(flowshop.nombre_machines)
    ordo_c.ordonnancer_liste_job(l0)
    ordo_opt.ordonnancer_liste_job(ordo_c.sequence)
    while (n<n_max_recherche_local):
        V=voisinage(ordo_c)  
        ordo_c.ordonnancer_liste_job(best_of(V).sequence)        
        if (ordo_c.duree<ordo_opt.duree):
            n=0
            ordo_opt.ordonnancer_liste_job(ordo_c.sequence)
        elif (ordo_c.duree>=ordo_opt.duree):
            n=n+1
    return ordo_opt
        

def ils(flowshop) :
    
    T1 = time.time() + 5*60 
    N=0 #itérations max
    n=0 #itérations sans améliorations max 
         
    #l=[job for job in flowshop.liste_jobs]
    #l=perturbation2(l)
    
    #On prend comme solution de départ le NEH
    l0 = flowshop.ordre_NEH()    
    ordo_c = ordonnancement.Ordonnancement(flowshop.nombre_machines)
    ordo_c.ordonnancer_liste_job(l0)    
    ordo_opt=ordonnancement.Ordonnancement(flowshop.nombre_machines)
    ordo_opt.ordonnancer_liste_job(ordo_c.sequence)
            
    while (N<N_max_ils) and (n<n_max_ils) and (time.time() < T1):            
        N+=1
        # On applique la recherche local
        ordo_c.ordonnancer_liste_job(recherche_local(flowshop, ordo_c.sequence).sequence)
        if (ordo_c.duree<ordo_opt.duree):
            n=0
            ordo_opt.ordonnancer_liste_job(ordo_c.sequence)
            
        elif (ordo_c.duree>=ordo_opt.duree):
            n+=1
            #On perturbe complètement l'ordo_c 
            #Pour trouver un autre voisinnage
            l=perturbation2(ordo_c.sequence)
    ordo_c.ordonnancer_liste_job(l)
    ordo_final=ordonnancement.Ordonnancement(flowshop.nombre_machines)
    ordo_final.ordonnancer_liste_job(ordo_opt.sequence) 
    return ordo_final.afficher()
    
# =============================================================================
# Main
# =============================================================================
    
if __name__ == "__main__":
    print("--- Tests ---")
    prob = flowshop.Flowshop()
    prob.definir_par_fichier("tai12.txt")
    
    o = ordonnancement.Ordonnancement(prob.nombre_machines)

    print("Ordo NEH :")
    l = prob.ordre_NEH()
    o.ordonnancer_liste_job(l)
    print(sequence_num(l),", duree ", o.duree)
    print()
    
    
    print("Recherche tabou :")
    tabu(prob).afficher()
    print()
    
    
    print("Recherche ILS : ")
    ils(prob)
    
