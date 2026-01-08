# RAPPORT

医療システムRAPPORTのデータベーススキーマ定義と患者データ取得ツール

## 概要

このリポジトリには以下が含まれています:
- RAPPORTシステムのデータベーステーブル定義（Markdownファイル）
- 患者データを取得するPythonスクリプト

## 患者データ取得スクリプト

### 必要な環境

- Python 3.7以上
- Oracle Database接続環境
- Oracle Instant Client（cx_Oracleの動作に必要）

### インストール

1. 必要なパッケージをインストール:
```bash
pip install -r requirements.txt
```

2. データベース接続設定ファイルを作成:
```bash
cp config.py.example config.py
```

3. `config.py` を編集して実際の接続情報を設定:
```python
DB_USERNAME = "your_username"
DB_PASSWORD = "your_password"
DB_DSN = "hostname:1521/service_name"
```

### 使用方法

#### 基本的な使用例

```python
from fetch_patient_data import RapportDBConnection, PatientDataFetcher
from config import DB_USERNAME, DB_PASSWORD, DB_DSN

# データベース接続
with RapportDBConnection(DB_USERNAME, DB_PASSWORD, DB_DSN) as db:
    fetcher = PatientDataFetcher(db)

    # 患者番号を指定してデータを取得
    patient_data = fetcher.get_patient_all_data("0000000001")
    print(patient_data)
```

#### サンプルスクリプトの実行

```bash
python example_usage.py
```

### 主要な機能

- `get_patient_basic_info(patient_id)`: 患者基本情報を取得
- `get_patient_address(patient_id)`: 患者住所情報を取得
- `get_patient_insurance(patient_id)`: 患者保険情報を取得
- `get_patient_diseases(patient_id)`: 患者傷病名情報を取得
- `get_patient_all_data(patient_id)`: 患者の全データを取得
- `search_patients_by_name(name)`: 氏名で患者を検索
- `get_patients_by_date_range(start_date, end_date)`: 登録日時の範囲で患者を検索

### データベーステーブル

主要な患者関連テーブル:
- `TTPT01`: 患者基本情報
- `TTPT02`: 患者住所情報
- `TTPT03`: 患者識別情報
- `TTPT11`: 患者保険情報
- `TTBY01`: 患者傷病名情報

詳細なテーブル定義は各Markdownファイルを参照してください。

## セキュリティ

- `config.py` には機密情報が含まれるため、バージョン管理には含めないでください
- `.gitignore` に `config.py` を追加することを推奨します

## ライセンス

このプロジェクトのライセンスについては、プロジェクトオーナーにお問い合わせください。