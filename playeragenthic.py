from abc import ABC, abstractmethod
from board import Board
from playeragentinterface import PlayerAgentInterface


class HumanInteractiveConsolePlayerAgent(PlayerAgentInterface):

    def __init__(self):
        self.board = Board()
        self.name = input('Name: ') 

    def request_player_name(self):
        return self.name

    def request_agent_description(self):
        return f'{self.__class__.__name__ } by Chris Feyerchak'

    def notify_other_players_move(self, r, c):
        print(f'{self.name}: I see the other player marked ({r},{c}):')
        self.board.set(r, c, 'o')
        self.board.print()

    def request_move(self):
        print(f'{self.name}:')
        self.board.print()
        r = int(input('Row: '))
        c = int(input('Col: '))
        self.board.set(r, c, 'x')
        self.board.print()
        return (int(r),int(c))

    def notify_game_over(self, outcome):
        print(f'{self.name}: I {outcome}!')

