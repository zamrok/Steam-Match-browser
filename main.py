#%%
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget, QHBoxLayout,
                             QListWidget, QStackedWidget, QComboBox, QGroupBox, QGridLayout, QGraphicsDropShadowEffect,QTableWidget, QTableWidgetItem, 
                             QHeaderView, QSplitter, QInputDialog, QListWidgetItem, QProgressBar)
from PyQt5.QtWidgets import QTabWidget, QLineEdit, QListWidgetItem
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QByteArray, QBuffer
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap, QImage, QIcon
from stats import PlayerStats
import asyncio
import aiohttp
import httpx
import requests
from PyQt5.QtCore import QRunnable, QThreadPool
import logging

logging.basicConfig(level=logging.DEBUG)

player_stats = PlayerStats()
friend_stats = PlayerStats()
# Now you can use the player_stats object for your application logic
game_keys = {"Counter-Strike: Global Offensive":730}

current_steam_id = os.getenv("STEAM_ID")
friend_steam_id = None

class MainWindow(QMainWindow):
    friends_list:QListWidget
    friends_player_stats:dict[str,PlayerStats]
    
    def __init__(self):
        super().__init__()
        self.friends_player_stats = {}
        # Set background color
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(240, 240, 240))
        self.setPalette(palette)
        
        # Create layout and widgets
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        header_layout = QHBoxLayout()
        content_splitter = QSplitter(Qt.Horizontal)
        game_selection = QComboBox()
        stat_group_selection = QComboBox()
        matches_list = QListWidget()
        # match_details = QStackedWidget()
        self.friends_list = QListWidget()
        
        # Create a tab widget
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        # Create a widget for the first tab (Steam Match Browser)
        steam_match_browser_widget = QWidget()
        steam_match_browser_layout = QVBoxLayout()
        steam_match_browser_widget.setLayout(steam_match_browser_layout)


        # Add the content splitter to the Steam Match Browser tab
        content_splitter = QSplitter(Qt.Horizontal)
        steam_match_browser_layout.addWidget(content_splitter)
        tab_widget.addTab(steam_match_browser_widget, "Stats")

        # Create a widget for the second tab (Friends)
        friends_widget = QWidget()
        friends_layout = QVBoxLayout()
        friends_widget.setLayout(friends_layout)

        # Add a QLineEdit for searching friends
        search_friends_edit = QLineEdit()
        search_friends_edit.setPlaceholderText("Search friends...")
        friends_layout.addWidget(search_friends_edit)

        # Add a QListWidget for displaying friends
        self.friends_list = QListWidget()
        friends_layout.addWidget(self.friends_list)

        # Add the Friends tab to the tab widget
        tab_widget.addTab(friends_widget, "Friends")


        # Set layout for central widget
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        # Configure game selection
        game_selection.addItem("Select a game")
        game_selection.addItem("Counter-Strike: Global Offensive")
        game_selection.addItem("Game 2")
        
        
        stat_group_selection.addItem("All Stats")
        stat_group_selection.addItem("Last Match Stats")
        stat_group_selection.addItem("Other Stats")
        
        progress_bar = QProgressBar()
        progress_bar.setObjectName("progress_bar")
        friends_layout.addWidget(progress_bar)
        progress_bar.hide()
        
        # Add layouts to the main layout
        main_layout.addLayout(header_layout)

        # Configure header layout
        app_name = QLabel("Steam Match Browser")
        app_name.setFont(QFont("Arial", 24))
        header_layout.addWidget(app_name, alignment=Qt.AlignCenter)
        header_layout.addWidget(game_selection)
        header_layout.addWidget(stat_group_selection)

        change_steam_id_button = QPushButton("Change Steam ID")
        header_layout.addWidget(change_steam_id_button)

        clear_button = QPushButton("Clear")
        header_layout.addWidget(clear_button)
        
        # Configure content layout
        matches_groupbox = QGroupBox("Match History")
        matches_layout = QGridLayout()
        matches_groupbox.setLayout(matches_layout)
        matches_layout.addWidget(matches_list, 0, 0, 1, 1)
        
        stats_groupbox = QGroupBox("Player Stats")
        stats_layout = QGridLayout()
        stats_groupbox.setLayout(stats_layout)
        stats_table = QTableWidget()
        stats_table.setColumnCount(3)
        stats_table.setHorizontalHeaderLabels(["Stat", "Your Value", "Friend's Value"])
        # Stats table search box
        search_box = QLineEdit()
        search_box.setPlaceholderText("Search...")
    
        
        stats_table.setSortingEnabled(True)
        # Set resize modes for columns and rows
        stats_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        stats_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        stats_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        stats_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # Adjust the row height
        stats_table.verticalHeader().setDefaultSectionSize(24)
        # Set alternating row colors
        stats_table.setAlternatingRowColors(True)
        stats_layout.addWidget(stats_table, 0, 0, 1, 1)
        stats_layout.addWidget(search_box, 1, 0, 1, 1)

        content_splitter.addWidget(matches_groupbox)
        # content_splitter.addWidget(match_details_groupbox)
        content_splitter.addWidget(stats_groupbox)
        

                
        # Connect the search box's textChanged signal to a slot function
        search_box.textChanged.connect(lambda x: filter_table(x, stats_table))
        search_friends_edit.textChanged.connect(lambda x: filter_table(x, self.friends_list))
        
        # Apply a custom style sheet to the table
        stats_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d6d6d6;
                selection-background-color: #87bdd8;
                alternate-background-color: #f7f7f7;
            }
            QHeaderView::section {
                background-color: #ededed;
                padding: 4px;
                border-style: none;
                border-bottom: 1px solid #d6d6d6;
                font-weight: bold;
            }
        """)
            # Style QComboBox
        selection_style = """
            QComboBox {
                background-color: #f0f0f0;
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                padding: 5px;
            }

            QComboBox::drop-down {
                border: none;
            }

            QComboBox::down-arrow {
                width: 16px;
                height: 16px;
                image: url(/path/to/your/arrow-image.png);
                background-color: #f0f0f0;
                image: url(./resources/down-arrow.png);
            }
        """
        # Style QGroupBox
        groupbox_style = """
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 20px;
                padding: 10px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding-left: 10px;
            }
        """
        
        game_selection.setStyleSheet(selection_style)
        stat_group_selection.setStyleSheet(selection_style)
        matches_groupbox.setStyleSheet(groupbox_style)
        stats_groupbox.setStyleSheet(groupbox_style)
        
        
        def clear_stats_table():
            stats_table.clearContents()
            stats_table.setRowCount(0)
        # Clear stats table
        def on_clear_button_clicked():
            clear_stats_table()
        # Change steam ID
        def on_change_steam_id_button_clicked():
            global current_steam_id
            steam_id, ok = QInputDialog.getText(self, "Change Steam ID", "Enter new Steam ID:")
            if ok and steam_id:
                current_steam_id = steam_id
                
        # Fill stats table when changing games
        def on_game_selection_changed(index):
            if index > 0:
                fetch_and_update_player_stats()
        # Fill stats table function
        def fill_stats_table(player_stats:PlayerStats, friend_stats:PlayerStats=None, group=None):
            stats_table.setRowCount(0)
            friend_stats_to_fill:dict = None
            
            stats_to_fill:dict = player_stats.all_stats
            if friend_stats:
                friend_stats_to_fill = friend_stats.all_stats
            # Stats group
            if group == "last_match":
                stats_to_fill = player_stats.last_match_stats
                if friend_stats:
                    friend_stats_to_fill = friend_stats.last_match_stats
            # Stats group
            if group == "other":
                stats_to_fill = player_stats.other_stats
                if friend_stats:
                    friend_stats_to_fill = friend_stats.other_stats
            for stat, value in stats_to_fill.items():
                row = stats_table.rowCount()
                stats_table.insertRow(row)
                stats_table.setItem(row, 0, QTableWidgetItem(str(stat)))
                stats_table.setItem(row, 1, QTableWidgetItem(str(value)))
                
                if friend_stats:
                    fr_value = friend_stats_to_fill.get(stat, "")
                    stats_table.setItem(row, 2, QTableWidgetItem(str(fr_value)))
                    
        # Load the friend player stats when a friend is double clicked
        def on_friend_double_clicked(item):
            global friend_steam_id
            friend_steam_id = item.data(Qt.UserRole)
            print("Friend Steam ID: {}".format(friend_steam_id))
            if friend_steam_id:
                fetch_and_update_player_stats()

        def update_stats_table():
            group = stat_group_selection.currentText()
            if group == "All Stats":
                fill_stats_table(player_stats, friend_stats)
            elif group == "Last Match Stats":
                fill_stats_table(player_stats, friend_stats, group="last_match")
            elif group == "Other Stats":
                fill_stats_table(player_stats, friend_stats, group="other")

        def fetch_and_update_player_stats():
            global current_steam_id, friend_steam_id
            global player_stats, friend_stats
            friend_stats_json = None
            player_stats_json = None
            
            if player_stats.steamID != current_steam_id:
                player_stats_json = fetch_user_stats(
                    os.getenv("STEAM_API_KEY"), current_steam_id, game_keys.get("Counter-Strike: Global Offensive", "")
                )
                player_stats.from_json(player_stats_json)

            if friend_steam_id:
                if(friend_stats_temp := self.friends_player_stats.get(friend_steam_id, None)):
                    friend_stats = friend_stats_temp
        
                else:
                    friend_stats_json = fetch_user_stats(
                        os.getenv("STEAM_API_KEY"), friend_steam_id, game_keys.get("Counter-Strike: Global Offensive", "")
                    )
                    
                    if friend_stats_json:
                        friend_stats = PlayerStats()
                        friend_stats.from_json(friend_stats_json)
            
            if player_stats.all_stats:
                fill_stats_table(player_stats, friend_stats)
        
        # Set actions that are defined in __init__
        stat_group_selection.currentIndexChanged.connect(update_stats_table)
        game_selection.currentIndexChanged.connect(on_game_selection_changed)
        self.friends_list.itemDoubleClicked.connect(on_friend_double_clicked)
        change_steam_id_button.clicked.connect(on_change_steam_id_button_clicked)
        clear_button.clicked.connect(on_clear_button_clicked)
        
        # Add a QPushButton for fetching friends list
        self.fetch_friends_button = QPushButton("Fetch friends")
        self.fetch_friends_button.clicked.connect(lambda: self.populate_friends_list_with_current_steam_id(os.getenv("STEAM_API_KEY"), current_steam_id, game_keys.get("Counter-Strike: Global Offensive", ""), progress_bar))
        friends_layout.addWidget(self.fetch_friends_button)
        self.worker = None

    def populate_friends_list_with_current_steam_id(self, api_key, steam_id, app_id, progress_bar:QProgressBar):
        self.friends_list.setEnabled(False)
        progress_bar.show()
        self.worker = FriendsListWorker(api_key, steam_id, app_id)
        self.worker.progress.connect(progress_bar.setValue)
        self.worker.finished.connect(lambda friends_data: self.update_friends_list_widget(friends_data))
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(progress_bar.hide)
        self.worker.start()

    def update_friends_list_widget(self, friends_data):
        self.friends_list.clear()
        for pixmap, friend_name, friend_steam_id, friend_stat in friends_data:  
            friend_item = QListWidgetItem(QIcon(pixmap), friend_name)
            friend_item.setData(Qt.UserRole, friend_steam_id)
            self.friends_list.addItem(friend_item)
            self.friends_player_stats.update({friend_steam_id: friend_stat})
            
        self.friends_list.setEnabled(True)


# Friend list worker for async fetching 
class FriendsListWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)

    def __init__(self, api_key, steam_id, app_id):
        super().__init__()
        self.api_key = api_key
        self.steam_id = steam_id
        self.app_id = app_id

    async def fetch_avatar_data(self, avatar_url):
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as response:
                return await response.read()

    async def fetch_friends_and_stats(self):
        friends = await fetch_friends_list_async(self.api_key, self.steam_id)
        result = []
        pixmap=None
        
        for index, friend in enumerate(friends):
            friend_steam_id = friend.get("steamid", "")
            friend_name = friend.get("personaname", "")
            friend_avatar_url = friend.get("avatar", "")
            
            try:
                avatar_data = await self.fetch_avatar_data(friend_avatar_url)
                buffer = QBuffer()
                buffer.open(QBuffer.ReadWrite)
                buffer.write(avatar_data)
                buffer.seek(0)
                image = QImage()
                image.loadFromData(buffer.readAll())
                pixmap = QPixmap.fromImage(image)
            except aiohttp.client.InvalidURL:
                logging.error(f"Invalid URL: {friend_avatar_url}")

            friend_stats = await fetch_player_stats_async(self.api_key, friend_steam_id, self.app_id)
            if "Error fetching user stats" in friend_stats:
                self.progress.emit((index + 1) * 100 // len(friends))
                continue
            
            logging.info("Found stats for " + friend_name)
            friend_name += " (Open Profile)"
            
            friend_player_stats = PlayerStats()
            friend_player_stats.from_json(friend_stats)
        
            result.append((pixmap, friend_name, friend_steam_id, friend_player_stats)) #pixmap, friend_name, friend_steam_id, 
            self.progress.emit((index + 1) * 100 // len(friends))
            
        return result

    def run(self):
        result = asyncio.run(self.fetch_friends_and_stats())
        self.finished.emit(result)
        

def fetch_user_stats(api_key, steam_id, game_key):
    if not game_key:
        return None

    url = f"http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v2/?appid={game_key}&key={api_key}&steamid={steam_id}"
    print(url)
    response = requests.get(url)
    print(response.content)
    
    if response.status_code == 200:
        try:
            return response.text
        except ValueError as e:
            print(f"Error decoding JSON: {e}")
    else:
        print(f"Error fetching user stats: {response.status_code}\n{response.text}")

    return None

async def fetch_player_stats_async(api_key, steam_id, game_key):
    async with aiohttp.ClientSession() as session:
        url = f"http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v2/?appid={game_key}&key={api_key}&steamid={steam_id}"
        logging.error(f"Fetching player stats URL: {url}")
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                return "Error fetching user stats"

async def fetch_friends_list_async(api_key, steam_id):
    url = f"http://api.steampowered.com/ISteamUser/GetFriendList/v1/?key={api_key}&steamid={steam_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            friends_steam_ids = [friend['steamid'] for friend in data['friendslist']['friends']]

    summaries_url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={api_key}&steamids={','.join(friends_steam_ids)}"
    async with aiohttp.ClientSession() as session:
        async with session.get(summaries_url) as response:
            data = await response.json()
            friends = data['response']['players']
    return friends

async def fetch_next_match_sharing_code():
    url = f"https://api.steampowered.com/ICSGOPlayers_730/GetNextMatchSharingCode/v1?key=XXX&steamid=765XXX&steamidkey={steam_id}&knowncode=CSGO-ZT42K-Jxxxx-Kxxxx-5xxxx-Oixxx"

# async def fetch_user_summary_async(api_key, steam_id):
#     url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={api_key}&steamids={steam_id}"
#     async with httpx.AsyncClient() as client:
#         response = await client.get(url)
#         data = response.json()
#         if "response" in data and "players" in data["response"] and len(data["response"]["players"]) > 0:
#             return data["response"]["players"][0]
#         else:
#             return {}
        
def filter_attributes(attributes, prefix):
    return [attr for attr in attributes if attr.startswith(prefix)]

# Slot function to filter the table based on search input
def filter_table(text, table: QTableWidget):
    for i in range(table.rowCount()):
        match = False
        for j in range(table.columnCount()):
            item = table.item(i, j)
            if item and text.lower() in item.text().lower():
                match = True
                break
        table.setRowHidden(i, not match)


def main():
    app = QApplication(sys.argv)
    app_name = QLabel("Steam Match Browser")
    app_name.setFont(QFont("Arial", 24))

    window = MainWindow()
    window.setWindowTitle("Steam Match Browser")
    window.setMinimumSize(800, 600)

    app.setStyleSheet("""
    QWidget {
        font-size: 14px;
    }

    QLabel {
        font-size: 14px;
    }

    QPushButton {
        background-color: #3498db;
        border: 1px solid #2980b9;
        color: white;
        padding: 5px 15px;
        border-radius: 4px;
    }

    QPushButton:hover {
        background-color: #2980b9;
    }


    QTableWidget {
        border: 1px solid #bdc3c7;
        border-radius: 5px;
    }

    QHeaderView::section {
        background-color: #bdc3c7;
        padding: 5px;
    }

    QSplitter::handle {
        background-color: #bdc3c7;
    }
""")
    

    
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
# %%
