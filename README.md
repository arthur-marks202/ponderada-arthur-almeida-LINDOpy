# Ponderada de Negócios - Problema de Localização de Capacidades (PLC)

##  Introdução
Neste projeto, desenvolvi um sistema em Python para resolver o Problema de Localização de Capacidades (PLC) da empresa fictícia Texas Petro S/A, conforme solicitado na atividade ponderada da disciplina de Negócios.

O problema foi inicialmente resolvido utilizando o software LINDO Classic, e posteriormente repliquei a solução em Python utilizando a biblioteca PuLP.


##  Contexto do Problema

A indústria Texas Petro S/A precisa distribuir 100 toneladas de combustível para seus 5 Centros Consumidores (CC). Atualmente, a empresa possui apenas o CD1 já instalado e deseja avaliar a instalação de mais dois Centros Distribuidores:

| Centro Distribuidor | Status | Custo de Instalação |
|---------------------|--------|---------------------|
| CD1 | Já instalado | R$ 0,00 |
| CD2 | A decidir | R$ 500.000,00 |
| CD3 | A decidir | R$ 450.000,00 |

### Dados de Oferta, Demanda e Custos de Transporte

**Combustível A:**

| CD | CC1 | CC2 | CC3 | CC4 | CC5 | Oferta (t) |
|----|-----|-----|-----|-----|-----|------------|
| CD1 | 60 | 65 | 78 | 67 | 84 | 50 |
| CD2 | 45 | 54 | 76 | 53 | 32 | 75 |
| CD3 | 31 | 43 | 54 | 65 | 72 | 85 |
| **Demanda** | 16 | 20 | 12 | 18 | 14 | **80** |

**Combustível B:**

| CD | CC1 | CC2 | CC3 | CC4 | CC5 | Oferta (t) |
|----|-----|-----|-----|-----|-----|------------|
| CD1 | 37 | 39 | 54 | 45 | 25 | 30 |
| CD2 | 23 | 34 | 21 | 34 | 70 | 60 |
| CD3 | 21 | 38 | 45 | 38 | 68 | 50 |
| **Demanda** | 10 | 14 | 12 | 16 | 8 | **60** |

---

##  a) Modelo Matemático

O modelo matemático que desenvolvi segue a formulação clássica do PLC:

### Variáveis de Decisão

- **yᵢ** ∈ {0, 1}: variável binária que indica se o CD i será instalado (1) ou não (0)
- **xᵢⱼ** ≥ 0: quantidade de combustível transportada do CD i para o CC j

### Função Objetivo

Minimizar o custo total (instalação + transporte):

$$\text{MIN } Z = \sum_{i \in I} f_i \cdot y_i + \sum_{i \in I} \sum_{j \in J} c_{ij} \cdot x_{ij}$$
*formula de LaTeX feita no chat*

Onde:
- $f_i$ = custo de instalação do CD i
- $c_{ij}$ = custo de transporte do CD i para o CC j

### Restrições

**1. Restrição de Capacidade:** A quantidade enviada por cada CD não pode exceder sua oferta (e só pode enviar se estiver instalado):

$$\sum_{j \in J} x_{ij} \leq a_i \cdot y_i, \quad \forall i \in I$$
*formula de LaTeX feita no chat*

**2. Restrição de Demanda:** Toda demanda de cada CC deve ser atendida:

$$\sum_{i \in I} x_{ij} = b_j, \quad \forall j \in J$$
*formula de LaTeX feita no chat*

**3. Restrição de Integralidade e Não-negatividade:**

$$x_{ij} \geq 0, \quad \forall i \in I, \forall j \in J$$
$$y_i \in \{0, 1\}, \quad \forall i \in I$$
*formula de LaTeX feita no chat*

**4. CD1 já instalado:**

$$y_1 = 1$$
*formula de LaTeX feita no chat (eu nâo sei LaTex)*

---

##  b) Solução Ótima

Após executar o solver, obtive os seguintes resultados:

### Combustível A

