import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
from matplotlib.patches import FancyArrowPatch
import seaborn as sns
import community as community_louvain  # Certifique-se de ter isso no início
from collections import Counter


# Configuração da página
st.set_page_config(layout="wide", page_title="Análise de Redes")
st.title("🔍 Análise e Visualização de Redes")
st.markdown(
    """
Esta aplicação analisa redes a partir de dados de relacionamento.
Carregue um arquivo CSV com colunas 'source' e 'target' para começar.
"""
)

# Upload do arquivo - versão com opções
st.markdown("### 📁 Selecione a fonte dos dados")
load_option = st.radio(
    "Escolha como deseja carregar os dados:",
    options=[
        "📤 Upload manual (seu arquivo CSV)",
        "🌐 URL do GitHub (raw)",
        "📦 Exemplos pré-configurados"
    ],
    horizontal=True,
    label_visibility="collapsed"
)

df = None

if load_option == "📤 Upload manual (seu arquivo CSV)":
    st.markdown("#### Faça upload do seu arquivo CSV")
    uploaded_file = st.file_uploader(
        "Arraste e solte ou clique para procurar",
        type="csv",
        key="file_uploader",
        help="Formatos suportados: CSV com colunas 'source' e 'target'"
    )
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
elif load_option == "🌐 URL do GitHub (raw)":
    st.markdown("#### Carregar de URL GitHub (raw)")
    col1, col2 = st.columns([3, 1])
    with col1:
        github_url = st.text_input(
            "Cole a URL raw do GitHub",
            value="",
            placeholder="https://raw.githubusercontent.com/.../arquivo.csv",
            help="""Como obter:
            1. Acesse o arquivo no GitHub
            2. Clique em 'Raw'
            3. Copie a URL do navegador
            Exemplo: https://raw.githubusercontent.com/Croncl/projetoU3-analise-de-redes/main/distribution_relationships.csv"""
        )
    with col2:
        st.write("")  # Espaçamento
        st.write("")  # Espaçamento
        if st.button("Carregar", key="load_url_btn"):
            if github_url:
                with st.spinner("Carregando..."):
                    try:
                        if "raw.githubusercontent.com" in github_url:
                            df = pd.read_csv(github_url)
                            st.success("✅ Arquivo carregado com sucesso!")
                        else:
                            st.warning("⚠️ Use uma URL raw do GitHub (raw.githubusercontent.com)")
                    except Exception as e:
                        st.error(f"❌ Erro ao carregar: {str(e)}")
            else:
                st.warning("⚠️ Por favor, insira uma URL válida")

else:  # Opções pré-definidas
    st.markdown("#### Exemplos disponíveis")
    example_option = st.selectbox(
        "Selecione um dataset de exemplo:",
        options=[
            "📊 Distribuições (exemplo simples)",
            "🐦 Tweets Rouanet (reduzido)",
            "🦅 Tweets Rouanet (completo)"
        ],
        index=0
    )
    
    file_urls = {
        "📊 Distribuições (exemplo simples)": "https://raw.githubusercontent.com/Croncl/projetoU3-analise-de-redes/main/distribution_relationships.csv",
        "🐦 Tweets Rouanet (reduzido)": "https://raw.githubusercontent.com/Croncl/projetoU3-analise-de-redes/main/tweets_rouanet_graph_reduzido_filtrado.csv",
        "🦅 Tweets Rouanet (completo)": "https://raw.githubusercontent.com/Croncl/projetoU3-analise-de-redes/main/tweets_rouanet_graph_filtrado.csv"
    }
    
    if st.button("Carregar Exemplo", key="load_example_btn"):
        with st.spinner(f"Carregando {example_option.split('(')[0].strip()}..."):
            try:
                df = pd.read_csv(file_urls[example_option])
                st.success(f"✅ {example_option} carregado com sucesso!")
            except Exception as e:
                st.error(f"❌ Falha no carregamento: {str(e)}")

