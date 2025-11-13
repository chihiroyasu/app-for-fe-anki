import requests
from bs4 import BeautifulSoup
import json
import time

# --- 設定情報 ---
BASE_URL = 'https://www.fe-siken.com/keyword'
FIELD_HIERARCHY = [
    5, 5, 5, 2, 5, 1, 2, 2, 5, 5, 5, 6, 4, 11, 5, 2, 4, 3, 4, 2, 5, 3, 5
]
OUTPUT_FILE = 'fe_keywords_data.json'
# --- 設定情報 終 ---

def get_category_info(soup):
    """
    HTMLから大分類名と中分類名を取得する。
    """
    # <h2>タグから中分類名（例: "離散数学"）を取得
    category_title_tag = soup.find('div', class_='main keyword').find('h2')
    if category_title_tag:
        # 例: "離散数学 - 34語（シラバス9.1）" から "離散数学" を抽出
        category_name = category_title_tag.text.split('-')[0].strip()
    else:
        category_name = '不明な分野'

    # 大分類名（例: "1 基礎理論"）を取得 (クラス名に注意)
    # 最初の <a class="category_badge" href="/keyword/1/"> を探す
    first_badge_tag = soup.find('a', class_='category_badge')
    if first_badge_tag:
        major_category = first_badge_tag.text
    else:
        major_category = '不明な大分類'
        
    return major_category, category_name

def scrape_page(url):
    """
    指定されたURLからカテゴリ情報、用語、説明を抽出し、辞書で返す。
    """
    try:
        time.sleep(1)  # サーバーへの負荷を軽減するために待機

        response = requests.get(url, timeout=10)
        response.encoding = response.apparent_encoding
        response.raise_for_status() 
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {url}: {e}")
        # エラー発生時は空のリストではなく、エラーフラグと代替情報を持つ辞書を返す
        return {"error": str(e)}
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # カテゴリ情報を取得
    major_cat, sub_cat = get_category_info(soup)
    
    # すべての記事を取得
    articles = soup.find_all('article', class_='term-article')

    keywords_on_page = []
    for article in articles:
        # 用語名を取得
        term_tag = article.find('h3', class_='term-article__title')
        term = term_tag.text.strip() if term_tag else '不明な用語'

        # 説明を取得
        description_tag = article.find('div', class_='term-article__body')
        description = description_tag.text.strip() if description_tag else '説明なし'

        keywords_on_page.append({
            '用語': term,
            '説明': description
        })
    
    # 用語リストとカテゴリ情報をまとめて返す
    return {
        "major_category": major_cat,
        "sub_category": sub_cat,
        "keywords": keywords_on_page
    }

def main():
    # データを辞書として初期化する (修正点1)
    all_fe_data = {} 

    # 大分類をループ
    for major_index, sub_content in enumerate(FIELD_HIERARCHY, start=1):
        
        # 小分類をループ
        for sub_index in range(1, sub_content + 1):
            
            # URLを構築
            relative_path = f"/{major_index}/{major_index}-{sub_index}"
            target_url = f"{BASE_URL}{relative_path}"

            print(f"🌐 Scraping URL: {target_url}")

            # カテゴリ情報とキーワードリストを同時に取得 (修正点2)
            page_data = scrape_page(target_url)

            if "error" in page_data:
                # エラーの場合は次のURLへ
                continue

            keywords = page_data["keywords"]
            major_cat = page_data["major_category"]
            sub_cat = page_data["sub_category"]
            
            if keywords:
                # 大分類のキーがなければ作成
                if major_cat not in all_fe_data:
                    all_fe_data[major_cat] = {}
                
                # 中分類を格納
                all_fe_data[major_cat][sub_cat] = keywords

            # サーバーへの負荷を軽減するために待機
            time.sleep(2)

    # JSONファイルに保存
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_fe_data, f, ensure_ascii=False, indent=4)
    
    print(f"\n✅ 全ての処理が完了しました。データは {OUTPUT_FILE} に保存されました。")

if __name__ == '__main__':
    main()