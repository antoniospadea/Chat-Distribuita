# Peer-to-Peer Network with Oracles

This repository contains a Python implementation of a peer-to-peer network with oracles. The network consists of multiple peers communicating with each other through oracles, which act as registration servers.

## Components

- `Oracle_Lez_Cappa.py`: This file contains the implementation of the `Oracle` class, which represents the oracle server. The oracle listens for registration requests from peers and maintains a list of registered peers.
- `Peer_Lez_Cappa.py`: This file contains the implementation of the `Peer` class, which represents a peer in the network. Each peer is assigned a random IP address and port number and registers with the oracles to join the network.
- `main.py`: This file serves as the entry point of the program. It initializes three instances of the `Oracle` class and one instance of the `Peer` class to test the functionality of the network.

## Requirements

- Python 3.x

## How to Run

1. Clone this repository to your local machine.
2. Open a terminal and navigate to the project directory.
3. Run the following command to start the program:
4. Follow the on-screen instructions to provide the required information such as nickname for the peer.
5. The program will initialize the oracles and the peer, and the peer will attempt to register with the oracles.
6. Once the registration is successful, the peer will be part of the peer-to-peer network and can communicate with other peers through the oracles.

## Customization

- The oracles are initialized with the following information:
- First oracle: IP address - 'localhost', Port - 9999, Nickname - 'primo_oracolo'
- Second oracle: IP address - 'localhost', Port - 9998, Nickname - 'secondo_oracolo'
- Third oracle: IP address - 'localhost', Port - 9997, Nickname - 'terzo_oracolo'
You can modify these details in the `main.py` file according to your requirements.

- The peer is assigned a random IP address and port number within the range of 1000 to 5000. You can modify this range in the `Peer` class in `Peer_Lez_Cappa.py` if needed.

## Contributing

Contributions to this project are welcome. If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