| Métrica | Valor |
|---------|-------|
| **Status** | Ótimo |
| **CDs Instalados** | CD1 + CD3 |
| **Custo de Instalação** | R$ 450.000,00 |
| **Custo de Transporte** | R$ 4.182,00 |
| **CUSTO TOTAL** | **R$ 454.182,00** |

**Plano de Transporte:**

| De/Para | CC1 | CC2 | CC3 | CC4 | CC5 | Total |
|---------|-----|-----|-----|-----|-----|-------|
| CD1 | 0 | 0 | 0 | 0 | 0 | 0 |
| CD2 | 0 | 0 | 0 | 0 | 0 | 0 |
| CD3 | 16 | 20 | 12 | 18 | 14 | **80** |

### Combustível B

| Métrica | Valor |
|---------|-------|
| **Status** | Ótimo |
| **CDs Instalados** | CD1 + CD3 |
| **Custo de Instalação** | R$ 450.000,00 |
| **Custo de Transporte** | R$ 2.092,00 |
| **CUSTO TOTAL** | **R$ 452.092,00** |

**Plano de Transporte:**

| De/Para | CC1 | CC2 | CC3 | CC4 | CC5 | Total |
|---------|-----|-----|-----|-----|-----|-------|
| CD1 | 0 | 2 | 0 | 0 | 8 | 10 |
| CD2 | 0 | 0 | 0 | 0 | 0 | 0 |
| CD3 | 10 | 12 | 12 | 16 | 0 | **50** |

---

##  c) Interpretação da Solução

### Conclusões Principais

1. **Decisão de Instalação:** A solução ótima indica que a Texas Petro S/A deve instalar apenas o CD3, mantendo o CD1 que já está operacional. O CD2 não deve ser instalado.

2. **Justificativa Econômica:**
   - O CD3 tem custo de instalação menor (R$ 450.000) comparado ao CD2 (R$ 500.000)
   - O CD3 possui a maior capacidade de oferta (85 toneladas para A e 50 para B)
   - Os custos de transporte do CD3 são competitivos, especialmente para os CCs mais próximos

3. **Estratégia de Distribuição:**
   - **Combustível A:** Toda a demanda (80 toneladas) é atendida exclusivamente pelo CD3, que possui capacidade suficiente (85t) e custos de transporte mais baixos para a maioria dos CCs
   - **Combustível B:** A distribuição é compartilhada entre CD1 (10t) e CD3 (50t), otimizando os custos de transporte

4. **Custo Total Combinado:** A operação para ambos os combustíveis resulta em um custo total de **R$ 906.274,00**, sendo:
   - R$ 454.182,00 para o Combustível A
   - R$ 452.092,00 para o Combustível B

### Por que o CD2 não foi selecionado?

Mesmo que o CD2 tenha bons custos de transporte para alguns CCs (como CC5 com custo 32 para Combustível A), o custo de instalação de R$ 500.000 não compensa quando comparado ao CD3, que além de ser R$ 50.000 mais barato para instalar, consegue atender toda a demanda com custos de transporte competitivos.

---

##  Tecnologias Utilizadas

- **Python 3.x**
- **PuLP** - Biblioteca de otimização para programação linear
- **LINDO Classic** - Software de otimização (resolução original)

##  Arquivos do Projeto

| Arquivo | Descrição |
|---------|-----------|
| `plc_solver.py` | Script Python com o solver completo |
| `lindo_combustivel_A.txt` | Modelo no formato LINDO para Combustível A |
| `lindo_combustivel_B.txt` | Modelo no formato LINDO para Combustível B |
| `assets/formulaLINDO.png` | Captura da fórmula no LINDO Classic |
| `assets/resultadoLINDO.png` | Captura do resultado no LINDO Classic |

##  Como Executar

```bash
# Instalar dependência
pip install pulp

# Executar o solver
python plc_solver.py
```

---

**Aluno:** Arthur Almeida
**Disciplina:** Negócios
**Professora:**  Natália Kloeckner