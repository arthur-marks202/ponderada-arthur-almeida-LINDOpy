"""
Problema de Localização de Capacidades (PLC) - Texas Petro S/A
Resolução usando PuLP (similar ao LINDO Classic)

Autor: Sistema de resolução automática
Baseado no modelo matemático:
    Minimizar Z = Σ(i∈I) fi*yi + Σ(i∈I)Σ(j∈J) cij*xij

    Sujeito a:
    Σ(j∈J) xij ≤ ai*yi, ∀i∈I  (restrição de capacidade)
    Σ(i∈I) xij = bj, ∀j∈J     (restrição de demanda)
    xij ≥ 0, ∀i∈I, ∀j∈J
    yi ∈ {0,1}, ∀i∈I
"""

from pulp import *


def gerar_formato_lindo(custos_instalacao, custos_transporte, ofertas, demandas, cds_instalados, nome="PLC"):
    """
    Gera o modelo no formato LINDO Classic
    """
    num_cds = len(ofertas)
    num_ccs = len(demandas)

    lindo_code = []
    lindo_code.append(f"! {nome} - Problema de Localização de Capacidades")
    lindo_code.append("! Texas Petro S/A")
    lindo_code.append("")

    # Função Objetivo
    lindo_code.append("MIN")

    termos = []
    # Custos de instalação
    for i in range(num_cds):
        if custos_instalacao[i] > 0:
            termos.append(f"{custos_instalacao[i]} Y{i+1}")

    # Custos de transporte
    for i in range(num_cds):
        for j in range(num_ccs):
            termos.append(f"{custos_transporte[i][j]} X{i+1}{j+1}")

    # Quebrar em linhas de até 60 caracteres
    linha_atual = ""
    for termo in termos:
        if len(linha_atual) + len(termo) + 3 > 60:
            lindo_code.append(linha_atual)
            linha_atual = "+ " + termo
        else:
            if linha_atual:
                linha_atual += " + " + termo
            else:
                linha_atual = termo
    if linha_atual:
        lindo_code.append(linha_atual)

    lindo_code.append("")
    lindo_code.append("SUBJECT TO")
    lindo_code.append("")

    # Restrições de capacidade
    lindo_code.append("! Restrições de Capacidade")
    for i in range(num_cds):
        restricao = " + ".join([f"X{i+1}{j+1}" for j in range(num_ccs)])
        restricao += f" - {ofertas[i]} Y{i+1} <= 0"
        lindo_code.append(restricao)

    lindo_code.append("")

    # Restrições de demanda
    lindo_code.append("! Restrições de Demanda")
    for j in range(num_ccs):
        restricao = " + ".join([f"X{i+1}{j+1}" for i in range(num_cds)])
        restricao += f" = {demandas[j]}"
        lindo_code.append(restricao)

    lindo_code.append("")

    # CDs já instalados
    if cds_instalados:
        lindo_code.append("! CDs já instalados")
        for i in cds_instalados:
            lindo_code.append(f"Y{i+1} = 1")

    lindo_code.append("")
    lindo_code.append("END")
    lindo_code.append("")

    # Variáveis inteiras (binárias)
    lindo_code.append("INT")
    for i in range(num_cds):
        lindo_code.append(f"Y{i+1}")

    return "\n".join(lindo_code)

