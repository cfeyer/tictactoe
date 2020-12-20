from abc import ABC, abstractmethod
from board import Board
from playeragenthic import HumanInteractiveConsolePlayerAgent
import json
import zmq

def serialize(obj):
    return bytearray(json.dumps(obj), 'utf-8')

def deserialize(somebytes):
    barray = bytearray(somebytes)
    return json.loads(barray.decode(encoding='utf-8'))

class PlayerAgentProxyForZmq(ABC):

    def __init__(self, agent_rpc_socket):
        self.agent_rpc_socket = agent_rpc_socket

    def request_player_name(self):
        request = {'request': 'request_player_name'}
        self.agent_rpc_socket.send(serialize(request))
        response = deserialize(self.agent_rpc_socket.recv())
        return response['player_name']

    def request_agent_description(self):
        self.agent_rpc_socket.send(serialize({'request': 'request_agent_description'}))
        return deserialize(self.agent_rpc_socket.recv())['agent_description']

    def notify_other_players_move(self, r, c):
        self.agent_rpc_socket.send(serialize({'request': 'notify_other_players_move', 'row': str(r), 'column': str(c)}))
        self.agent_rpc_socket.recv()

    def request_move(self):
        self.agent_rpc_socket.send(serialize({'request': 'request_move'}))
        response_obj = deserialize(self.agent_rpc_socket.recv())
        return (int(response_obj['row']), int(response_obj['column']))

    def notify_game_over(self, outcome):
        self.agent_rpc_socket.send(serialize({'request': 'notify_game_over', 'outcome': outcome}))
        self.agent_rpc_socket.recv()


class PlayerAgentFactoryInterface(ABC):

    @abstractmethod
    def make_player_agent(self):
        pass

class HumanInteractiveConsolePlayerAgentFactory(PlayerAgentFactoryInterface):

    def make_player_agent(self):
        return HumanInteractiveConsolePlayerAgent()

class PlayerAgentProxyForZmqFactory(PlayerAgentFactoryInterface):

    def __init__(self, zmq_context, bind_interface, bind_tcp_port):
        self.zmq_context = zmq_context
        self.bind_interface = bind_interface
        self.bind_tcp_port = bind_tcp_port

        address = f'tcp://{self.bind_interface}:{self.bind_tcp_port}'
        print(f'Server binding to {address}...')
        self.well_known_socket = self.zmq_context.socket(zmq.REP)
        self.well_known_socket.bind(address)


    def make_player_agent(self):
        print('Server waiting for agent to connect...')
        request = self.well_known_socket.recv()
        print('Agent connecting. Establishing agent-specific port...')
        agent_socket = self.zmq_context.socket(zmq.REQ)
        agent_socket.bind(f'tcp://{self.bind_interface}:*')
        last_endpoint = agent_socket.getsockopt_string(zmq.LAST_ENDPOINT)
        print(f'Last endpoint: {last_endpoint}')
        agent_port = str(last_endpoint).split(':')[-1]
        response = {'agent_port': str(agent_port)}
        print(f'Redirecting agent to port {agent_port}')
        self.well_known_socket.send(serialize(response))
        return PlayerAgentProxyForZmq(agent_socket)

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

    #player_factory = HumanInteractiveConsolePlayerAgentFactory()
    zmq_context = zmq.Context()
    player_factory = PlayerAgentProxyForZmqFactory(zmq_context, '0.0.0.0', '5555')

    while True:
    
        player_1 = player_factory.make_player_agent()
        player_2 = player_factory.make_player_agent()

        game = Game(player_1, player_2)
        game.play()


if __name__ == '__main__':
    main()
