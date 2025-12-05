import socket
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  # 用於顯示圖片

# 計算點數機制
has_ace = False
def calculate_card_value(card):
    rank = int(card[:-1])  # 去掉花色後取數字部分
    global has_ace
    if rank == 1:
        has_ace = True
        return 1  # Ace 的點數可以是 1 或 11
    elif rank in range(11, 14):  # 11, 12, 13 的點數都是 10
        return 10
    else:
        return rank

def start_client():
    global has_ace
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 5555))

    player_id = client.recv(1024).decode()
    print(f"You are \"player {player_id}\"")
    print("Enter 'DRAW' to draw a card, 'STOP' to stop.")
    
    total_points = 0
    card_cnt = 0
    waiting_for_round_winner = False  # 新增變數標記是否在等待結果
    
    response = client.recv(1024).decode()
    if "drew" in response:
        card_info = response.split(", ")
        card = card_info[0]
        card = card[6:]
        remaining_cards = card_info[1]
        remaining_cards = remaining_cards[17:]
        card_val = calculate_card_value(card)
        total_points += card_val
        card_cnt += 1
        print(f"Your initial card is {card}")
        if card_val == 1:
            print(f"This card value = 1 or 11")
        else:
            print(f"This card value = {card_val}")
        
        if has_ace and total_points + 10 <= 21:
            print(f"You have {card_cnt} cards, total card value = {total_points} or {total_points + 10}")
        else:
            print(f"You have {card_cnt} cards, total card value = {total_points}")
    
    
    while True:
        if not waiting_for_round_winner:
            message = input(" > ")
            client.send(message.encode())
        else:
            message = None
            
        response = client.recv(1024).decode()
        # print(response)
        
        if "drew" in response:
            card_info = response.split(", ")
            card = card_info[0]
            card = card[6:]
            remaining_cards = card_info[1]
            remaining_cards = remaining_cards[17:]
            card_val = calculate_card_value(card)
            total_points += card_val
            card_cnt += 1
            print(f"Drew {card}")
            if card_val == 1:
                print(f"This card value = 1 or 11")
            else:
                print(f"This card value = {card_val}")
            
            if has_ace and total_points + 10 <= 21:
                print(f"You have {card_cnt} cards, total card value = {total_points} or {total_points + 10}")
            else:
                print(f"You have {card_cnt} cards, total card value = {total_points}")
                
            # 判斷有沒有超過21點
            if total_points > 21:
                print("Bust! You've exceeded 21 points.")
                client.send("STOP".encode())
                client.send(str(f"{player_id}, -1").encode())
                print("Waiting for other players...")
                waiting_for_round_winner = True  # 進入等待狀態

        elif message == "STOP":
            # 決定此client的true total points
            if has_ace and total_points + 10 <= 21:
                true_total_points = total_points + 10
            else:
                true_total_points = total_points
            print(f"Your total points is {true_total_points}.")
            # 傳送得分到伺服器
            client.send(str(f"{player_id}, {true_total_points}").encode())
            print("Waiting for other players...")
            waiting_for_round_winner = True  # 進入等待狀態

        elif "winner" in response:  # 收到伺服器的冠軍資訊
            print(response)  # 顯示冠軍結果
            client.close()
            break

start_client()
