# Copyright 2020 by Chris Feyerchak and distributed under the GPL v2 license; see 'license.txt'.

import sys
import zmq
from playeragentproxyzmq import ServerHalfFactory as PlayerAgentProxyForZmqFactory
import server

def main(argv):
    bind_address = argv[1] if len(argv) > 1 else '0.0.0.0:5555'
    zmq_context = zmq.Context()
    player_factory = PlayerAgentProxyForZmqFactory(zmq_context, bind_address)
    server.run(player_factory)


if __name__ == '__main__':
    main(sys.argv)
