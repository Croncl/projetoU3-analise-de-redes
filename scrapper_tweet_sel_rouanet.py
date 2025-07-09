from datetime import datetime, timedelta
import time  # Adicionar no início do arquivo
import csv
import os
import pandas as pd
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

SEARCH_TERMS = ["rouanet"]
SINCE = "2017-01-20"
UNTIL = "2022-10-30"

MAX_TWEETS = 10000
MAX_RETRIES = 6
RETRY_INTERVAL = 120
SCROLL_PAUSE = 6
WINDOW_DAYS = 23

CSV_PATH = f"tweets_{SEARCH_TERMS[0]}_graph.csv"

def extrair_usuario_da_url(href):
    """Extrai @usuario de uma URL, removendo parâmetros como ?src=..."""
    return "@" + href.split("/")[-1].split("?")[0]

def wait_for_tweets(driver):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="tweet"]'))
            )
            return True
        except TimeoutException:
            if attempt < MAX_RETRIES:
                print(f"⌛ Tentativa {attempt}/{MAX_RETRIES} - Aguardando...")
                time.sleep(RETRY_INTERVAL)
            else:
                print("⚠️ Não foi possível carregar tweets")
                return False


def scroll_to_load_all(driver, max_tweets):
    previous_count = 0
    no_new_scrolls = 0
    max_no_new_scrolls = 6
    scroll_attempts = 0
    max_scroll_attempts = 50  # Limite máximo de rolagens

    while no_new_scrolls < max_no_new_scrolls and scroll_attempts < max_scroll_attempts:
        # Espera explícita pelo carregamento
        try:
            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')) > previous_count or no_new_scrolls >= 1
            )
        except TimeoutException:
            print("⌛ Timeout durante espera por novos tweets")

        tweets = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
        current_count = len(tweets)

        if current_count >= max_tweets:
            print(f"✅ Limite de {max_tweets} tweets")
            break

        if current_count == previous_count:
            no_new_scrolls += 1
            print(f"🔁 Nenhum novo tweet após rolagem {scroll_attempts} (tentativas restantes: {max_no_new_scrolls - no_new_scrolls})")
        else:
            no_new_scrolls = 0
            delta = max(0, current_count - previous_count)
            print(f"⬇️ {delta} novos tweets carregados")


        previous_count = current_count
        
        # Rolagem suave com pausa aleatória
        driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
        
        # Pausa dinâmica baseada no carregamento
        wait_time = random.uniform(6, 12)  # Pausa maior entre rolagens
        print(f"⏳ Aguardando {wait_time:.1f} segundos para carregamento...")
        time.sleep(wait_time)
        
        # Verificação adicional de erros
        try:   # Verificação adicional de erros do Twitter
            error_msg = driver.find_element(By.XPATH, '//*[contains(text(), "Something went wrong")]')
            if error_msg:
                print("⚠️ Erro detectado - aguardando 20 segundos")
                time.sleep(20)
                driver.refresh()
                time.sleep(10)
                no_new_scrolls = 0  # Reseta o contador
        except NoSuchElementException:
            pass

        # Verificação de rate limit
        if "rate limit" in driver.page_source.lower():
            print("⏳ Rate limit detectado - aguardando 5 minutos...")
            time.sleep(300)
            driver.refresh()
            time.sleep(10)
            no_new_scrolls = 0  # Reseta o contador
        scroll_attempts += 1

    print(f"🛑 Finalizado após {scroll_attempts} rolagens. Total de tweets: {previous_count}")

def should_skip_user(username):
    """Filtra apenas usuários que são exatamente o termo de busca"""
    username_lower = username.lower()
    return username_lower == f"@{SEARCH_TERMS[0].lower()}"

def fetch_tweets_from_search(driver, existing_tweets):
    tweets_elements = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
    results = []
    
    for tweet in tweets_elements:
        try:
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", tweet)
            time.sleep(random.uniform(5, 10))
            
            user_section = WebDriverWait(tweet, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="User-Name"]'))
            )
            author_link = user_section.find_element(By.XPATH, './/a[contains(@href, "/") and not(contains(@href, "/status/"))]')
            author_handle = extrair_usuario_da_url(author_link.get_attribute("href"))
            
            if should_skip_user(author_handle):
                continue

            tweet_date = tweet.find_element(By.TAG_NAME, "time").get_attribute("datetime") if tweet.find_elements(By.TAG_NAME, "time") else ""
            content = tweet.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetText"]').text if tweet.find_elements(By.CSS_SELECTOR, 'div[data-testid="tweetText"]') else ""

            reply_to = set()
            try:
                reply_section = tweet.find_element(By.CSS_SELECTOR, 'div[data-testid="reply"]')
                reply_users = reply_section.find_elements(By.XPATH, './/a[contains(@href, "/") and not(contains(@href, "/status/"))]')
                
                for user in reply_users:
                    mention = extrair_usuario_da_url(user.get_attribute("href"))
                    if mention != author_handle and not should_skip_user(mention):
                        reply_to.add(mention)

                if "and others" in reply_section.text:
                    try:
                        driver.execute_script("arguments[0].click();", reply_section)
                        time.sleep(3)
                        
                        modal_users = driver.find_elements(By.XPATH, '//div[@role="dialog"]//a[contains(@href, "/")]')
                        for user in modal_users:
                            mention = extrair_usuario_da_url(user.get_attribute("href"))
                            if mention not in reply_to and not should_skip_user(mention):
                                reply_to.add(mention)
                    except:
                        pass

            except NoSuchElementException:
                pass

            mentions = set()
            for link in tweet.find_elements(By.XPATH, './/a[contains(@href, "/") and not(contains(@href, "/status/"))]'):
                mention = extrair_usuario_da_url(link.get_attribute("href"))
                if mention != author_handle and not should_skip_user(mention):
                    mentions.add(mention)
            
            mentions.update(reply_to)

            if mentions:
                for mention in mentions:
                    results.append((author_handle, mention, content, tweet_date))
            else:
                results.append((author_handle, "", content, tweet_date))

        except Exception as e:
            if "NoSuchElementException" not in str(e):
                print(f"⚠️ Erro inesperado: {str(e)[:100]}")
            continue
    # verificar quandos foram filtrados:
    print(f"📊 Tweets encontrados: {len(tweets_elements)}, Após filtro: {len(results)}")
    return results

