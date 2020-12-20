import zmq
from playeragentproxyzmq import ServerHalfFactory as PlayerAgentProxyForZmqFactory
import server

def main():

    zmq_context = zmq.Context()
    player_factory = PlayerAgentProxyForZmqFactory(zmq_context, '0.0.0.0', '5555')
    server.run(player_factory)


if __name__ == '__main__':
    main()
