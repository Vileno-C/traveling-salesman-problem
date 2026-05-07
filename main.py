# Importando a bibliotecas necessarias
import gurobipy as gp
from pulp import *
import tsplib95
import time

#print(listSolvers(onlyAvailable = True))

# Carrega a instância do problema
problem = tsplib95.load_problem('gr17.tsp')

# Obtém o número de nós na instância e as distâncias entre os nós
num_nodes = problem.dimension
print("Número de nós:", num_nodes)
distance_matrix = [[problem.get_weight(node1, node2) for node2 in range(0, num_nodes)] for node1 in range(0, num_nodes)]
#distance_matrix = [[problem.get_weight(node1, node2) for node2 in range(1, num_nodes+1)] for node1 in range(1, num_nodes+1)]

# Dicionario de custos
n = len(distance_matrix) # tamanho da matriz
print("Número de nós:", n)
custos = dict()
for i in range(n):
    for j in range(n):
        custos[i,j] = distance_matrix[i][j]

  ################ Funcoes DL #################

# Dada uma cidade j, encontra qual cidade a rota visita em seguida
def encontrar_prox(x, j):
  next = 0
  for i in range(n):
    if i != j:
      if x[j,i].varValue == 1:
        next = i
  return next

# Retorna uma sub-rota em forma de vetor
def escrever_subtour(x, j):
  subtour = [j]
  next = encontrar_prox(x,j)
  while next != j:
    subtour.append(next)
    next = encontrar_prox(x,next)
  return subtour

# Retorna a solução em forma de um vetor em que cada elemento é uma sub-rota
def escrever_solucao(x):
  solucao = []
  for j in range(n):
    j_solucao = 0
    for i in range(len(solucao)):
      if j in solucao[i]:
        j_solucao = 1
    if j_solucao == 0:
      subtour = escrever_subtour(x,j)
      solucao.append(subtour)
  return solucao

################ Montando e resolvendo o problema #################

# Inicializar o modelo
model = pulp.LpProblem('Modelo', sense=LpMinimize)

# Variaveis de decisão
arestas = [(i,j) for i in range(n) for j in range(n)]
x = LpVariable.dicts("x", arestas, cat="Binary")
u = LpVariable.dicts('u', (i for i in range(n)), lowBound=1, upBound=n-1, cat="Integer")

# Função objetivo
model += lpSum([custos[i,j]*x[i,j] for (i,j) in arestas])

# Restrições
for i in range(n):
  model += lpSum([x[i,j] for j in range(n) if i != j]) == 1

for j in range(n):
  model += lpSum([x[i,j] for i in range(n) if i != j]) == 1

for j in range(n):
  model += x[j,j] == 0



# MTZ
'''
for i in range(1, n):
  for j in range(1, n):
    if i != j:
      model += u[i] - u[j] + n*x[i,j] <= n - 1


# DL

for i in range(2, n):
  for j in range(2, n):
    if i != j:
      model += u[i] - u[j] + (n - 1)*x[i, j] + (n - 3)*x[j, i] <= n - 2

for i in range(2, n):
  if i != 1:
    model += 1 + (n - 3)*x[i,1] + lpSum(x[j,i] for j in range(2, n) if  i != j) <= u[i]

for i in range(2, n):
  if i != 1:
    model += n - 1 - (n -3)*x[1,i] - lpSum(x[i,j] for j in range(2, n) if  i != j) >= u[i]
'''


print('################################# DFJ ##########################')

start_time = time.time()

# Resolve o modelo criando uma restricao a cada sub-rota
qtd_rotas = 0
while qtd_rotas != 1:
 
  #model.solve(GUROBI(msg=False))
  model.solve(PULP_CBC_CMD(msg=True))
  #model.solve(SCIP_CMD(msg=0))
  solucao = escrever_solucao(x)

  qtd_rotas = len(solucao)

  # Cria uma restricao para cada sub-rota
  for k in range(qtd_rotas):
    model += lpSum(x[i,j] for i in solucao[k] for j in solucao[k] if i!=j) <= len(solucao[k]) - 1

end_time = time.time()


print('\n #################### GUROBI: \n')
#print('\n #################### CBC: \n')
#print('\n #################### SCIP: \n')
print("Valor da funcao objetivo:", model.objective.value())
print("\nTempo total: ", round(end_time-start_time,2))