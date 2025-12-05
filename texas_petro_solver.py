"""
Sistema de Otimização para o Problema de Localização e Capacidade (PLC)
Texas Petro S/A - Distribuição de Combustível

Autor: Arthur Almeida
Data: 2025-12-05
"""

from pulp import *
import numpy as np


class TexasPetroSolver:
    """
    Solver para o Problema de Localização e Capacidade da Texas Petro S/A
    """
    
    def __init__(self):
        # Dados do problema
        self.num_cds = 3  # CD1, CD2, CD3
        self.num_ccs = 5  # CC1, CC2, CC3, CC4, CC5
        
        # Custos de transporte (R$ por 1.000kg) - Combustível A
        self.custos_transporte = {
            (1, 1): 60, (1, 2): 65, (1, 3): 78, (1, 4): 67, (1, 5): 84,
            (2, 1): 45, (2, 2): 54, (2, 3): 76, (2, 4): 53, (2, 5): 32,
            (3, 1): 31, (3, 2): 43, (3, 3): 54, (3, 4): 65, (3, 5): 72
        }
        
        # Oferta de cada CD (toneladas)
        self.ofertas = {1: 50, 2: 75, 3: 85}
        
        # Demanda de cada CC (toneladas)
        self.demandas = {1: 16, 2: 20, 3: 12, 4: 18, 5: 14}
        
        # Custos fixos de instalação (R$)
        # CD1 já está instalado (custo = 0)
        # CD2 e CD3 precisam ser instalados
        self.custos_instalacao = {1: 0, 2: 500000, 3: 450000}
        
        # Modelo
        self.modelo = None
        self.x = {}  # Variáveis de transporte
        self.y = {}  # Variáveis de instalação
        
    def criar_modelo(self):
        """
        Cria o modelo matemático do PLC
        """
        # Inicializar o modelo
        self.modelo = LpProblem("Texas_Petro_PLC", LpMinimize)
        
        # Variáveis de decisão
        # x[i,j] = quantidade transportada do CD i para o CC j (em toneladas)
        for i in range(1, self.num_cds + 1):
            for j in range(1, self.num_ccs + 1):
                self.x[i, j] = LpVariable(f"x_{i}_{j}", lowBound=0, cat='Continuous')
        
        # y[i] = 1 se o CD i é instalado, 0 caso contrário
        for i in range(1, self.num_cds + 1):
            if i == 1:
                # CD1 já está instalado
                self.y[i] = LpVariable(f"y_{i}", cat='Binary')
                self.modelo += self.y[i] == 1, f"CD1_ja_instalado"
            else:
                self.y[i] = LpVariable(f"y_{i}", cat='Binary')
        
        # Função Objetivo
        # Minimizar: Custo de Instalação + Custo de Transporte
        custo_instalacao = lpSum([self.custos_instalacao[i] * self.y[i] 
            for i in range(1, self.num_cds + 1)])
        
        # Converter toneladas para 1.000kg (1 tonelada = 1 unidade de 1.000kg)
        custo_transporte = lpSum([self.custos_transporte[i, j] * self.x[i, j] 
            for i in range(1, self.num_cds + 1) 
            for j in range(1, self.num_ccs + 1)])
        
        self.modelo += custo_instalacao + custo_transporte, "Custo_Total"
        
        # Restrições
        # 1. Restrição de capacidade: o que sai de cada CD não pode exceder sua oferta
        #    e só pode sair se o CD estiver instalado
        for i in range(1, self.num_cds + 1):
            self.modelo += (
                lpSum([self.x[i, j] for j in range(1, self.num_ccs + 1)]) 
                <= self.ofertas[i] * self.y[i],
                f"Capacidade_CD{i}"
            )
        
        # 2. Restrição de demanda: cada CC deve receber exatamente sua demanda
        for j in range(1, self.num_ccs + 1):
            self.modelo += (
                lpSum([self.x[i, j] for i in range(1, self.num_cds + 1)]) 
                == self.demandas[j],
                f"Demanda_CC{j}"
            )
        
    def resolver(self):
        """
        Resolve o modelo de otimização
        """
        if self.modelo is None:
            self.criar_modelo()
        
        # Resolver usando o solver padrão
        self.modelo.solve(PULP_CBC_CMD(msg=1))
        
        return LpStatus[self.modelo.status]
    
    def exibir_resultados(self):
        """
        Exibe os resultados da otimização de forma formatada
        """
        print("=" * 80)
        print("TEXAS PETRO S/A - SOLUÇÃO DO PROBLEMA DE LOCALIZAÇÃO E CAPACIDADE")
        print("=" * 80)
        print()
        
        # Status da solução
        status = LpStatus[self.modelo.status]
        print(f"Status da Solução: {status}")
        print()
        
        if status == "Optimal":
            # a) Modelo Matemático
            print("a) MODELO MATEMÁTICO")
            print("-" * 80)
            print("Minimizar Z = Σ f_i * y_i + Σ Σ c_ij * x_ij")
            print()
            print("Sujeito a:")
            print("  Σ x_ij ≤ a_i * y_i,  ∀ i ∈ I  (Capacidade dos CDs)")
            print("  Σ x_ij = b_j,         ∀ j ∈ J  (Demanda dos CCs)")
            print("  x_ij ≥ 0,             ∀ i ∈ I, ∀ j ∈ J")
            print("  y_i ∈ {0,1},         ∀ i ∈ I")
            print()

