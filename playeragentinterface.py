from abc import ABC, abstractmethod

class PlayerAgentInterface(ABC):

    @abstractmethod
    def request_player_name(self):
        pass

    @abstractmethod
    def request_agent_description(self):
        pass

    @abstractmethod
    def notify_other_players_move(self, r, c):
        pass

    @abstractmethod
    def request_move(self):
        pass

    @abstractmethod
    def notify_game_over(self, outcome):
        pass

