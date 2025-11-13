import json
import csv
import os

# --- 設定 ---
INPUT_JSON_FILE = 'fe_keywords_data.json'
OUTPUT_CSV_FILE = 'anki_fe_cards.csv'
# --- 設定 終 ---

def convert_json_to_csv():
    if not os.path.exists(INPUT_JSON_FILE):
        print(f"❌ エラー: 入力ファイル '{INPUT_JSON_FILE}' が見つかりません。")
        return

    # 1. JSONファイルを読み込む
    with open(INPUT_JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 2. CSVファイルを開き、書き込み準備をする
    # newline='' は空行が入るのを防ぐため、encoding='utf-8-sig' はExcelでの文字化けを防ぐため
    with open(OUTPUT_CSV_FILE, 'w', encoding='utf-8-sig', newline='') as csvfile:
        # writerowsを使うため、リストとしてデータを準備します
        fieldnames = ['用語', '説明', 'タグ', 'デッキ名']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t') # 区切り文字をタブ (\t) に設定（より安全なため）
        
        # ヘッダー行を書き込む（Ankiには必須ではないが分かりやすさのため）
        # writer.writeheader() 

        card_count = 0
        
        # 3. JSONの階層構造をループし、CSV形式のリストに変換する
        # 大分類 (例: "1 基礎理論") をループ
        for major_cat, sub_categories in data.items():
            # デッキ名として使用するため、大分類から番号を除去
            deck_name = major_cat.split(' ', 1)[-1].strip()
            
            # 中分類 (例: "離散数学") をループ
            for sub_cat, keywords in sub_categories.items():
                
                # タグとして使用するため、中分類名を設定
                tag_name = sub_cat.replace(' ', '_').replace('-', '_') # タグとして使いやすいように整形
                
                # 用語のリストをループ
                for item in keywords:
                    # CSVの1行分のデータを作成
                    writer.writerow({
                        '用語': item['用語'],
                        '説明': item['説明'],
                        # 複数タグ対応のため、大分類名と中分類名をタグとして使用
                        'タグ': f"{deck_name.replace(' ', '_')} {tag_name}", 
                        'デッキ名': deck_name # 大分類名をAnkiのデッキ名に使用
                    })
                    card_count += 1

    print(f"\n✅ 変換が完了しました。")
    print(f"ファイル: **{OUTPUT_CSV_FILE}**")
    print(f"作成されたカード数: **{card_count}**")

if __name__ == '__main__':
    convert_json_to_csv()
