from playeragenthic import HumanInteractiveConsolePlayerAgent
import zmq
from playeragentproxyzmq import AgentHalf as PlayerAgentProxyForZmq


def main():
    zmq_context = zmq.Context()
    agent = HumanInteractiveConsolePlayerAgent(input('Name: '))
    proxy = PlayerAgentProxyForZmq(agent, zmq_context, 'localhost', '5555')
    proxy.run()

if __name__ == '__main__':
    main()
