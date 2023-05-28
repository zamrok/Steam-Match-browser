# Importing Required Libraries
#%%
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem
import sys
import requests
import json

# Steam API Key
steam_api_key = 'YOUR_STEAM_API_KEY'

# Steam API URL
steam_api_url = 'https://api.steampowered.com/'

# Function to get match history

def get_match_history(steam_id):
    # API URL for getting match history
    url = steam_api_url + 'IDOTA2Match_570/GetMatchHistory/V001/?key=' + steam_api_key + '&account_id=' + steam_id
    # Sending GET request to the API
    response = requests.get(url)
    # Converting the response to JSON format
    data = json.loads(response.text)
    # Returning the match history
    return data['result']['matches']

# UI Class

class UI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Setting the window title
        self.setWindowTitle('Steam Match Browser')
        # Setting the window size
        self.setGeometry(100, 100, 800, 600)
        # Creating the layout
        layout = QVBoxLayout()
        # Creating the Steam ID label
        steam_id_label = QLabel('Steam ID:')
        # Creating the Steam ID input field
        self.steam_id_input = QLineEdit()
        # Creating the Game label
        game_label = QLabel('Game:')
        # Creating the Game dropdown
        self.game_dropdown = QComboBox()
        self.game_dropdown.addItem('Dota 2')
        self.game_dropdown.addItem('CS:GO')
        # Creating the Search button
        search_button = QPushButton('Search')
        search_button.clicked.connect(self.search)
        # Creating the table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Match ID', 'Game Mode', 'Duration', 'Result'])
        # Adding the widgets to the layout
        layout.addWidget(steam_id_label)
        layout.addWidget(self.steam_id_input)
        layout.addWidget(game_label)
        layout.addWidget(self.game_dropdown)
        layout.addWidget(search_button)
        layout.addWidget(self.table)
        # Setting the layout
        self.setLayout(layout)

    def search(self):
        # Clearing the table
        self.table.setRowCount(0)
        # Getting the Steam ID
        steam_id = self.steam_id_input.text()
        # Getting the game
        game = self.game_dropdown.currentText()
        # Getting the match history
        match_history = get_match_history(steam_id)
        # Filtering the match history by game
        filtered_match_history = [match for match in match_history if match['game_mode'] == game]
        # Populating the table
        for match in filtered_match_history:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(str(match['match_id'])))
            self.table.setItem(row_position, 1, QTableWidgetItem(str(match['game_mode'])))
            self.table.setItem(row_position, 2, QTableWidgetItem(str(match['duration'])))
            self.table.setItem(row_position, 3, QTableWidgetItem(str(match['radiant_win'])))

ui = UI()
# %%
