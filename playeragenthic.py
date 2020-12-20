from abc import ABC, abstractmethod
from board import Board
from playeragentinterface import PlayerAgentInterface
import zmq
import json

def serialize(obj):
    return bytearray(json.dumps(obj), 'utf-8')

def deserialize(somebytes):
    barray = bytearray(somebytes)
    return json.loads(barray.decode(encoding='utf-8'))


class PlayerAgentProxyForZmq(PlayerAgentInterface):

    def __init__(self, agent, zmq_context, server_host, server_port):
        self.agent = agent
        self.zmq_context = zmq_context
        self.server_host = server_host
        self.server_port = server_port
        self.agent_rpc_socket = None

    def run(self):
        join_socket = self.zmq_context.socket(zmq.REQ)
        join_address = f'tcp://{self.server_host}:{self.server_port}'
        print(f'Agent connecting to {join_address}...')
        with join_socket.connect(join_address):
            print('Agent connected.')
            join_socket.send(b'')
            response = join_socket.recv()
            print(f'Agent received join response: {response}')
        response_obj = deserialize(response)
        agent_port = response_obj['agent_port']

        self.agent_rpc_socket = self.zmq_context.socket(zmq.REP)
        agent_rpc_address = f'tcp://{self.server_host}:{agent_port}'
        print(f'Agent conecting to {agent_rpc_address}...')
        with self.agent_rpc_socket.connect(agent_rpc_address):
            print('Agent connected.')
            while True:
                request = self.agent_rpc_socket.recv()
                print(f'Received: {request}')
                request_obj = deserialize(request)
                request_name = request_obj['request']
                if request_name == 'request_player_name':
                    self.request_player_name()
                elif request_name == 'request_agent_description':
                    self.request_agent_description()
                elif request_name == 'notify_other_players_move':
                    self.notify_other_players_move(int(request_obj['row']), int(request_obj['column']))
                elif request_name == 'request_move':
                    self.request_move()
                elif request_name == 'notify_game_over':
                    self.notify_game_over(request_obj['outcome'])
                    break
                else:
                    self.agent_rpc_socket.send(b'Not implemented')
        self.agent_rpc_socket = None

    def request_player_name(self):
        self.agent_rpc_socket.send(serialize({'player_name': self.agent.request_player_name()}))

    def request_agent_description(self):
        self.agent_rpc_socket.send(serialize({'agent_description': self.agent.request_agent_description()}))

    def notify_other_players_move(self, r, c):
        self.agent.notify_other_players_move(r, c)
        self.agent_rpc_socket.send(b'')

    def request_move(self):
        (row, column) = self.agent.request_move()
        self.agent_rpc_socket.send(serialize({'row': row, 'column': column}))

    def notify_game_over(self, outcome):
        self.agent.notify_game_over(outcome)
        self.agent_rpc_socket.send(b'')

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


def main():
    zmq_context = zmq.Context()
    agent = HumanInteractiveConsolePlayerAgent()
    proxy = PlayerAgentProxyForZmq(agent, zmq_context, 'localhost', '5555')
    proxy.run()

if __name__ == '__main__':
    main()