# Visualização dos dados (para todas as opções)
if df is not None:
    with st.expander("🔍 Visualizar amostra dos dados", expanded=True):
        st.dataframe(df.head(3))
        st.caption(f"📊 Total: {len(df)} registros | 🏷️ Colunas: {', '.join(df.columns)}")
        
    # Processamento do grafo
    df.dropna(subset=["source", "target"], inplace=True)
    G = nx.from_pandas_edgelist(
        df, source="source", target="target", create_using=nx.DiGraph()
    )
    G.remove_edges_from(nx.selfloop_edges(G))

    st.success(
        f"🎉 Grafo carregado: {G.number_of_nodes()} nós e {G.number_of_edges()} arestas"
    )

    # =============================================
    # MÉTRICAS ESTRUTURAIS(Sem filtros)
    # =============================================
    # TEXTOS DE AJUDA (Métricas Estruturais)
    help_densidade = (
        "A densidade é a razão entre o número de arestas existentes e o número máximo possível. "
        "Varia de 0 a 1.\n\n"
        "- 0: grafo extremamente esparso (poucas conexões)\n"
        "- 1: grafo completamente conectado (todos os nós se conectam entre si)\n\n"
        "Útil para entender quão interligada é a rede."
    )
    help_assortatividade = (
        "Mede a tendência de nós se conectarem com outros de grau similar. "
        "Varia de -1 a +1.\n\n"
        "- Valor > 0: nós com grau alto conectam-se a outros com grau alto (ex: redes sociais)\n"
        "- Valor < 0: nós com grau alto conectam-se a nós com grau baixo (ex: redes tecnológicas)\n"
        "- Valor ≈ 0: conexões são aleatórias em relação ao grau dos nós\n\n"
        "Ajuda a entender o padrão de conexões da rede."
    )
    help_clustering = (
        "Mede o grau de agrupamento (formação de triângulos) entre os vizinhos de um nó. "
        "Varia de 0 a 1.\n\n"
        "- Valor próximo de 1: forte tendência de formar grupos (alta coesão local)\n"
        "- Valor próximo de 0: pouca ou nenhuma formação de grupos\n\n"
        "Comum em redes sociais e redes pequenas-mundo."
    )
    help_scc = (
        "Número de subgrafos nos quais **cada nó pode alcançar todos os outros seguindo a direção das arestas**.\n\n"
        "- Relevante em redes dirigidas (como grafos de citações ou hyperlinks).\n"
        "- Valor maior indica uma rede mais fragmentada em termos de alcance direcional.\n"
        "- Um único componente forte sugere alta conectividade mútua.\n\n"
        "Ex: Em um SCC, se A alcança B, então B também alcança A por algum caminho dirigido."
    )

    help_wcc = (
        "Número de subgrafos nos quais os nós estão conectados **se ignorarmos a direção das arestas**.\n\n"
        "- Mede a conectividade geral da estrutura, desconsiderando direcionalidade.\n"
        "- Útil para avaliar fragmentação estrutural bruta da rede.\n"
        "- Um único componente fraco indica que todos os nós estão ligados por algum caminho (mesmo que indirecional).\n\n"
        "Ex: A pode não alcançar B na direção correta, mas ainda faz parte do mesmo grupo fraco."
    )
    help_katz = (
        "A centralidade de Katz mede a influência de um nó, considerando todas as caminhadas possíveis até ele, "
        "mas penalizando caminhos mais longos com um fator de atenuação.\n\n"
        "- Diferente do PageRank, ela atribui importância inclusive a conexões indiretas.\n"
        "- Requer um parâmetro alfa (menor que o inverso do maior autovalor do grafo) para garantir convergência.\n\n"
        "⚠️ Se o grafo for grande, muito esparso ou desconexo, ou se o parâmetro não for adequado, "
        "o cálculo pode falhar por não convergir ou por gerar números instáveis, resultando em 'N/A'."
    )

    help_pagerank = (
        "O PageRank mede a importância de um nó com base na quantidade e qualidade das conexões recebidas.\n\n"
        "- Desenvolvido por Larry Page (Google), ele atribui maior pontuação a nós que são apontados por outros nós importantes.\n"
        "- Útil para identificar nós influentes em redes direcionadas.\n\n"
        "⚠️ Em grafos desconectados ou com estruturas degeneradas (ex: nós isolados), o algoritmo pode ter dificuldade de convergir "
        "e retornar valores consistentes. Nesses casos, o resultado pode ser 'N/A'."
    )
    help_diametro = (
        "O diâmetro é a maior distância geodésica entre quaisquer dois nós da maior componente conexa da rede.\n\n"
        "- Representa o 'pior caso' de distância entre pares de nós.\n"
        "- Quanto menor o diâmetro, mais 'compacta' é a rede.\n\n"
        "⚠️ Se a rede não for conexa (ou seja, houver nós isolados ou múltiplas componentes), "
        "o diâmetro não pode ser calculado diretamente e o resultado será 'N/A'."
    )
    help_caminho_medio = (
        "O comprimento médio do caminho mede a média das distâncias mais curtas entre todos os pares de nós "
        "da maior componente conexa da rede.\n\n"
        "- Reflete quão facilmente a informação se espalha na rede.\n"
        "- Redes pequenas-mundo tendem a ter caminhos médios curtos.\n\n"
        "⚠️ Se o grafo não for conexo (mesmo ignorando direções), não é possível calcular distâncias entre todos os pares, "
        "e o resultado será 'N/A'."
    )
    help_excentricidade = (
        "A excentricidade de um nó é a maior distância entre ele e qualquer outro nó da componente em que está.\n"
        "A excentricidade média considera todos os nós da maior componente conexa.\n\n"
        "- Valores mais baixos indicam maior centralidade estrutural.\n"
        "- Relaciona-se com o quão 'longe' um nó pode estar de qualquer outro na rede.\n\n"
        "⚠️ Se a rede não for conexa (ao menos ignorando a direção das arestas), a excentricidade média "
        "não poderá ser calculada e o valor será 'N/A'."
    )


    def calcular_assortatividade_segura(grafo):
        """
        Calcula o coeficiente de assortatividade de forma segura, evitando erros em grafos esparsos.

        Args:
            grafo: Um grafo NetworkX (Graph ou DiGraph)

        Returns:
            float: Valor da assortatividade ou None se não for possível calcular
        """
        try:
            # Verifica se o grafo tem nós suficientes e variação de graus
            if grafo.number_of_nodes() < 2:
                return None

            degrees = [d for _, d in grafo.degree()]
            if len(set(degrees)) < 2:  # Todos os nós têm o mesmo grau
                return None

            return nx.degree_assortativity_coefficient(grafo)
        except (ZeroDivisionError, nx.NetworkXError):
            return None

    # =============================================
    # MÉTRICAS ESTRUTURAIS E VISUALIZAÇÃO ESTÁTICA
    # =============================================
    with st.expander("📊 Métricas Estruturais da Rede", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Densidade", f"{nx.density(G):.4f}", help=help_densidade)

            assort = calcular_assortatividade_segura(G)
            st.metric(
                "Assortatividade (grau do nó)",
                f"{assort:.4f}" if assort is not None else "N/A",
                help=help_assortatividade,
            )

            st.metric(
                "Coef. Clustering",
                f"{nx.average_clustering(G.to_undirected()):.4f}",
                help=help_clustering,
            )

            try:
                katz = nx.katz_centrality_numpy(G)
                katz_avg = sum(katz.values()) / len(katz)
                st.metric("Centralidade de Katz (média)", f"{katz_avg:.4f}", help=help_katz)
            except Exception as e:
                st.metric("Centralidade de Katz (média)", "N/A", help=help_katz)

            try:
                pagerank = nx.pagerank(G)
                pr_avg = sum(pagerank.values()) / len(pagerank)
                st.metric("PageRank (médio)", f"{pr_avg:.4f}", help=help_pagerank)
            except Exception as e:
                st.metric("PageRank (médio)", "N/A", help=help_pagerank)

        with col2:
            if nx.is_directed(G):
                sccs = list(nx.strongly_connected_components(G))
                scc_count = sum(1 for c in sccs if len(c) >= 2)
                isolated_scc_count = sum(1 for c in sccs if len(c) == 1)
                st.metric("SCCs com ≥2 nós", scc_count, help=help_scc)
                st.metric("Nós isolados (SCCs tamanho 1)", isolated_scc_count, help="Nós que não fazem parte de componentes fortemente conectados com outros")
            else:
                st.metric("SCCs com ≥2 nós", "N/A", help=help_scc)
                st.metric("Nós isolados (SCCs tamanho 1)", "N/A", help="Nós que não fazem parte de componentes fortemente conectados com outros")

            st.metric(
                "Componentes Fracamente Conectados",
                nx.number_weakly_connected_components(G),
                help=help_wcc,
            )

            # Diâmetro e comprimento médio do caminho (se conexa)
            try:
                if nx.is_connected(G.to_undirected()):
                    diameter = nx.diameter(G.to_undirected())
                    avg_path = nx.average_shortest_path_length(G.to_undirected())
                    eccentricity = nx.eccentricity(G.to_undirected())
                    ecc_avg = sum(eccentricity.values()) / len(eccentricity)
                    st.metric("Diâmetro", f"{diameter}", help=help_diametro)
                    st.metric("Caminho Médio", f"{avg_path:.4f}", help=help_caminho_medio)
                    st.metric("Excentricidade Média", f"{ecc_avg:.2f}", help=help_excentricidade)
                else:
                    st.metric("Diâmetro", "N/A", help=help_diametro)
                    st.metric("Caminho Médio", "N/A", help=help_caminho_medio)
                    st.metric("Excentricidade Média", "N/A", help=help_excentricidade)
            except Exception as e:
                st.metric("Diâmetro", "Erro", help=help_diametro)
                st.metric("Caminho Médio", "Erro", help=help_caminho_medio)
                st.metric("Excentricidade Média", "Erro", help=help_excentricidade)
    # =============================================
    # VISUALIZAÇÃO ESTÁTICA
    # =============================================

    with st.expander(
        "📊 Visualização Estática do Grafo (Métricas de Centralidade)", expanded=False
    ):
        st.markdown(
            """
        ## Comparação Visual das Métricas de Centralidade
        
        Cada visualização destaca os nós mais importantes de acordo com diferentes métricas:
        - **Tamanho do nó**: Proporcional à centralidade
        - **Cor**: Escala de azul (menos central) a amarelo (mais central)
        """
        )

        # Selecionar métrica
        metric_option = st.selectbox(
            "Selecione a métrica para visualização:",
            [
                "Degree Centrality",
                "Closeness Centrality",
                "Betweenness Centrality",
                "Eigenvector Centrality",
                "Strongly Connected Component",
                "Weakly Connected Component",
            ],
            key="static_viz_metric",
        )

        # Calcular centralidades com tratamento de erro robusto
        try:
            if metric_option == "Degree Centrality":
                centrality = nx.degree_centrality(G)
                title = "Degree Centrality (Nós mais conectados)"
            elif metric_option == "Closeness Centrality":
                centrality = nx.closeness_centrality(G)
                title = "Closeness Centrality (Nós que alcançam outros mais rapidamente)"
            elif metric_option == "Betweenness Centrality":
                centrality = nx.betweenness_centrality(G)
                title = "Betweenness Centrality (Nós que atuam como pontes)"
            elif metric_option == "Eigenvector Centrality":
                try:
                    centrality = nx.eigenvector_centrality(G, max_iter=1000)
                    title = "Eigenvector Centrality (Nós conectados a outros importantes)"
                except nx.PowerIterationFailedConvergence:
                    st.error(
                        "Não foi possível calcular Eigenvector Centrality (o algoritmo não convergiu)"
                    )
                    centrality = None
            elif metric_option == "Strongly Connected Component":
                sccs = list(nx.strongly_connected_components(G))
                centrality = {node: len(c) for c in sccs for node in c}
                title = "Componentes Fortemente Conectados (tamanho do SCC de cada nó)"
            elif metric_option == "Weakly Connected Component":
                wccs = list(nx.weakly_connected_components(G))
                centrality = {node: len(c) for c in wccs for node in c}
                title = "Componentes Fracamente Conectados (tamanho do WCC de cada nó)"
        except Exception as e:
            st.error(f"Erro ao calcular {metric_option}: {str(e)}")
            centrality = None

        layout_option = st.selectbox(
            "Escolha o layout da visualização",
            ["spring", "circular", "random"],
            index=0,
            help="Escolha o algoritmo de layout para distribuir os nós na visualização."
        )


        if centrality and len(centrality) > 0:
            # Preparar valores
            cent_values = np.array(list(centrality.values()))
            nodes_list = list(centrality.keys())

            if np.ptp(cent_values) == 0:
                st.warning(
                    f"Todos os nós têm o mesmo valor de {metric_option.split()[0]} Centrality"
                )
                sizes = np.full_like(cent_values, 300)
                colors = np.zeros_like(cent_values)
            else:
                sizes = 10 + 150 * (cent_values - cent_values.min()) / (
                    np.ptp(cent_values) + 1e-10
                )
                colors = (cent_values - cent_values.min()) / (np.ptp(cent_values) + 1e-10)

            # Layout e figura
            k_value = 1.5 / np.sqrt(len(G))  # Valor maior → nós mais afastados
            if layout_option == "spring":
                k_value = 1.5 / np.sqrt(len(G)) if len(G) > 0 else 0.1
                pos = nx.spring_layout(G, seed=42, k=k_value, iterations=100)
            elif layout_option == "circular":
                pos = nx.circular_layout(G)
            elif layout_option == "random":
                pos = nx.random_layout(G, seed=42)


            plt.style.use("dark_background")  # Define fundo escuro

            fig = plt.figure(figsize=(12, 8), facecolor="#0D1117")
            gs = fig.add_gridspec(1, 2, width_ratios=[20, 1], wspace=0.05)
            ax = fig.add_subplot(gs[0])
            cax = fig.add_subplot(gs[1])

            ax.set_facecolor("#0D1117")
            cax.set_facecolor("#0D1117")

            nodes_draw = nx.draw_networkx_nodes(
                G,
                pos,
                node_size=sizes,
                node_color=colors,
                cmap=plt.cm.plasma,# mapa de cores
                alpha=0.9, # transparência dos nós
                ax=ax,# ax do gráfico principal
            )

            for u, v in G.edges():
                if u == v:
                    continue  # opcional: pula auto-laços
                rad = 0.2  # quanto mais alto, mais curvado
                arrow = FancyArrowPatch(
                    posA=pos[u],
                    posB=pos[v],
                    connectionstyle=f"arc3,rad={rad}",
                    arrowstyle='-',
                    color="#BBBBBB",
                    linewidth=0.4,
                    alpha=0.5
                )
                ax.add_patch(arrow)


            # Rótulo dos top 10
            if np.ptp(cent_values) > 0:
                top_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]
                for node, _ in top_nodes:
                    x, y = pos[node]
                    ax.text(
                        x, y, str(node),
                        fontsize=8,
                        ha='center',
                        va='center',
                        bbox=dict(facecolor='black', alpha=0.7, edgecolor='none')
                    )

            # Título e eixos
            ax.set_title(title, fontsize=14, color="white")
            ax.axis("off")

            # Barra de cor separada
            norm = plt.Normalize(vmin=cent_values.min(), vmax=cent_values.max())
            cbar = plt.colorbar(
                plt.cm.ScalarMappable(norm=norm, cmap=plt.cm.plasma),
                cax=cax
            )
            cbar.set_label("Valor de Centralidade", color="white")
            cbar.ax.yaxis.set_tick_params(color='white')
            plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')

            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

            # Interpretação e tabela
            st.markdown(
                f"""
            ### Interpretação:
            - **Nós maiores e mais amarelos**: Possuem maior {metric_option.split()[0]} centrality  
            - **Nós menores e mais escuros**: Possuem menor {metric_option.split()[0]} centrality  
            - **Top 10 nós** estão rotulados com seus nomes
            """
            )

            st.markdown("### 📊 Tabela de Centralidades")
            df_centrality = pd.DataFrame.from_dict(
                centrality, orient="index", columns=["Centralidade"]
            )
            st.dataframe(df_centrality.sort_values("Centralidade", ascending=False))
        else:
            st.warning(
                "Não foi possível gerar a visualização para esta métrica ou todos os nós têm o mesmo valor."
            )

    # =============================================
    # DISTRIBUIÇÃO DE GRAU
    # =============================================

    with st.expander("📈 Distribuição de Grau", expanded=False):
        plt.style.use("dark_background")  # Define fundo escuro

        fig, ax = plt.subplots(1, 2, figsize=(12, 4), facecolor="#121222")

        # Grau de entrada
        sns.histplot(
            list(dict(G.in_degree()).values()),
            bins=30,
            ax=ax[0],
            color="skyblue",
            edgecolor="#111111",
        )
        ax[0].set_title("Distribuição do Grau de Entrada", color="white")
        ax[0].set_xlabel("Grau de entrada", color="white")
        ax[0].set_ylabel("Frequência", color="white")
        ax[0].set_yscale("log")
        ax[0].tick_params(colors="white")

        # Grau de saída
        sns.histplot(
            list(dict(G.out_degree()).values()),
            bins=30,
            ax=ax[1],
            color="salmon",
            edgecolor="black",
        )
        ax[1].set_title("Distribuição do Grau de Saída", color="white")
        ax[1].set_xlabel("Grau de saída", color="white")
        ax[1].set_ylabel("Frequência", color="white")
        ax[1].set_yscale("log")
        ax[1].tick_params(colors="white")

        st.pyplot(fig)

        st.markdown(
            """
            - A distribuição de grau mostra como os nós estão conectados na rede.
            - Redes reais muitas vezes têm poucos nós com alto grau e muitos com baixo grau.
            - A escala logarítmica evidencia essa estrutura com cauda longa.
            """
        )

    # =============================================
    # ANÁLISE DE CENTRALIDADE 
    # =============================================

    with st.expander("⭐ Análise de Centralidade", expanded=False):
        st.markdown(
            """
        Compare as diferentes medidas de centralidade para identificar os nós mais importantes:
        - **Degree**: Nós mais conectados
        - **Closeness**: Nós que podem alcançar outros mais rapidamente
        - **Betweenness**: Nós que atuam como pontes
        - **Eigenvector**: Nós conectados a outros nós importantes
        """
        )

        col1, col2 = st.columns(2)
        with col1:
            metric = st.selectbox(
                "Métrica de Centralidade",
                ["Degree", "Closeness", "Betweenness", "Eigenvector"],
                key="centrality_metric"
            )
        with col2:
            k = st.slider("Número de nós para mostrar", 1, 100, 10, key="top_k_nodes")

        # Cálculo de centralidade com tratamento de erros
        try:
            if metric == "Degree":
                centrality = nx.degree_centrality(G)
            elif metric == "Closeness":
                centrality = nx.closeness_centrality(G)
            elif metric == "Betweenness":
                centrality = nx.betweenness_centrality(G)
            elif metric == "Eigenvector":
                centrality = nx.eigenvector_centrality(G, max_iter=1000)
        except Exception as e:
            st.error(f"Erro ao calcular {metric} centrality: {str(e)}")
            centrality = None

        if centrality:
            # Mostra tabela com top k nós
            top_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:k]
            st.dataframe(pd.DataFrame(top_nodes, columns=["Nó", "Centralidade"]))
            
            # Visualização estática
            st.markdown("### 📌 Visualização dos Nós Mais Centrais")
            H = G.subgraph([n for n, _ in top_nodes])
            
            # Configuração do plot
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.set_facecolor('#0D1117')
            
            # Layout e cores
            pos = nx.spring_layout(H, seed=42)
            node_values = [centrality[n] for n in H.nodes()]
            node_sizes = [100 + 500 * (val - min(node_values))/(max(node_values) - min(node_values)) for val in node_values]
            
            # Desenho do grafo
            nodes = nx.draw_networkx_nodes(
                H, pos,
                node_color=node_values,
                node_size=node_sizes,
                cmap=plt.cm.viridis,
                alpha=0.9,
                ax=ax
            )
            
            nx.draw_networkx_edges(
                H, pos,
                edge_color='#CCCCCC',
                width=0.4,
                alpha=0.5,
                ax=ax
            )
            
            # Adicionar labels para os top 5 nós
            for node, (x, y) in pos.items():
                ax.text(x, y+0.02, node, 
                    ha='center', va='bottom', 
                    fontsize=8, color='white')
            
            # Colorbar corretamente integrada
            sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis, 
                                    norm=plt.Normalize(vmin=min(node_values), 
                                                    vmax=max(node_values)))
            sm.set_array([])
            cbar = fig.colorbar(sm, ax=ax, shrink=0.5)
            cbar.set_label(f'Centralidade ({metric})', color='white')
            cbar.ax.yaxis.set_tick_params(color='white')
            
            plt.title(f"Top {k} Nós por {metric} Centrality", color='white')
            st.pyplot(fig)
            plt.close()
    # =============================================
    # DETECÇÃO DE COMUNIDADES (VERSÃO CORRIGIDA)
    # =============================================

    with st.expander("🧩 Detecção de Comunidades", expanded=False):
        st.markdown(
            """
            ## Detecção de Comunidades (Algoritmo Louvain)
            
            Grupos de nós mais densamente conectados entre si do que com o resto da rede.
            """
        )

        # Converte para grafo não direcionado
        G_undirected = G.to_undirected() if nx.is_directed(G) else G

        # Detecta comunidades
        partition = community_louvain.best_partition(G_undirected)
        community_sizes = Counter(partition.values())
        
        # Filtra comunidades pequenas (opcional)
        min_community_size = st.slider("Tamanho mínimo da comunidade", 3, 10, 10)
        communities_to_keep = {comm for comm, size in community_sizes.items() if size >= min_community_size}
        
        # Filtra nós e arestas
        nodes_to_keep = [node for node in G_undirected.nodes() if partition[node] in communities_to_keep]
        G_filtered = G_undirected.subgraph(nodes_to_keep)
        
        # Configurações do plot
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_facecolor('#121212')
        
                # Layout
        # Calcula um k adaptativo com base no número de nós (quanto mais nós, mais espaçado)
        k_val = 1.2 / np.sqrt(G_filtered.number_of_nodes())  # experimente valores como 0.3, 0.5, 0.8 também

        pos = nx.spring_layout(G_filtered, seed=42, k=k_val)
        
        # Usa seaborn para gerar cores das comunidades
        community_list = sorted(communities_to_keep)
        palette = sns.color_palette("hls", len(community_list))
        community_colors = {comm: mcolors.to_hex(c) for comm, c in zip(community_list, palette)}
        node_colors = [community_colors[partition[node]] for node in G_filtered.nodes()]

        # Tamanho dos nós proporcional ao grau
        degrees = dict(G_filtered.degree())
        node_sizes = [50 + degrees[node]*5 for node in G_filtered.nodes()]
        
        # Desenha o grafo
        nx.draw_networkx_nodes(
            G_filtered, pos,
            node_color=node_colors,
            node_size=node_sizes,
            alpha=0.9,
            ax=ax
        )
        
        nx.draw_networkx_edges(
            G_filtered, pos,
            edge_color='#CCCCCC',
            width=0.3,
            alpha=0.3,
            ax=ax
        )
        
        # Adiciona labels para os nós mais centrais
        top_degree_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:20]
        for node, _ in top_degree_nodes:
            x, y = pos[node]
            ax.text(x, y, str(node), 
                fontsize=8, 
                ha='center', 
                va='center',
                bbox=dict(facecolor='black', alpha=0.7, edgecolor='none'))
        
        # Legenda de comunidades
        legend_elements = [
            plt.Line2D([0], [0], 
                    marker='o', 
                    color='w', 
                    label=f'Comunidade {comm} ({size} nós)',
                    markerfacecolor=community_colors[comm], 
                    markersize=10)
            for comm, size in sorted(community_sizes.items(), key=lambda x: x[1], reverse=True)
            if comm in communities_to_keep
        ]
        
        ax.legend(
            handles=legend_elements,
            title="Comunidades Detectadas",
            loc='upper left',
            bbox_to_anchor=(1.02, 1),  # um pouco à direita e alinhado ao topo
            borderaxespad=0.0, # espaçamento entre a legenda e o gráfico
            frameon=True, # ativa borda
            framealpha=0.8, # transparência da borda
            facecolor='#222222',
            edgecolor='white',
            fontsize=8
        )
        
        plt.title(
            f"Detecção de Comunidades (Louvain) - {len(communities_to_keep)} comunidades com ≥{min_community_size} nós",
            color='white'
        )
        plt.tight_layout()# evita corte na figura e na legenda
        st.pyplot(fig)
        plt.close()
        
        # Estatísticas
        st.markdown("### 📊 Estatísticas das Comunidades")
        st.write(f"Total de comunidades detectadas: {len(community_sizes)}")
        st.write(f"Comunidades com ≥{min_community_size} nós: {len(communities_to_keep)}")
        
        # Tabela de comunidades
        comm_table = pd.DataFrame(
            [(comm, size) for comm, size in community_sizes.items() if size >= min_community_size],
            columns=["Comunidade", "Tamanho"]
        ).sort_values("Tamanho", ascending=False)
        
        st.dataframe(comm_table)
