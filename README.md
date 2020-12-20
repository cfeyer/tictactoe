Description: Program(s) for playing the game of tic-tac-toe, and reusable
modules for creating other programs that deal with tic-tac-toe.

Use Case 1: Enable two players to play tic-tac-toe against one another
over a network. Each user runs a console user interface agent program.
A server program is also run on a computer that is accessible over the
network by both user agents. The agents and server communicate using
ZeroMQ messaging over TCP.

If all users and the server are collocated on the same machine, the
following procedure will work. Otherwise, substitute the server's
network address in place of "localhost".

1) On server: python serverzmq.py localhost:5555
2) User 1: python playeragenthiczmq.py localhost:5555 Alice
3) User 2: python playeragenthiczmq.py localhost:5555 Bob

The topmost row of the board is row 0. The leftmost column of the
board is column 0.

Use Case 2: A programmer can implement an autonomous agent program
in Python to play the game in lieu of a human player by implementing
a subclass of playeragentinterface.PlayerAgentInterface, instantiating
an object of it, and attaching a playeragentproxyzmq.AgentHalf object to it.

Use Case 3: A programmer can implement an autonomous agent program
in an arbitrary programming language by implementing the ZeroMQ/JSON
message passing protocol presented within playeragentproxyzmq.
