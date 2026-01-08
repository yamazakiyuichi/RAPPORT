#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
患者データ取得スクリプト 使用例

このスクリプトは fetch_patient_data.py の使用方法を示すサンプルです。
"""

from fetch_patient_data import RapportDBConnection, PatientDataFetcher, export_to_json
import json


def example1_get_single_patient():
    """例1: 特定の患者データを取得"""
    print("=" * 60)
    print("例1: 特定の患者データを取得")
    print("=" * 60)

    from config import DB_USERNAME, DB_PASSWORD, DB_DSN

    with RapportDBConnection(DB_USERNAME, DB_PASSWORD, DB_DSN) as db:
        fetcher = PatientDataFetcher(db)

        # 患者番号を指定してデータを取得
        patient_id = "0000000001"
        patient_data = fetcher.get_patient_all_data(patient_id)

        # 結果を表示
        print(json.dumps(patient_data, ensure_ascii=False, indent=2))

        # JSONファイルにエクスポート
        export_to_json(patient_data, f'patient_{patient_id}.json')


def example2_search_by_name():
    """例2: 氏名で患者を検索"""
    print("=" * 60)
    print("例2: 氏名で患者を検索")
    print("=" * 60)

    from config import DB_USERNAME, DB_PASSWORD, DB_DSN

    with RapportDBConnection(DB_USERNAME, DB_PASSWORD, DB_DSN) as db:
        fetcher = PatientDataFetcher(db)

        # カナ氏名で検索（部分一致）
        search_name = "ヤマダ"
        patients = fetcher.search_patients_by_name(search_name)

        print(f"'{search_name}' で検索した結果: {len(patients)}件")
        print(json.dumps(patients, ensure_ascii=False, indent=2))


def example3_get_patient_basic_info():
    """例3: 患者基本情報のみを取得"""
    print("=" * 60)
    print("例3: 患者基本情報のみを取得")
    print("=" * 60)

    from config import DB_USERNAME, DB_PASSWORD, DB_DSN

    with RapportDBConnection(DB_USERNAME, DB_PASSWORD, DB_DSN) as db:
        fetcher = PatientDataFetcher(db)

        # 患者番号を指定
        patient_id = "0000000001"

        # 基本情報のみを取得
        basic_info = fetcher.get_patient_basic_info(patient_id)
        print("基本情報:")
        print(json.dumps(basic_info, ensure_ascii=False, indent=2))

        # 住所情報を取得
        address_info = fetcher.get_patient_address(patient_id)
        print("\n住所情報:")
        print(json.dumps(address_info, ensure_ascii=False, indent=2))

        # 保険情報を取得
        insurance_info = fetcher.get_patient_insurance(patient_id)
        print("\n保険情報:")
        print(json.dumps(insurance_info, ensure_ascii=False, indent=2))

        # 傷病名情報を取得
        disease_info = fetcher.get_patient_diseases(patient_id)
        print("\n傷病名情報:")
        print(json.dumps(disease_info, ensure_ascii=False, indent=2))


def example4_get_patients_by_date():
    """例4: 登録日時の範囲で患者を取得"""
    print("=" * 60)
    print("例4: 登録日時の範囲で患者を取得")
    print("=" * 60)

    from config import DB_USERNAME, DB_PASSWORD, DB_DSN

    with RapportDBConnection(DB_USERNAME, DB_PASSWORD, DB_DSN) as db:
        fetcher = PatientDataFetcher(db)

        # 日付範囲を指定
        start_date = "2024-01-01"
        end_date = "2024-12-31"

        patients = fetcher.get_patients_by_date_range(start_date, end_date)

        print(f"{start_date} から {end_date} の間に登録された患者: {len(patients)}件")
        print(json.dumps(patients, ensure_ascii=False, indent=2))


def example5_batch_export():
    """例5: 複数患者のデータを一括エクスポート"""
    print("=" * 60)
    print("例5: 複数患者のデータを一括エクスポート")
    print("=" * 60)

    from config import DB_USERNAME, DB_PASSWORD, DB_DSN

    with RapportDBConnection(DB_USERNAME, DB_PASSWORD, DB_DSN) as db:
        fetcher = PatientDataFetcher(db)

        # 取得する患者番号のリスト
        patient_ids = ["0000000001", "0000000002", "0000000003"]

        all_patients_data = {}

        for patient_id in patient_ids:
            print(f"患者 {patient_id} のデータを取得中...")
            patient_data = fetcher.get_patient_all_data(patient_id)
            all_patients_data[patient_id] = patient_data

        # 全患者のデータを1つのJSONファイルに保存
        export_to_json(all_patients_data, 'all_patients.json')
        print(f"{len(patient_ids)}人の患者データを all_patients.json に出力しました")


if __name__ == '__main__':
    print("RAPPORT患者データ取得スクリプト 使用例\n")

    # 実行したい例を選択（コメントを外して実行）
    try:
        # 例1: 特定の患者データを取得
        example1_get_single_patient()

        # 例2: 氏名で患者を検索
        # example2_search_by_name()

        # 例3: 患者基本情報のみを取得
        # example3_get_patient_basic_info()

        # 例4: 登録日時の範囲で患者を取得
        # example4_get_patients_by_date()

        # 例5: 複数患者のデータを一括エクスポート
        # example5_batch_export()

    except ImportError:
        print("エラー: config.py が見つかりません。")
        print("config.py.example を config.py にコピーして、接続情報を設定してください。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
