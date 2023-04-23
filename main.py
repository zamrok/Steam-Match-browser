#%%
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget, QHBoxLayout,
                             QListWidget, QStackedWidget, QComboBox, QGroupBox, QGridLayout, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette
# import game_keys

import requests



def get_user_stats(api_key, steam_id, game_key):
    if not game_key:
        return None

    url = f"http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v2/?appid={game_key}&key={api_key}&steamid={steam_id}"
    print(url)
    response = requests.get(url)

    if response.status_code == 200:
        try:
            return response.json()
        except ValueError as e:
            print(f"Error decoding JSON: {e}")
    else:
        print(f"Error fetching user stats: {response.status_code}\n{response.text}")

    return None

game_keys = {"Counter-Strike: Global Offensive":730}

def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Steam Match Browser")
    window.setMinimumSize(800, 600)

    # Set background color
    palette = QPalette()
    palette.setColor(QPalette.Background, QColor(240, 240, 240))
    window.setPalette(palette)

    # Create layout and widgets
    central_widget = QWidget()
    main_layout = QVBoxLayout()
    header_layout = QHBoxLayout()
    content_layout = QHBoxLayout()
    game_selection = QComboBox()
    matches_list = QListWidget()
    match_details = QStackedWidget()

    # Set layout for central widget
    central_widget.setLayout(main_layout)
    window.setCentralWidget(central_widget)

    # Configure game selection
    game_selection.addItem("Select a game")
    game_selection.addItem("Counter-Strike: Global Offensive")
    game_selection.addItem("Game 2")
    
    game_selection.currentIndexChanged.connect(
        lambda index: get_user_stats(os.getenv("STEAM_API_KEY"), os.getenv("STEAM_ID"), game_keys.get(game_selection.itemText(index), '')) if index > 0 else None
    )

    # Add layouts to the main layout
    main_layout.addLayout(header_layout)
    main_layout.addLayout(content_layout)

    # Configure header layout
    app_name = QLabel("Steam Match Browser")
    app_name.setFont(QFont("Arial", 24))
    header_layout.addWidget(app_name, alignment=Qt.AlignCenter)
    header_layout.addWidget(game_selection)

    # Configure content layout
    matches_groupbox = QGroupBox("Match History")
    matches_layout = QGridLayout()
    matches_groupbox.setLayout(matches_layout)
    matches_layout.addWidget(matches_list, 0, 0, 1, 1)

    match_details_groupbox = QGroupBox("Match Details")
    match_details_layout = QGridLayout()
    match_details_groupbox.setLayout(match_details_layout)
    match_details_layout.addWidget(match_details, 0, 0, 1, 1)

    content_layout.addWidget(matches_groupbox)
    content_layout.addWidget(match_details_groupbox)

    # Show the window
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

# %%
