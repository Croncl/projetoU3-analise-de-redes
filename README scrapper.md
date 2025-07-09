# **README - Configuração do Ambiente para Automação Web com Selenium**  

Este guia explica como configurar um ambiente virtual (`venv`) para executar o script de automação web que utiliza **Selenium** e **Pandas**.  

---

## **Pré-requisitos**  
- **Python 3.6+** instalado ([Download aqui](https://www.python.org/downloads/)).  
- **Gerenciador de pacotes `pip`** (vem com o Python por padrão).  
- **Navegador** (Chrome, Firefox ou Edge) e seu respectivo **WebDriver**.  

---

## **Passo a Passo para Configuração**  

### **1. Criar e Ativar o Ambiente Virtual**  
Execute no terminal:  

```bash
# Criar ambiente virtual (dentro da pasta do projeto)
python -m venv venv

# Ativar o ambiente:
# Windows (CMD/PowerShell):
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate
```
*(O prompt deve mostrar `(venv)` no início.)*  

---

### **2. Instalar Dependências**  
Crie um arquivo `requirements.txt` na raiz do projeto com:  

```txt
selenium>=4.0.0
pandas>=1.0.0
```  

Depois instale as dependências:  

```bash
pip install -r requirements.txt
```

---

### **3. Configurar o WebDriver**  
- Baixe o driver compatível com seu navegador:  
  - **Chrome**: [Chromedriver](https://sites.google.com/chromium.org/driver/)  
  - **Firefox**: [Geckodriver](https://github.com/mozilla/geckodriver)  
  - **Edge**: [Edgedriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)  

- Coloque o executável:  
  - Na pasta do projeto **OU**  
  - Em um diretório no `PATH` do sistema.  

---

### **4. Executar o Script**  
Com o ambiente ativado, rode:  

```bash
python seu_script.py
```

---

### **5. Desativar o Ambiente Virtual**  
Quando terminar:  

```bash
deactivate
```

---

## **Solução de Problemas**  
- **Erro "WebDriver not found"**: Verifique se o driver está no caminho correto.  
- **Dependências desatualizadas**: Atualize com `pip install --upgrade selenium pandas`.  
- **Problemas no `venv`**: Recrie o ambiente (`rm -rf venv` no Linux/macOS ou `rmdir /s venv` no Windows).  

---

## **Estrutura do Projeto (Exemplo)**  
```
meu_projeto/  
│  
├── venv/                  # Ambiente virtual (gerado)  
├── seu_script.py          # Script principal  
├── requirements.txt       # Dependências  
└── chromedriver.exe       # WebDriver (se usar Chrome)  
```

---

**Contribuições**:  
Sugestões ou problemas? Abra uma **issue** ou envie um **pull request**.  

--- 

🔹 **Nota**: Mantenha o `venv` fora do controle de versão (adicione `venv/` ao `.gitignore`).  

📌 **Pronto!** Seu ambiente está configurado para automação web.
