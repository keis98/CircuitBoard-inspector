import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image as PILImage, ImageTk
import cv2
from image_debug import Image  # デバッグ用，不要になる
#from image import Image  # 必要になる
from data_logger_debug import DataLogger  # DataLoggerクラスの読み込み

# guiのデバッグ用 
# imageのデバッグ用と動かすこと前提

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("基板検査GUI")
        self.root.geometry("800x600")
        self.root.resizable(False, False)  # 画面サイズ固定
        root.configure(bg="#ecf0f1")
        
        # Imageクラスのインスタンス化
        self.image_processor = Image()

        # data_loggerクラスのインスタンス化
        self.data_logger = DataLogger()
        self.data_logger.set_image_handler(self.image_processor)
        
        # ラズパイサーバー立ち上げ
        self.image_processor.StartServer() 

        # 画像と結果の状態管理用の変数を追加
        self.inspection_image = None
        self.inspection_result = None
        self.update_check_id = None
        self.current_screen = None  # 現在の画面を追跡
        self.inspection_complete = False  # 検査/撮影完了フラグ

        # 画面ごとの更新完了時のコールバック
        self.update_callbacks = {
            "disp2": self.on_inspection_complete,
            "disp4": self.on_registration_complete
        }

        # スタイルの定義
        self.style = ttk.Style()
        
        # 既存のスタイル
        self.style.configure("TButton", font=("Meiryo", 17), padding=5)
        self.style.configure("TLabel", font=("Rounded M+ 1c", 18))
        self.style.configure("TFrame", background="#ecf0f1")

        # 追加のスタイル
        self.style.configure("title.TLabel", font=("Rounded M+ 1c", 22), weight="bold")
        self.style.configure("back_mainmenu.TButton", font=("Meiryo", 13))

        self.main_menu()

    def show_dialog(self, dialog_type):
        if dialog_type == "Dialog1":
            response1 = messagebox.askokcancel("question", "終了しますか？")
            if response1:
                self.root.quit()

        elif dialog_type == "Dialog2":
            response2 = messagebox.askokcancel("question", "もう一度検査しますか？")
            if response2:
                self.start_inspection()

        elif dialog_type == "Dialog3":
            messagebox.showinfo("info", "基板を登録しました")

        elif dialog_type == "Dialog4":
            messagebox.showwarning("warning", "異常を検知しました")

        elif dialog_type == "Dialog5":
            response3 = messagebox.askokcancel("question", "基板をセットしていますか？")
            if response3:
                self.start_inspection()

        elif dialog_type == "Dialog6":
            response4 = messagebox.askokcancel("question", "基板をセットしていますか？")
            if response4:
                self.start_registration()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def main_menu(self):
        self.clear_screen()
        ttk.Label(self.root, text="メインメニュー", style="title.TLabel").place(x=330, y=20)
        ttk.Button(self.root, text="検査開始", command=lambda: self.show_dialog("Dialog5")).place(x=300, y=200, width=200, height=50)
        ttk.Button(self.root, text="設定", command=self.switch_to_disp3).place(x=300, y=300, width=200, height=50)
        ttk.Button(self.root, text="終了", command=lambda: self.show_dialog("Dialog1")).place(x=550, y=500, width=200, height=50)

    # 結合画像と検査結果のリセット
    # 検査開始時，メインメニューに戻るとき，再検査時にリセット
    def reset_inspection_state(self):
        if self.update_check_id:
            self.root.after_cancel(self.update_check_id)
            self.update_check_id = None
        
        self.inspection_image = None
        self.inspection_result = None
        self.inspection_complete = False


    def check_updates(self, is_registration=False):
        # 画面が遷移している場合は更新を停止
        if (self.current_screen != "disp2" and self.current_screen != "disp4") or not hasattr(self, 'image_label'):
            self.reset_inspection_state()
            return
        
        updated = False
        
        # 画像の更新チェック
        if self.inspection_image is None:
            self.image_processor.ConcatImage() # デバッグ用，不要になる
            new_image = self.image_processor.concat_img

            if new_image is not None:
                self.inspection_image = new_image
                self.update_inspection_image()
                updated = True
        
        # 結果の更新チェック
        if self.inspection_result is None:
            if is_registration:
                new_result = "R"
            else:
                new_result = self.data_logger.show_inspection_results()
            
            if new_result is not None:
                self.inspection_result = new_result
                if not is_registration: 
                    self.update_inspection_result() # 検査時
                else:
                    self.update_inspection_result_register() # 基板登録時
                updated = True
        
        # 更新完了チェック
        if self.inspection_image is not None and self.inspection_result is not None:
            self.inspection_complete = True
            
            # 画面固有の完了処理を実行
            if self.current_screen in self.update_callbacks:
                self.update_callbacks[self.current_screen]()
            
            if self.update_check_id:
                self.root.after_cancel(self.update_check_id)
                self.update_check_id = None
        else:
            self.update_check_id = self.root.after(500, lambda: self.check_updates(is_registration))
    
    def on_inspection_complete(self):
        """検査完了時の処理"""
        if hasattr(self, 'result_label'):
            self.data_logger.save_inspection_results()

    def on_registration_complete(self):
        """登録準備完了時の処理"""
        if hasattr(self, 'register_button'):
            self.register_button.state(['!disabled'])

    # 検査時のモータ・カメラ処理
    def start_inspection(self):
        self.reset_inspection_state()
        self.current_screen = "disp2"
        self.switch_to_disp2()
        self.root.update()  # 画面を強制的に更新
        
        self.image_processor.InstructMotor("S")

        for _ in range(3):
            self.image_processor.CaptureImage()
            self.image_processor.ConcatImage()
            self.image_processor.InstructMotor("I")
        
        self.check_updates(False)
    

    def switch_to_disp2(self):
        self.clear_screen()
        self.current_screen = "disp2"
        ttk.Label(self.root, text="検査画面", style="title.TLabel").place(x=350, y=20)

        # 画像表示用のラベルを作成（プレースホルダー画像で初期化）
        self.image_label = ttk.Label(self.root)
        self.image_label.place(x=200, y=80)
        
        # プレースホルダー画像の設定
        placeholder = PILImage.new('RGB', (400, 300), color='gray')
        placeholder_photo = ImageTk.PhotoImage(placeholder)
        self.image_label.configure(image=placeholder_photo)
        self.image_label.image = placeholder_photo

        # 結果表示用の枠
        self.result_frame = ttk.Frame(self.root, style="TFrame", width=200, height=200)
        self.result_frame.place(x=50, y=450)
        self.result_frame.propagate(False)

        self.result_label = ttk.Label(self.result_frame, text="検査中...", style="TLabel")
        self.result_label.pack(pady=20)

        ttk.Button(self.root, text="もう一度検査する", command=lambda: self.show_dialog("Dialog2")).place(x=350, y=500, width=200, height=50)
        ttk.Button(self.root, text="メインメニューに戻る", command=self.main_menu, style="back_mainmenu.TButton").place(x=550, y=500, width=200, height=50)
    
    # 結合後の基板画像の更新
    def update_inspection_image(self):

        if self.inspection_image is not None:
            # OpenCV画像をPIL画像に変換
            rgb_image = cv2.cvtColor(self.inspection_image, cv2.COLOR_BGR2RGB)
            pil_image = PILImage.fromarray(rgb_image)
            photo = ImageTk.PhotoImage(pil_image)
            
            # 画像を更新
            self.image_label.configure(image=photo)
            self.image_label.image = photo

    # 検査結果の更新
    def update_inspection_result(self):

        # 基板登録時はここが×になるが，result_textを使わないので問題ない
        if self.inspection_result is not None:
            if self.inspection_result == "G":
                self.result_label.configure(text="〇", font=("Rounded M+ 1c", 88), foreground="blue")
            else:
                self.result_label.configure(text="×", font=("Rounded M+ 1c", 88), foreground="red")

            #result_text = "〇" if self.inspection_result == "G" else "×"
            #self.result_label.configure(text=result_text, font=("Rounded M+ 1c", 56))
            
            # 不良品の場合は警告ダイアログを表示
            if self.inspection_result == "B":
                self.show_dialog("Dialog4")
                # モータを逆転させる
                self.image_processor.InstructMotor("E")
            else:
                # モータを正転させる
                self.image_processor.InstructMotor("E")
    
    # 基板登録時のモータ制御用
    def update_inspection_result_register(self):

        if self.inspection_result is not None:
            
            # 念のためevaluateの中身を変更しないように
            temp_evaluate = self.image_processor.evaluate
            self.image_processor.evaluate = "B"

            # モータを逆転させる
            self.image_processor.InstructMotor("E")

            self.image_processor.evaluate = temp_evaluate



    def switch_to_disp3(self):
        self.clear_screen()
        ttk.Label(self.root, text="設定", style="title.TLabel").place(x=350, y=20)

        ttk.Checkbutton(self.root, text="設定項目1").place(x=100, y=100)
        ttk.Checkbutton(self.root, text="設定項目2").place(x=100, y=140)
        ttk.Scale(self.root, from_=0, to=100, orient="horizontal").place(x=100, y=180, width=200)

        ttk.Button(self.root, text="基板登録", command=lambda: self.show_dialog("Dialog6")).place(x=300, y=300, width=200, height=50)
        ttk.Button(self.root, text="正解基板確認", command=self.check_correct_image).place(x=300, y=400, width=200, height=50)
        ttk.Button(self.root, text="履歴確認", command=self.switch_to_disp6).place(x=300, y=450, width=200, height=50)
        ttk.Button(self.root, text="メインメニューに戻る", command=self.main_menu, style="back_mainmenu.TButton").place(x=550, y=500, width=200, height=50)

    # 基板登録時のモータ・カメラ処理
    def start_registration(self):
        self.reset_inspection_state()
        self.current_screen = "disp4"
        self.switch_to_disp4()
        self.root.update()  # 画面を強制的に更新
        
        self.image_processor.InstructMotor("S")

        for _ in range(3):
            self.image_processor.CaptureImage()
            self.image_processor.ConcatImage()
            self.image_processor.InstructMotor("I")
        
        self.check_updates(True)
    

    def switch_to_disp4(self):
        self.clear_screen()
        self.current_screen = "disp4"
        
        ttk.Label(self.root, text="基板登録確認", style="title.TLabel").place(x=300, y=20)

        self.image_label = ttk.Label(self.root)
        self.image_label.place(x=200, y=80)
        
        placeholder = PILImage.new('RGB', (400, 300), color='gray')
        placeholder_photo = ImageTk.PhotoImage(placeholder)
        self.image_label.configure(image=placeholder_photo)
        self.image_label.image = placeholder_photo

        self.register_button = ttk.Button(self.root, text="基板を登録", command=self.register_board)
        self.register_button.place(x=100, y=500, width=200, height=50)
        
        if not self.inspection_complete:
            self.register_button.state(['disabled'])

        ttk.Button(self.root, text="設定画面に戻る", command=self.switch_to_disp3).place(x=350, y=500, width=200, height=50)
        ttk.Button(self.root, text="メインメニューに戻る", command=self.main_menu, style="back_mainmenu.TButton").place(x=550, y=500, width=200, height=50)

    # 正解基板登録の処理
    def register_board(self):

        self.image_processor.RegisterSubstrate() # 正解基盤の基板登録を行う
        self.data_logger.save_inspection_results_register() # 履歴の登録
        # 既存のダイアログ表示
        self.show_dialog("Dialog3")

    # 「正解基板確認」を押されたときの処理  正解基板の画像を渡す
    def check_correct_image(self):
        # imageの呼び出し - 正解画像を取得
        
        self.image_processor.LoadCorrectImage() # デバッグ用，不要になる
        correct_img = self.image_processor.correct_img # デバッグ用，不要になる

        # 本番では以下の2種類のどちらかを使う 必要になる

        # 保存されたcorrect_imgをよぶパターン
        #correct_img_filepath = self.image_handler.correct_img_filepath
        #correct_img = cv2.imread(correct_img_filepath)

        # correct_imgをそのまま呼ぶパターン
        #correct_image = self.image_handler.correct_img

        if correct_img is not None:
            # 画像付きで画面遷移
            self.switch_to_disp5(correct_img)
        else:
            # 画像読み込み失敗時は通常の遷移
            self.switch_to_disp5()

        
    def switch_to_disp5(self, correct_img=None):
        self.clear_screen()
        ttk.Label(self.root, text="正解基板確認画面", style="title.TLabel").place(x=300, y=20)

        if correct_img is not None:
            rgb_img = cv2.cvtColor(correct_img, cv2.COLOR_BGR2RGB)
            pil_img = PILImage.fromarray(rgb_img)
            photo_img = ImageTk.PhotoImage(pil_img)
            # 画像を中央に配置
            img_label = ttk.Label(self.root, image=photo_img)
            img_label.place(relx=0.5, rely=0.4, anchor="center")
            self.root.correct_img = photo_img
        else:
            ttk.Label(self.root, text="正解基板画像を読み込めませんでした", style="TLabel").place(relx=0.5, rely=0.4, anchor="center")

        ttk.Button(self.root, text="設定画面に戻る", command=self.switch_to_disp3).place(x=350, y=500, width=200, height=50)
        ttk.Button(self.root, text="メインメニューに戻る", command=self.main_menu, style="back_mainmenu.TButton").place(x=550, y=500, width=200, height=50)

    
    def switch_to_disp6(self):
        self.clear_screen()
        ttk.Label(self.root, text="履歴確認画面", style="title.TLabel").place(x=300, y=20)

        # 履歴表示用のフレームを作成（画面中央に配置）
        history_frame = ttk.Frame(self.root)
        history_frame.place(x=100, y=80, width=600, height=380) 
        
        # Canvasとスクロールバーを追加（縦と横）
        canvas = tk.Canvas(history_frame)
        scrollbar_y = ttk.Scrollbar(history_frame, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(history_frame, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)
        
        # スクロール領域の設定
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # キャンバスウィンドウの作成（スクロール可能なフレームを配置）
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # スクロールバーの設定
        canvas.configure(
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        
        # データロガーから全履歴を取得して表示
        history = self.data_logger.get_formatted_history()
        for item in history:
            ttk.Label(scrollable_frame, text=item, style="TLabel").pack(pady=2, anchor="w")
        
        # スクロールバーとキャンバスの配置
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

        # 下部にボタンを配置（スクロールバーの下になるように y座標を調整）
        ttk.Button(self.root, text="設定画面に戻る", command=self.switch_to_disp3).place(x=350, y=500, width=200, height=50)
        ttk.Button(self.root, text="メインメニューに戻る", command=self.main_menu, style="back_mainmenu.TButton").place(x=550, y=500, width=200, height=50)

    
if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()