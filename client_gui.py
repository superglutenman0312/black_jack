import socket
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# 計算點數
has_ace = False
def calculate_card_value(card):
    rank = int(card[:-1])
    global has_ace
    if rank == 1: # 花色1要特判
        has_ace = True
        return 1
    elif rank in range(11, 14):
        return 10
    else:
        return rank

class BlackjackClient(tk.Tk):
    def __init__(self):
        global has_ace
        super().__init__()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("127.0.0.1", 5555))
        
        self.geometry("800x400")
        
        self.cards_frame = tk.Frame(self)
        self.cards_frame.pack(pady=20)

        self.total_points_label = tk.Label(self, text="Total Points: 0", font=("Arial", 12))
        self.total_points_label.pack()

        self.draw_button = tk.Button(self, text="DRAW", height=3, width=20, command=self.draw_card)
        self.draw_button.pack(pady=10)

        self.stop_button = tk.Button(self, text="STOP", height=3, width=20, command=self.stop_turn)
        self.stop_button.pack(pady=10)
        
        self.player_id = self.client.recv(1024).decode()
        self.title(f"Blackjack Game (player {self.player_id})")
        print(f"You are \"player {self.player_id}\"")
        
        # 初始設置
        self.total_points = 0
        self.card_cnt = 0
        self.card_labels = []  # 用於存放卡片圖片的 Label 控件
        
    def draw_card(self):
        self.client.send("DRAW".encode())
        response = self.client.recv(1024).decode()
        
        if "drew" in response:
            card_info = response.split(", ")
            card = card_info[0][7:]
            remaining_cards = card_info[1][17:]
            card_val = calculate_card_value(card)
            self.total_points += card_val
            self.card_cnt += 1

            print(f"Drew {card}")
            if card_val == 1:
                print(f"This card value = 1 or 11")
            else:
                print(f"This card value = {card_val}")

            if has_ace and self.total_points + 10 <= 21:
                print(f"You have {self.card_cnt} cards, total points = {self.total_points} or {self.total_points + 10}")
                self.total_points_label.config(text=f"Total Points: {self.total_points} or {self.total_points + 10}")
            else:
                print(f"You have {self.card_cnt} cards, total points = {self.total_points}")
                self.total_points_label.config(text=f"Total Points: {self.total_points}")
            
            # 顯示卡牌圖片
            card_image = Image.open(f"poker_dataset/{card}.png")
            card_image = card_image.resize((100, 150))  # 改變圖片大小
            card_image_tk = ImageTk.PhotoImage(card_image)
            
            # 新增卡牌到畫面
            label = tk.Label(self.cards_frame, image=card_image_tk, bg="green")
            label.image = card_image_tk  # 防止垃圾回收
            label.grid(row=0, column=self.card_cnt - 1, padx=10)  # 動態排版
            self.card_labels.append(label)
                        
            if self.total_points > 21:
                messagebox.showinfo("Bust", "You've exceeded 21 points.")
                self.client.send(f"STOP".encode())
                self.client.send(f"{self.player_id}, -1".encode())
                print("Bust! You've exceeded 21 points.")
                print("Waiting for other players...")
                response = self.client.recv(1024).decode()
                if "winner" in response:
                    print(response)
                    messagebox.showinfo("Game Over ", response)
                self.client.close()
                self.quit()

    def stop_turn(self):
        # 計算最終分數
        true_total_points = self.total_points + 10 if has_ace and self.total_points + 10 <= 21 else self.total_points
        self.client.send(f"STOP".encode())
        print(f"Your total points is {true_total_points}.")
        self.client.send(str(f"{self.player_id}, {true_total_points}").encode())
        print("Waiting for other players...")
        response = self.client.recv(1024).decode()
        if "winner" in response:
            print(response)
            messagebox.showinfo("Game Over ", response)
        self.client.close()
        self.quit()

def start_client():
    app = BlackjackClient()
    app.mainloop()

start_client()
