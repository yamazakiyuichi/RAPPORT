#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
患者データ取得スクリプト
RAPPORT医療システムから患者データを取得するためのPythonスクリプト
"""

import cx_Oracle
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RapportDBConnection:
    """RAPPORTデータベース接続クラス"""

    def __init__(self, username: str, password: str, dsn: str):
        """
        Args:
            username: データベースユーザー名
            password: データベースパスワード
            dsn: データソース名 (host:port/service_name)
        """
        self.username = username
        self.password = password
        self.dsn = dsn
        self.connection = None

    def connect(self):
        """データベースに接続"""
        try:
            self.connection = cx_Oracle.connect(
                user=self.username,
                password=self.password,
                dsn=self.dsn,
                encoding="UTF-8"
            )
            logger.info("データベース接続成功")
            return self.connection
        except cx_Oracle.Error as error:
            logger.error(f"データベース接続エラー: {error}")
            raise

    def disconnect(self):
        """データベース接続を切断"""
        if self.connection:
            self.connection.close()
            logger.info("データベース接続を切断しました")

    def __enter__(self):
        """コンテキストマネージャー: with文で使用"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー: with文終了時"""
        self.disconnect()


class PatientDataFetcher:
    """患者データ取得クラス"""

    def __init__(self, db_connection: RapportDBConnection):
        """
        Args:
            db_connection: データベース接続オブジェクト
        """
        self.db = db_connection

    def _execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        SQLクエリを実行して結果を返す

        Args:
            query: 実行するSQLクエリ
            params: バインド変数のパラメータ

        Returns:
            クエリ結果のリスト
        """
        cursor = self.db.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            columns = [col[0] for col in cursor.description]
            results = []

            for row in cursor.fetchall():
                row_dict = {}
                for i, value in enumerate(row):
                    # 日付型をISO形式の文字列に変換
                    if isinstance(value, datetime):
                        row_dict[columns[i]] = value.isoformat()
                    else:
                        row_dict[columns[i]] = value
                results.append(row_dict)

            return results
        except cx_Oracle.Error as error:
            logger.error(f"クエリ実行エラー: {error}")
            raise
        finally:
            cursor.close()

    def get_patient_basic_info(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        患者基本情報を取得 (TTPT01)

        Args:
            patient_id: 患者番号

        Returns:
            患者基本情報の辞書、見つからない場合はNone
        """
        query = """
        SELECT
            F001 as 患者番号,
            F002 as カナ名,
            F003 as カナ氏名,
            F004 as 漢字名,
            F005 as 漢字氏名,
            F006 as 性別,
            F007 as 生年月日,
            F008 as 血液型,
            F010 as 職種,
            F016 as 患者区分1,
            F017 as 患者区分2,
            F018 as 患者コメント1,
            F019 as 患者コメント2,
            UPDDT as 更新日時
        FROM TTPT01
        WHERE F001 = :patient_id
        """
        results = self._execute_query(query, {'patient_id': patient_id})
        return results[0] if results else None

    def get_patient_address(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        患者住所情報を取得 (TTPT02)

        Args:
            patient_id: 患者番号

        Returns:
            患者住所情報のリスト
        """
        query = """
        SELECT
            F001 as 患者番号,
            F002 as 住所区分,
            F003 as 郵便番号,
            F004 as 住所,
            F005 as 電話番号,
            UPDDT as 更新日時
        FROM TTPT02
        WHERE F001 = :patient_id
        ORDER BY F002
        """
        return self._execute_query(query, {'patient_id': patient_id})

    def get_patient_insurance(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        患者保険情報を取得 (TTPT11)

        Args:
            patient_id: 患者番号

        Returns:
            患者保険情報のリスト
        """
        query = """
        SELECT
            F001 as 患者番号,
            F002 as 保険番号,
            F003 as 保険者番号,
            F004 as 保険種別,
            F005 as 本人家族区分,
            F006 as 記号,
            F007 as 番号,
            F008 as 有効開始日,
            F009 as 有効終了日,
            UPDDT as 更新日時
        FROM TTPT11
        WHERE F001 = :patient_id
        ORDER BY F002
        """
        return self._execute_query(query, {'patient_id': patient_id})

    def get_patient_diseases(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        患者傷病名情報を取得 (TTBY01)

        Args:
            patient_id: 患者番号

        Returns:
            患者傷病名情報のリスト
        """
        query = """
        SELECT
            F001 as 患者番号,
            F002 as 傷病名連番,
            F003 as 診療科,
            F004 as 傷病名コード,
            F005 as 傷病名,
            F006 as 診療開始日,
            F007 as 診療終了日,
            F008 as 転帰区分,
            UPDDT as 更新日時
        FROM TTBY01
        WHERE F001 = :patient_id
        ORDER BY F006 DESC
        """
        return self._execute_query(query, {'patient_id': patient_id})

    def get_patient_all_data(self, patient_id: str) -> Dict[str, Any]:
        """
        患者の全データを取得

        Args:
            patient_id: 患者番号

        Returns:
            患者の全データを含む辞書
        """
        logger.info(f"患者ID {patient_id} のデータを取得中...")

        data = {
            '基本情報': self.get_patient_basic_info(patient_id),
            '住所情報': self.get_patient_address(patient_id),
            '保険情報': self.get_patient_insurance(patient_id),
            '傷病名情報': self.get_patient_diseases(patient_id),
        }

        return data

    def search_patients_by_name(self, name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        患者を氏名（カナ）で検索

        Args:
            name: 検索する氏名（カナ、部分一致）
            limit: 取得する最大件数

        Returns:
            患者基本情報のリスト
        """
        query = f"""
        SELECT
            F001 as 患者番号,
            F002 as カナ名,
            F003 as カナ氏名,
            F004 as 漢字名,
            F005 as 漢字氏名,
            F006 as 性別,
            F007 as 生年月日
        FROM TTPT01
        WHERE F003 LIKE :name
        AND ROWNUM <= :limit
        ORDER BY F001
        """
        return self._execute_query(query, {'name': f'%{name}%', 'limit': limit})

    def get_patients_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        登録日時の範囲で患者を検索

        Args:
            start_date: 開始日 (YYYY-MM-DD形式)
            end_date: 終了日 (YYYY-MM-DD形式)

        Returns:
            患者基本情報のリスト
        """
        query = """
        SELECT
            F001 as 患者番号,
            F002 as カナ名,
            F003 as カナ氏名,
            F004 as 漢字名,
            F005 as 漢字氏名,
            F006 as 性別,
            F007 as 生年月日,
            F023 as 登録日時
        FROM TTPT01
        WHERE F023 BETWEEN TO_DATE(:start_date, 'YYYY-MM-DD')
                       AND TO_DATE(:end_date, 'YYYY-MM-DD')
        ORDER BY F023 DESC
        """
        return self._execute_query(query, {'start_date': start_date, 'end_date': end_date})


def export_to_json(data: Dict[str, Any], output_file: str):
    """
    データをJSONファイルにエクスポート

    Args:
        data: エクスポートするデータ
        output_file: 出力ファイル名
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"データを {output_file} に出力しました")
    except Exception as e:
        logger.error(f"ファイル出力エラー: {e}")
        raise


if __name__ == '__main__':
    # 使用例
    # 設定ファイルから接続情報を読み込む場合は config.py を使用
    try:
        from config import DB_USERNAME, DB_PASSWORD, DB_DSN

        # データベース接続
        with RapportDBConnection(DB_USERNAME, DB_PASSWORD, DB_DSN) as db:
            fetcher = PatientDataFetcher(db)

            # 患者番号を指定してデータを取得
            patient_id = "0000000001"
            patient_data = fetcher.get_patient_all_data(patient_id)

            # 結果を表示
            print(json.dumps(patient_data, ensure_ascii=False, indent=2))

            # JSONファイルにエクスポート
            export_to_json(patient_data, f'patient_{patient_id}.json')

    except ImportError:
        logger.error("config.py が見つかりません。config.py.example を参考に作成してください。")
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
