# Copyright 2020 by Chris Feyerchak and distributed under the GPL v2 license; see 'license.txt'.

import sys
from playeragenthic import HumanInteractiveConsolePlayerAgent
import zmq
from playeragentproxyzmq import AgentHalf as PlayerAgentProxyForZmq


def main(argv):
    server_address = argv[1] if len(argv) > 1 else 'localhost:5555'
    zmq_context = zmq.Context()
    agent = HumanInteractiveConsolePlayerAgent(argv[2] if len(argv) > 2 else input('Name: '))
    proxy = PlayerAgentProxyForZmq(agent, zmq_context, server_address)
    proxy.run()

if __name__ == '__main__':
    main(sys.argv)
