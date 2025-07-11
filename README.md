# 🔍 Análise e Visualização de Redes
Streamlit: https://kutdwqpuhtjzuns8ocqe5r.streamlit.app/  
GitHub Pages: https://croncl.github.io/projetoU3-analise-de-redes-network/

Este projeto é uma aplicação web interativa desenvolvida com **Streamlit** para análise e visualização de redes direcionadas a partir de dados tabulares, oferecendo insights sobre a estrutura e dinâmica de redes complexas.

# 🌟 Recursos Avançados de Análise de Redes

## 🔍 Análise Estrutural Completa
### 📐 Métricas Fundamentais
- **Densidade da rede**: Medida de conectividade global (0-1)
- **Assortatividade**: Tendência de conexão entre nós similares (-1 a 1)
- **Coeficiente de clustering**: Probabilidade de formação de triângulos

### 🧩 Componentes da Rede
- **SCC (Componentes Fortemente Conectados)**: Sub-redes onde todos os nós são mutuamente alcançáveis
- **WCC (Componentes Fracamente Conectados)**: Sub-redes considerando conexões não-direcionadas
- **Diâmetro**: Maior distância entre quaisquer dois nós
- **Caminho médio**: Distância média entre todos os pares de nós

## 🖼️ Visualização Interativa Avançada
### 🎨 Personalização Gráfica
- **Layouts múltiplos**: 
  - Spring (força-direcionada): Organização baseada em forças de atração/repulsão
  - Circular (organização radial): Nós dispostos em círculo equidistantes
  - Random (aleatório): Posicionamento randômico para análise inicial
- **Sistema de cores**: 
  - Gradiente azul-amarelo por centralidade
  - Destaque para comunidades

### 📊 Ferramentas de Análise Visual
- **Ranking automático**: Top 10 nós por métrica selecionada
- **Distribuição de grau**: 
  - Visualização logarítmica
  - Identificação de hubs e outliers

## 🕵️ Detecção de Comunidades
### 🔬 Algoritmo Louvain
- Detecção hierárquica de grupos
- Ajuste de parâmetros:
  - Tamanho mínimo de comunidade
  - Resolução de modularidade

### 📈 Estatísticas de Grupos
- Quantidade de comunidades
- Distribuição de tamanhos
- Densidade intra-comunidade

## 📌 Análise de Centralidade Comparada
### 🎯 Métricas Principais
| Métrica | Descrição | Aplicação |
|---------|-----------|-----------|
| **Degree** | Número de conexões diretas | Identificação de hubs |
| **Closeness** | Distância média até outros nós | Nós estratégicos para difusão |
| **Betweenness** | Mediação em caminhos curtos | Pontes entre comunidades |
| **Eigenvector** | Influência considerando conexões importantes | Líderes naturais |

### 🔗 Componentes Estruturais
- **Análise WCC**: Avaliação de conectividade básica
- **Análise SCC**: Identificação de sub-redes interdependentes

Esta versão:
1. Organiza hierarquicamente as informações
2. Adiciona descrições técnicas precisas
3. Inclui tabela comparativa das métricas
4. Mantém linguagem acessível com termos técnicos explicados
5. Melhora a visualização com formatação clara
6. Destaca aplicações práticas de cada recurso

## 🛠 Tecnologias Utilizadas
 - Framework: Streamlit
 - Análise de Redes: NetworkX
 - Visualização: Matplotlib, Seaborn
 - Processamento: Pandas, NumPy

## 🚀 Como Usar

### Pré-requisitos
- Python 3.8+
- Pip instalado

### Instalação Rápida
```bash
git clone https://github.com/Croncl/projetoU3-analise-de-redes.git
cd projetoU3-analise-de-redes
pip install -r requirements.txt
streamlit run app.py
```

### Opções de Dados
1. **Upload manual** de seu arquivo CSV
2. **Carregar via URL** do GitHub (formato raw)
3. **Exemplos pré-configurados**:
   - Dataset de distribuições (exemplo simples)
   - Tweets sobre Rouanet (versão reduzida)
   - Tweets sobre Rouanet (dataset completo)

## 📋 Formato dos Dados
```csv
source,target,relationship
A,B,type1, 
B,C,type2
C,A,type3
```

## 📌 Exemplo de Uso
1. Selecione um dataset de exemplo ou carregue seu arquivo
2. Explore as métricas estruturais da rede
3. Visualize o grafo com diferentes layouts
4. Identifique comunidades e nós centrais
5. Exporte os resultados para análise posterior

## 🌐 Demonstração Online
Acesse a versão hospedada:  
[![Streamlit App]: https://kutdwqpuhtjzuns8ocqe5r.streamlit.app/

## 📚 Glossário
- **SCC**: Componente Fortemente Conectado
- **WCC**: Componente Fracamente Conectado
- **Eccentricity**: Máxima distância de um nó para qualquer outro
