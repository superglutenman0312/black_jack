import socket
import threading
import random

# 建立 52 張牌的牌組
def initialize_deck():
    suits = ["c", "d", "h", "s"]  # 梅花、方塊、紅心、黑桃
    return [f"{rank}{suit}" for rank in range(1, 14) for suit in suits]

# 抽牌功能，確保不重複抽牌
def draw_card(deck, drawn_cards):
    available_cards = [card for card in deck if card not in drawn_cards]
    if not available_cards:
        return None  # 當牌組抽光時回傳 None
    card = random.choice(available_cards)
    drawn_cards.add(card)  # 標記該牌為已抽取
    return card

def announce_winner():
    winner_list = []
    max_score = max(client_scores)
    
    for i in range(len(client_scores)):
        if client_scores[i] == max_score:
            winner_list.append(i)
    
    if max_score < 0: # 代表所有player都爆了
        winner_msg = f"There is no winner here! All of you are loser!"
    else:
        if len(winner_list) == 1:
            winner_msg = f"The winner is \"player {winner_list[0]}\" with a score of {max_score} !"
        elif len(winner_list) == 2:
            winner_msg = f"The winner are \"player {winner_list[0]}\" and \"player {winner_list[1]}\", with a score of {max_score} !"
    
    print(winner_msg)  # 在伺服器顯示結果
    
    # 向所有玩家廣播結果
    for client_socket in player_sockets:
        client_socket.send(winner_msg.encode())

# 處理每位玩家的連線
client_scores = []
player_sockets = []
player_cnt = 0
stop_cnt = 0
# 加入遊戲結束旗標
game_over_flag = False  # 全域變數

def handle_client(client_socket, addr, deck, drawn_cards):
    global player_cnt, client_scores, player_sockets, stop_cnt, game_over_flag
    
    print(f"Player {player_cnt} connected, his IP address is: {addr}")
    client_socket.send(str(player_cnt).encode())
    
    client_scores.append(0)
    player_sockets.append(client_socket)
    player_cnt += 1

    # 當玩家加入遊戲，先自動抽一張牌
    initial_card = draw_card(deck, drawn_cards)
    if initial_card is None:
        client_socket.send("No cards left in the deck.".encode())
    else:
        remaining_cards = len(deck) - len(drawn_cards)
        print(f"Player {addr} drew 1 card. Remaining {remaining_cards} cards.")
        client_socket.send(f"drew: {initial_card}, Remaining cards: {remaining_cards}".encode())
    
    while True:
        try:
            # 接收玩家的訊息
            message = client_socket.recv(1024).decode()
            if message == "DRAW":
                card = draw_card(deck, drawn_cards)
                if card is None:
                    client_socket.send("No cards left in the deck.".encode())
                else:
                    remaining_cards = len(deck) - len(drawn_cards)
                    print(f"Player {addr} drew {card}. Remaining {remaining_cards} cards.")
                    # 只发送卡片名称
                    client_socket.send(f"drew2: {card}, Remaining cards: {remaining_cards}".encode())
            elif message == "STOP":
                client_socket.send("stop your turn".encode())
                response = client_socket.recv(1024).decode()
                response = response.split(", ")
                player_id = int(response[0])
                points = int(response[1])
                client_scores[player_id] = points
                stop_cnt += 1
                print(f"Player {player_id} has ended his round with a score of {points}, waitting for other player")
                if stop_cnt >= player_cnt:
                    print("All player is done. Calculating result...")
                    announce_winner()
                    # client_socket.close()
                    return "SHUTDOWN"
                
            elif message == "EXIT":
                client_socket.send("Server shutting down.".encode())
                return "SHUTDOWN"
        except ConnectionResetError:
            print(f"Player {addr} disconnected.")
            return "SHUTDOWN"
    
        

# 伺服器設置
def start_server():
    # 建立撲克牌牌組和已抽取記錄
    deck = initialize_deck()
    drawn_cards = set()

    # 啟動伺服器
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 5555))
    server.listen(5)
    print("Server started, waiting for connections...")

    # 設置終止條件
    stop_flag = threading.Event()

    # 定義接受連線的函數
    def accept_connections():
        while not stop_flag.is_set():
            try:
                client_socket, addr = server.accept()
                threading.Thread(target=handle_client_wrapper, args=(client_socket, addr, deck, drawn_cards)).start()
            except OSError:  # 當伺服器被關閉時會拋出 OSError
                break

    # 包裝 `handle_client`，檢查是否需要關閉伺服器
    def handle_client_wrapper(client_socket, addr, deck, drawn_cards):
        result = handle_client(client_socket, addr, deck, drawn_cards)
        if result == "SHUTDOWN":
            stop_flag.set()

    # 啟動接受連線的執行緒
    accept_thread = threading.Thread(target=accept_connections, daemon=True)
    accept_thread.start()

    # 等待關閉指令
    try:
        stop_flag.wait()
    finally:
        print("Shutting down server...")
        server.close()
        accept_thread.join()

start_server()
