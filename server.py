from abc import ABC, abstractmethod
from board import Board
from playeragenthic import HumanInteractiveConsolePlayerAgent


class PlayerAgentFactoryInterface(ABC):

    @abstractmethod
    def make_player_agent(self):
        pass

class HumanInteractiveConsolePlayerAgentFactory(PlayerAgentFactoryInterface):

    def make_player_agent(self):
        return HumanInteractiveConsolePlayerAgent()

class Game:

    def __init__(self, player_x, player_o):
        self.player_x = player_x
        self.player_o = player_o

    def play(self):
        mark = 'x'
        current_player = self.player_x
        other_player = self.player_o

        print(f'{current_player.request_player_name()} ({current_player.request_agent_description()}) vs {other_player.request_player_name()} ({other_player.request_agent_description()})')
   
        board = Board()
        #board.print()
        #print('')

        is_game_won = False
    
        while not board.is_full():
            (r, c) = current_player.request_move()
            board.set(r, c, mark)
            other_player.notify_other_players_move(r, c)
            #board.print()
            winner = board.find_winner()
            if winner:
                print(f'{current_player.request_player_name()} ({current_player.request_agent_description()}) defeated {other_player.request_player_name()} ({other_player.request_agent_description()})')
                current_player.notify_game_over('win')
                other_player.notify_game_over('lose')
                is_game_won = True
                break
    
            (current_player, other_player) = (other_player, current_player)
            mark = 'o' if mark == 'x' else 'x'

        if not is_game_won:
            current_player.notify_game_over('draw')
            other_player.notify_game_over('draw')


def main():

    player_factory = HumanInteractiveConsolePlayerAgentFactory()

    while True:
    
        player_1 = player_factory.make_player_agent()
        player_2 = player_factory.make_player_agent()

        game = Game(player_1, player_2)
        game.play()


main()
