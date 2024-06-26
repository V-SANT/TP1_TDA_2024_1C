import time
import pulp
from pulp import PULP_CBC_CMD
import os
from constantes import *

def traducir(groups,maestros):
    grupos = []
    for group in groups:
        grupo = []
        for i in group:
            grupo.append(maestros[i])
        grupos.append(grupo)
    return grupos

def p_opt_tribu_agua_pl(maestros, habilidades, k):
    # Cantidad de maestros
    n = len(habilidades)

    #Creo el problem que va a ser de minimización
    problem = pulp.LpProblem("Diferencia_minima_entre_el_máximo_y_mínimo", pulp.LpMinimize)
    
    # Inicializo las variables

    # xij = 1 si el maestro i pertenece al grupo j, 0 en caso contrario. Es binaria
    x = pulp.LpVariable.dicts("x", ((i, j) for i in range(n) for j in range(k)), 0, 1, cat='Binary')

    # Sj = Suma de las habilidades de los maestros en el grupo j
    s = pulp.LpVariable.dicts("S", (j for j in range(k)), lowBound=0, cat='Continuous')

    # Sumatoria de las habilidades del maximo grupo
    max_group = pulp.LpVariable("M", lowBound=0, cat='Continuous')

    # Sumatoria de las habilidades del minimo grupo
    min_group = pulp.LpVariable("m", lowBound=0, cat='Continuous')
    
    # Funcion que queremos minimizar
    problem += max_group - min_group
    
    # 1 maestro pertenece a un solo grupo. Itero por cada maestro y le digo que pertenece a un solo grupo
    # Si tenemos 3 grupos el caso para un maestro seria: x11 + x12 + x13 = 1. Solo pertenece a un grupo
    for i in range(n):
        problem += pulp.lpSum(x[i, j] for j in range(k)) == 1
    
    # Por cada grupo que tengo
    for j in range(k):
        # La suma de las habilidades de los maestros en el grupo j (Sj) es igual a la suma de las habilidades de los maestros
        # Por cada maestro i me fijo si pertenece o no al grupo (xij) y si pertenece habilito que se sume la habilidad
        problem += s[j] == pulp.lpSum(x[i, j] * habilidades[i] for i in range(n))

        # El máximo grupo tiene que sesr mayor o igual a todos los grupos
        problem += max_group >= s[j]

        # El minimo grupo tiene que ser menor o igual a todos los grupos
        problem += min_group <= s[j]
    
    # Resolvemos el problema
    problem.solve(PULP_CBC_CMD(msg=False))
    
    # Obtengo los resultados. Para eso creo mi lista de listas de grupos
    groups = [[] for _ in range(k)]
    # Por cada maestro
    for i in range(n):
        # Por cada grupo
        for j in range(k):
            # Me fijo si ese maestro pertenece al grupo j. Si pertenece lo agrego a la lista de grupos
            if pulp.value(x[i, j]) == 1:
                groups[j].append(i)
                break

    # Calcular las sumas de habilidades por grupo
    sumas = [sum(habilidades[i] for i in group) for group in groups]
    
    # Calcular el coeficiente (suma de los cuadrados de las sumas)
    coeficiente = sum(suma**2 for suma in sumas)
    
    return traducir(groups,maestros), coeficiente