def resolver_plc(nome_problema, custos_instalacao, custos_transporte, ofertas, demandas, cds_instalados):
    """
    Resolve o Problema de Localização de Capacidades
    
    Parâmetros:
    - nome_problema: Nome identificador do problema
    - custos_instalacao: Lista com custos de instalação de cada CD [f1, f2, f3]
    - custos_transporte: Matriz de custos de transporte [CD][CC]
    - ofertas: Lista com oferta de cada CD [a1, a2, a3]
    - demandas: Lista com demanda de cada CC [b1, b2, b3, b4, b5]
    - cds_instalados: Lista de CDs já instalados (índices começando em 0)
    """
    
    num_cds = len(ofertas)
    num_ccs = len(demandas)
    
    # Criar o problema de minimização
    prob = LpProblem(nome_problema, LpMinimize)
    
    # Variáveis de decisão
    # yi = 1 se CD i é instalado, 0 caso contrário
    y = [LpVariable(f"y{i+1}", cat='Binary') for i in range(num_cds)]
    
    # xij = quantidade transportada do CD i para CC j
    x = [[LpVariable(f"x{i+1}{j+1}", lowBound=0, cat='Continuous') 
        for j in range(num_ccs)] for i in range(num_cds)]
    
    # Função Objetivo: Minimizar custos de instalação + custos de transporte
    prob += (
        lpSum([custos_instalacao[i] * y[i] for i in range(num_cds)]) +
        lpSum([custos_transporte[i][j] * x[i][j] 
            for i in range(num_cds) for j in range(num_ccs)])
    ), "Custo_Total"
    
    # Restrições de capacidade: Σ(j) xij ≤ ai * yi
    for i in range(num_cds):
        prob += (
            lpSum([x[i][j] for j in range(num_ccs)]) <= ofertas[i] * y[i],
            f"Capacidade_CD{i+1}"
        )
    
    # Restrições de demanda: Σ(i) xij = bj
    for j in range(num_ccs):
        prob += (
            lpSum([x[i][j] for i in range(num_cds)]) == demandas[j],
            f"Demanda_CC{j+1}"
        )
    
    # CDs já instalados devem permanecer instalados
    for i in cds_instalados:
        prob += y[i] == 1, f"CD{i+1}_Instalado"
    
    # Resolver o problema
    prob.solve(PULP_CBC_CMD(msg=0))
    
    return prob, y, x


def exibir_resultados(prob, y, x, nome, custos_instalacao, custos_transporte, ofertas, demandas):
    """Exibe os resultados da otimização"""
    
    num_cds = len(y)
    num_ccs = len(demandas)
    
    print("=" * 70)
    print(f"RESULTADO - {nome}")
    print("=" * 70)
    print(f"\nStatus: {LpStatus[prob.status]}")
    print(f"\nValor Ótimo da Função Objetivo: R$ {value(prob.objective):,.2f}")
    
    print("\n" + "-" * 40)
    print("DECISÕES DE INSTALAÇÃO:")
    print("-" * 40)
    
    custo_instalacao_total = 0
    for i in range(num_cds):
        status = "INSTALADO" if value(y[i]) == 1 else "NÃO INSTALADO"
        custo = custos_instalacao[i] if value(y[i]) == 1 else 0
        custo_instalacao_total += custo
        print(f"  CD{i+1}: {status} (Custo: R$ {custos_instalacao[i]:,.2f})")
    
    print(f"\n  Custo Total de Instalação: R$ {custo_instalacao_total:,.2f}")
    
    print("\n" + "-" * 40)
    print("PLANO DE TRANSPORTE (toneladas):")
    print("-" * 40)
    
    # Cabeçalho
    header = "       " + "".join([f"CC{j+1:>8}" for j in range(num_ccs)]) + "    Total"
    print(header)
    
    custo_transporte_total = 0
    for i in range(num_cds):
        linha = f"  CD{i+1}: "
        total_cd = 0
        for j in range(num_ccs):
            val = value(x[i][j])
            linha += f"{val:>8.1f}"
            total_cd += val
            custo_transporte_total += val * custos_transporte[i][j]
        linha += f"  {total_cd:>6.1f}"
        print(linha)
    
    # Linha de demanda atendida
    print("  " + "-" * (8 * num_ccs + 15))
    demanda_linha = "  Dem.: "
    for j in range(num_ccs):
        total_cc = sum(value(x[i][j]) for i in range(num_cds))
        demanda_linha += f"{total_cc:>8.1f}"
    print(demanda_linha)
    
    print(f"\n  Custo Total de Transporte: R$ {custo_transporte_total:,.2f}")
    
    print("\n" + "=" * 70)
    print("INTERPRETAÇÃO DA SOLUÇÃO:")
    print("=" * 70)
    
    cds_abertos = [i+1 for i in range(num_cds) if value(y[i]) == 1]
    print(f"\n  → A solução ótima indica que os seguintes CDs devem operar: {cds_abertos}")
    print(f"  → Custo total (instalação + transporte): R$ {value(prob.objective):,.2f}")
    
    return value(prob.objective)


