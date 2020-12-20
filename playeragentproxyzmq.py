import zmq
import json
from playeragentinterface import PlayerAgentInterface, PlayerAgentFactoryInterface


def serialize(obj):
    return bytearray(json.dumps(obj), 'utf-8')

def deserialize(somebytes):
    barray = bytearray(somebytes)
    return json.loads(barray.decode(encoding='utf-8'))

class ServerHalf(PlayerAgentInterface):

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

class ServerHalfFactory(PlayerAgentFactoryInterface):

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
        return ServerHalf(agent_socket)

class AgentHalf(PlayerAgentInterface):

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
