import cv2
# import time
# import socket
# import paramiko
# import numpy as np
import sys
import os
import time

# imageのデバッグ用

class Image():
    # 初期化処理
    def __init__(self):
        self.capture_img            = None              # 撮影した画像 [img]
        self.concat_img             = None              # 結合した画像（concatで結合する感覚）[img]
        self.correct_img            = None              # 登録した正解の画像 [img]
        self.correct_img_filepath   = "image1.jpg" # 正解画像の保存先 [string]
        self.evaluate           = None # 検査結果 [string] (G:欠陥無し, B:欠陥あり)
        self.defect_position    = []   # 欠陥の座標位置 [list] 

    # 写真撮影
    def CaptureImage(self):

        print("CaptureImage")
        time.sleep(1)

    # 画像結合
    def ConcatImage(self):
        try:
            # 現在のファイルと同じディレクトリのパスを取得
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # image1.jpgへのパスを作成
            concat_image_filepath = os.path.join(current_dir, "image2.jpg")
            
            # 画像の読み込み
            concat_img = cv2.imread(concat_image_filepath)
            
            if concat_img is None:
                raise Exception(f"画像の読み込みに失敗しました: {concat_image_filepath}")
            
            # 画像のリサイズ（400×300）
            concat_img = cv2.resize(concat_img, (400, 300))

            self.concat_img = concat_img    
            #return concat_img

        except Exception as e:
            print(f"Error in LoadCorrectImage: {str(e)}")
            return None

    def InspectImg(self):
        print("InspectImage")

    # 正解画像の読み込み
    def LoadCorrectImage(self):
        try:
            # 現在のファイルと同じディレクトリのパスを取得
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # image1.jpgへのパスを作成
            correct_image_filepath = os.path.join(current_dir, "image1.jpg")
            
            # 画像の読み込み
            correct_img = cv2.imread(correct_image_filepath)
            
            if correct_img is None:
                raise Exception(f"画像の読み込みに失敗しました: {correct_image_filepath}")
            
            # 画像のリサイズ（400×300）
            correct_img = cv2.resize(correct_img, (400, 300))
            self.correct_img = correct_img
            #return correct_img

        except Exception as e:
            print(f"Error in LoadCorrectImage: {str(e)}")
            return None

    # 検査結果の評価
    def EvaluateResult(self):
        # 検査結果の判定
        evaluate = "B"   # 欠陥があれば "B" 仮にBにする
        #evaluate = "G"   # 欠陥がなければ "G"
        
        self.evaluate = evaluate
        #return evaluate
        print("EvaluateResult")

    # 欠陥箇所の座標取得
    def GetDefectPosition(self):
        # 欠陥の位置を格納
        defect_position = []
        defect_position.append((1, 2, 3, 4)) # 仮データ
        defect_position.append((5, 6, 7, 8))
        defect_position.append((9, 10, 11, 12))

        self.defect_position = defect_position
        #return defect_position
        print("GetDefectPosition")

    # 正解基板の登録
    def RegisterSubstrate(self):
        print("RegisterSubstrate")

    # 欠陥箇所を囲む
    def FrameDefect(self):
        print("FrameDefect")

    def StartServer(self):
        print("StartServer")

    # ラズパイに接続
    def ConnectRaspi(self):
        print("ConnectRaspi")

    # ラズパイのサーバスクリプトを実行
    def ExecuteRaspiScript(self):
        print("ExecuteRaspiScript")
 
    def InstructMotor(self, state):
        if(state == "S"):
            print("StartMotor")
        elif(state == "I"):
            print("InspectMotor")
        elif(state == "E"):
            if self.evaluate == "B":
                print("back")
            else:
                print("forward")