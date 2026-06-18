import os
import pandas as pd
from datetime import datetime

# data_loggerのデバッグ用

class DataLogger:
    def __init__(self):
        # 履歴を保持するDataFrameを初期化
        self.history_df = pd.DataFrame(columns=[
            'Timestamp',          # タイムスタンプ
            'Result',             # 検査結果（G/B/R）
            'DefectCount',        # 欠陥の数
            'DefectPositions'     # 欠陥の位置
        ])
        self.image_handler = None  # 画像処理ハンドラーを保持する変数
        self.csv_path = "inspection_history.csv"

        # csvの読み込み，なければ作成
        if not os.path.exists(self.csv_path):
            self.save_to_csv(self.csv_path)
        else:
            self.load_from_csv(self.csv_path)

    # 画像処理ハンドラの設定 
    def set_image_handler(self, handler):
        self.image_handler = handler
    
    # 検査結果を履歴に保存
    def save_inspection_results(self):
        try:
            if not self.image_handler:
                raise Exception("画像処理ハンドラーが設定されていません")

            # 現在のタイムスタンプ，検査結果，欠陥位置を取得
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            result = self.image_handler.evaluate
            self.image_handler.GetDefectPosition() # デバッグ用，不要になる
            defect_positions = self.image_handler.defect_position
            
            # 欠陥の数を計算
            defect_count = len(defect_positions) if defect_positions else 0
            
            # 位置情報を文字列に変換して保存（CSVとの互換性のため）
            defect_positions_str = str(defect_positions) if defect_positions else ""
            
            # 新しい行データを作成
            new_row = pd.DataFrame({
                'Timestamp': [timestamp],
                'Result': [result],
                'DefectCount': [defect_count],
                'DefectPositions': [defect_positions_str]
            })
            
            # DataFrameとcsvに保存
            self.history_df = pd.concat([self.history_df, new_row], ignore_index=True)
            self.save_to_csv(self.csv_path)
            
            return True
            
        except Exception as e:
            print(f"検査結果の保存中にエラーが発生しました: {e}")
            return False
    
    # 基板登録時の履歴保存用
    def save_inspection_results_register(self):
        try:
            if not self.image_handler:
                raise Exception("画像処理ハンドラーが設定されていません")

            # 現在のタイムスタンプ，検査結果，欠陥位置を取得
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            result = "R"             # R(Register)で固定
            defect_positions = None  # Noneで固定          
            defect_count = 0         # 0で固定
            
            # 位置情報を文字列に変換して保存（CSVとの互換性のため）
            defect_positions_str = str(defect_positions) if defect_positions else ""
            
            # 新しい行データを作成
            new_row = pd.DataFrame({
                'Timestamp': [timestamp],
                'Result': [result],
                'DefectCount': [defect_count],
                'DefectPositions': [defect_positions_str]
            })
            
            # DataFrameとcsvに保存
            self.history_df = pd.concat([self.history_df, new_row], ignore_index=True)
            self.save_to_csv(self.csv_path)
            
            return True
            
        except Exception as e:
            print(f"検査結果の保存中にエラーが発生しました: {e}")
            return False

    # 検査結果(〇×表示用)
    def show_inspection_results(self):
        try:
            if not self.image_handler:
                raise Exception("画像処理ハンドラーが設定されていません")
                
            # 検査結果（良品/不良品）を取得
            self.image_handler.EvaluateResult() # デバッグ用，不要になる
            result = self.image_handler.evaluate
            
            print("検査結果を正常に表示しました")
            return result
            
        except Exception as e:
            print(f"検査結果の表示中にエラーが発生しました: {e}")
            return None


    # limitの数だけ検査履歴を取得
    def get_inspection_history(self, limit=None):
        if limit:
            return self.history_df.tail(limit)
        return self.history_df
    
    # GUI表示用に修正した履歴を取得
    def get_formatted_history(self, limit=None):
        history = self.get_inspection_history(limit)
        formatted_history = []
        
        for _, row in history.iterrows():
            # 結果を記号に変換
            if row['Result'] == "G":
                result_mark = "○"
            elif row['Result'] == "B":
                result_mark = "×"
            elif row['Result'] == "R":
                result_mark = "基板登録"
            else:
                result_mark = "-"  # 想定外の値の場合の処理
            
            # 欠陥情報の文字列を作成
            defect_info = f" - 欠陥数: {row['DefectCount']}"
            if row['DefectCount'] > 0:
                defect_info += f" - 位置: {row['DefectPositions']}"
            
            history_str = f"{row['Timestamp']}: {result_mark}{defect_info}"
            formatted_history.append(history_str)
            
        return formatted_history

    # 履歴をcsvファイルに保存
    def save_to_csv(self, filepath):
        try:
            self.history_df.to_csv(filepath, index=False)
            print(f"履歴を{filepath}に保存しました")
            return True
        except Exception as e:
            print(f"CSVファイルへの保存中にエラーが発生しました: {e}")
            return False
    
    #CSVファイルから履歴を読み込む
    def load_from_csv(self, filepath):
        try:
            self.history_df = pd.read_csv(filepath)
            print(f"履歴を{filepath}から読み込みました")
            return True
        except Exception as e:
            print(f"CSVファイルの読み込み中にエラーが発生しました: {e}")
            return False