def main():
    """
    Programa Principal - Texas Petro S/A
    Problema de Localização de Capacidades
    """

    print("\n" + "█" * 70)
    print("  TEXAS PETRO S/A - PROBLEMA DE LOCALIZAÇÃO DE CAPACIDADES")
    print("  Resolução via Programação Linear Inteira Mista")
    print("█" * 70)

    # =========================================================================
    # DADOS DO PROBLEMA
    # =========================================================================

    # Custos de instalação (CD1 já está instalado, custo = 0)
    # CD1: já instalado, CD2: R$ 500.000, CD3: R$ 450.000
    custos_instalacao = [0, 500000, 450000]

    # CD1 já está instalado (índice 0)
    cds_instalados = [0]

    # -------------------------------------------------------------------------
    # COMBUSTÍVEL A
    # -------------------------------------------------------------------------
    print("\n" + "▓" * 70)
    print("  COMBUSTÍVEL A")
    print("▓" * 70)

    # Custos de transporte [CD][CC] - Combustível A
    custos_transporte_A = [
        [60, 65, 78, 67, 84],  # CD1 -> CC1, CC2, CC3, CC4, CC5
        [45, 54, 76, 53, 32],  # CD2 -> CC1, CC2, CC3, CC4, CC5
        [31, 43, 54, 65, 72],  # CD3 -> CC1, CC2, CC3, CC4, CC5
    ]

    # Ofertas (capacidade) de cada CD em toneladas
    ofertas_A = [50, 75, 85]

    # Demandas de cada CC em toneladas
    demandas_A = [16, 20, 12, 18, 14]  # Total = 80 toneladas

    prob_A, y_A, x_A = resolver_plc(
        "Combustivel_A",
        custos_instalacao,
        custos_transporte_A,
        ofertas_A,
        demandas_A,
        cds_instalados
    )

    resultado_A = exibir_resultados(
        prob_A, y_A, x_A, "COMBUSTÍVEL A",
        custos_instalacao, custos_transporte_A, ofertas_A, demandas_A
    )

    # -------------------------------------------------------------------------
    # COMBUSTÍVEL B
    # -------------------------------------------------------------------------
    print("\n" + "▓" * 70)
    print("  COMBUSTÍVEL B")
    print("▓" * 70)

    # Custos de transporte [CD][CC] - Combustível B
    custos_transporte_B = [
        [37, 39, 54, 45, 25],  # CD1 -> CC1, CC2, CC3, CC4, CC5
        [23, 34, 21, 34, 70],  # CD2 -> CC1, CC2, CC3, CC4, CC5
        [21, 38, 45, 38, 68],  # CD3 -> CC1, CC2, CC3, CC4, CC5
    ]

    # Ofertas (capacidade) de cada CD em toneladas
    ofertas_B = [30, 60, 50]

    # Demandas de cada CC em toneladas
    demandas_B = [10, 14, 12, 16, 8]  # Total = 60 toneladas

    prob_B, y_B, x_B = resolver_plc(
        "Combustivel_B",
        custos_instalacao,
        custos_transporte_B,
        ofertas_B,
        demandas_B,
        cds_instalados
    )

    resultado_B = exibir_resultados(
        prob_B, y_B, x_B, "COMBUSTÍVEL B",
        custos_instalacao, custos_transporte_B, ofertas_B, demandas_B
    )

    # -------------------------------------------------------------------------
    # GERAR ARQUIVOS LINDO
    # -------------------------------------------------------------------------
    lindo_A = gerar_formato_lindo(
        custos_instalacao, custos_transporte_A, ofertas_A, demandas_A,
        cds_instalados, "Combustivel_A"
    )
    with open("lindo_combustivel_A.txt", "w") as f:
        f.write(lindo_A)

    lindo_B = gerar_formato_lindo(
        custos_instalacao, custos_transporte_B, ofertas_B, demandas_B,
        cds_instalados, "Combustivel_B"
    )
    with open("lindo_combustivel_B.txt", "w") as f:
        f.write(lindo_B)

    print("\n  Arquivos LINDO gerados: lindo_combustivel_A.txt, lindo_combustivel_B.txt")

    # -------------------------------------------------------------------------
    # RESUMO FINAL
    # -------------------------------------------------------------------------
    print("\n" + "█" * 70)
    print("  RESUMO FINAL")
    print("█" * 70)
    print(f"\n  Custo Ótimo Combustível A: R$ {resultado_A:,.2f}")
    print(f"  Custo Ótimo Combustível B: R$ {resultado_B:,.2f}")
    print(f"  CUSTO TOTAL COMBINADO:     R$ {resultado_A + resultado_B:,.2f}")
    print("\n" + "█" * 70)


if __name__ == "__main__":
    main()