def salvar_tweets(tweets, existing_tweets, periodo):
    """
    Salva tweets no arquivo CSV, evitando duplicatas.
    
    Args:
        tweets: Lista de tweets a serem salvos (cada tweet é uma tupla)
        existing_tweets: Conjunto de tweets já existentes
        periodo: String com o período sendo processado (para logs)
    
    Returns:
        int: Número de tweets novos salvos (0 se nenhum novo)
    """
    try:
        # Força a criação do CSV com cabeçalho se ainda não existir
        if not os.path.exists(CSV_PATH):
            with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["source", "target", "tweet_text", "tweet_date"])
            print(f"🆕 Arquivo CSV criado: {CSV_PATH}")

        # Filtra tweets que ainda não existem
        new_tweets = [t for t in tweets if t not in existing_tweets]
        count = len(new_tweets)
        
        if count > 0:
            # Salva os novos tweets
            with open(CSV_PATH, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(new_tweets)  # Mais eficiente que writerow em loop
            
            print(f"✅ [{periodo}] {count} tweets novos salvos")
            # Atualiza o conjunto de tweets existentes
            existing_tweets.update(new_tweets)
        else:
            print(f"ℹ️ [{periodo}] Nenhum tweet novo para salvar")
        
        return count  # Sempre retorna um inteiro
    
    except Exception as e:
        print(f"❌ Erro ao salvar tweets: {e}")
        return 0  # Retorna 0 em caso de erro


def daterange(start_date, end_date, step_days):
    current = start_date
    while current < end_date:
        yield current, min(current + timedelta(days=step_days), end_date)
        current += timedelta(days=step_days + 1)


def main():
    # Configurações do Chrome (mantidas)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--window-size=1200,900")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = webdriver.Chrome(options=chrome_options)

    # 🔧 Garante que o CSV será criado antes de qualquer leitura
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["source", "target", "tweet_text", "tweet_date"])
        print(f"🆕 Arquivo CSV inicial criado: {CSV_PATH}")

    # Tratamento do CSV existente
    existing_tweets = set()
    try:
        df_existing = pd.read_csv(CSV_PATH)
        required_columns = {'source', 'target', 'tweet_text', 'tweet_date'}
        
        if not required_columns.issubset(df_existing.columns):
            print("⚠️ Arquivo CSV corrompido - recriando")
            os.remove(CSV_PATH)
            with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["source", "target", "tweet_text", "tweet_date"])
        else:
            existing_tweets = {
                (str(row["source"]).lower(),
                 str(row["target"]).lower() if pd.notna(row["target"]) else "",
                 str(row["tweet_text"]),
                 str(row["tweet_date"]))
                for _, row in df_existing.iterrows()
            }
            print(f"📂 {len(existing_tweets)} tweets carregados")

    except Exception as e:
        print(f"⚠️ Erro ao ler CSV: {e} - Recriando")
        os.remove(CSV_PATH)
        with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["source", "target", "tweet_text", "tweet_date"])

    # Loop de coleta
    try:
        count = 0
        for start, end in daterange(datetime.strptime(SINCE, "%Y-%m-%d"), 
                                    datetime.strptime(UNTIL, "%Y-%m-%d"), 
                                    WINDOW_DAYS):
            if count >= MAX_TWEETS:
                break

            print(f"\n📅 Período: {start.date()} a {end.date()}")
            
            query = " OR ".join([f'"{term}"' if " " in term else term for term in SEARCH_TERMS])
            url = f"https://x.com/search?q={query}%20since%3A{start.date()}%20until%3A{end.date()}&src=typed_query&f=live"
            driver.get(url)
            time.sleep(random.uniform(10, 30))

            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="tweet"]'))
                )
            except TimeoutException:
                print("⚠️ Timeout ao abrir busca — tentando recarregar")
                driver.refresh()
                time.sleep(random.uniform(16, 40))
                try:
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="tweet"]'))
                    )
                except TimeoutException:
                    print("❌ Ainda sem sucesso — pulando período")
                    continue

            if not wait_for_tweets(driver):
                continue

            scroll_to_load_all(driver, MAX_TWEETS - count)
            tweets = fetch_tweets_from_search(driver, existing_tweets)
            count += salvar_tweets(tweets, existing_tweets, f"{start.date()} a {end.date()}")

            intervalo = random.uniform(10, 40)
            print(f"⏸️ Aguardando {intervalo:.1f} segundos antes da próxima janela...")
            time.sleep(intervalo)

    finally:
        driver.quit()
        print(f"\n✅ Total de tweets salvos: {count}")


if __name__ == "__main__":
    import time
    main()