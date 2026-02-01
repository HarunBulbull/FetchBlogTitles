import requests
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import Error
import time
import xml.etree.ElementTree as ET

SITEMAP_URLS = [
    "https://www.domain.com/sitemap.xml", # sitemap url
    # ... sitemap urls
]

KEYWORDS = [
    "keyword1",
    "keyword2" 
    # ... keywords
]

IGNORE_LIST = [
    "ignore1",
    "ignore2",
    # ... ignore list
]

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'blogTitles'
}
# ----------------------------------------

def init_db():
    try:
        conn_params = DB_CONFIG.copy()
        db_name = conn_params.pop('database')
        
        temp_conn = mysql.connector.connect(**conn_params)
        temp_cursor = temp_conn.cursor()
        temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        temp_conn.close()

        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS headings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title TEXT,
                    url VARCHAR(500),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_title (title(255))
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            ''')
            conn.commit()
            print(f"Veritabanı '{db_name}' ve 'headings' tablosu hazır.")
            return conn
    except Error as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        return None

def contains_domain(text):
    domains = [".com", ".net", ".org", ".info", ".biz", ".com.tr", ".gen.tr", ".web.tr", ".gov", ".edu"]
    text_lower = text.lower()
    for d in domains:
        if d in text_lower:
            return True
    return False

def get_urls_from_sitemap(sitemap_url):
    print(f"--> Sitemap taranıyor: {sitemap_url}")
    urls = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(sitemap_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        ns = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
        
        sitemaps = root.findall('.//ns:sitemap', ns) if ns else root.findall('.//sitemap')
        if sitemaps:
            for sm in sitemaps:
                loc = sm.find('ns:loc', ns) if ns else sm.find('loc')
                if loc is not None:
                    urls.extend(get_urls_from_sitemap(loc.text))
        else:
            url_elements = root.findall('.//ns:url', ns) if ns else root.findall('.//url')
            for u in url_elements:
                loc = u.find('ns:loc', ns) if ns else u.find('loc')
                if loc is not None:
                    urls.append(loc.text)
                    
    except Exception as e:
        print(f"!!! Sitemap hatası ({sitemap_url}): {e}")
        
    return list(set(urls))

def process_page(url, keywords, ignore_list, conn):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        h_tags = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        cursor = conn.cursor()
        saved_count = 0
        
        for tag in h_tags:
            title_text = tag.get_text(strip=True)
            
            if not title_text:
                continue
                
            has_keyword = any(kw.lower() in title_text.lower() for kw in keywords)
            if not has_keyword:
                continue
                
            if contains_domain(title_text):
                continue

            valid_ignores = [ign for ign in ignore_list if ign.strip()]
            has_ignored_word = any(ign.lower() in title_text.lower() for ign in valid_ignores)
            if has_ignored_word:
                continue
            
            try:
                sql = "INSERT IGNORE INTO headings (title, url) VALUES (%s, %s)"
                cursor.execute(sql, (title_text, url))
                if cursor.rowcount > 0:
                    saved_count += 1
            except Exception as db_err:
                pass
        
        conn.commit()
        if saved_count > 0:
            print(f"✅ BAŞARILI: {url} | {saved_count} yeni başlık eklendi.")
        else:
            print(f"❌ ATLANDI/TEKRAR: {url}")
            
    except Exception as e:
        print(f"!!! Sayfa hatası ({url}): {e}")

def main():
    conn = init_db()
    if not conn:
        print("Veritabanı bağlantısı olmadan işleme devam edilemez.")
        return

    print("Sitemap'ten URL'ler toplanıyor, lütfen bekleyin...")
    all_urls = []
    for sitemap in SITEMAP_URLS:
        try:
            urls = get_urls_from_sitemap(sitemap)
            all_urls.extend(urls)
        except:
            continue
    
    all_urls = list(set(all_urls))
    total = len(all_urls)
    print(f"\n--- Tarama Başlıyor: Toplam {total} URL işlenecek ---\n")
    
    for i, url in enumerate(all_urls, 1):
        print(f"[{i}/{total}] İşleniyor...", end=" ", flush=True)
        process_page(url, KEYWORDS, IGNORE_LIST, conn)
        time.sleep(0.1)
        
    conn.close()
    print("\n--- BÜTÜN İŞLEMLER TAMAMLANDI ---")

if __name__ == "__main__":
    main()
