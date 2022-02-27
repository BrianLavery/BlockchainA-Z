# Module 2 - Create a Cryptocurrency

# Importing libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# PART 1: Creating blockchain
class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = [] # List of TXNs before added to a block
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set() # These are a set as no order to nodes

    # Create a block
    def create_block(self, proof, previous_hash):
        block = { 'index': len(self.chain) + 1,
                'timestamp': str(datetime.datetime.now()),
                'proof': proof,
                'previous_hash': previous_hash,
                'transactions': self.transactions }
        self.transactions = [] # Empty list of TXNs from those added to block
        self.chain.append(block)
        return block

    # Returns the last block on the chain
    def get_previous_block(self):
        return self.chain[-1]

    # Solves the proof of work challenge
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    # Returns a hash of any block passed to it
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    # Checks that the blockchain is valid
    def is_chain_valid(self, chain):
        previous_block = chain[0] # Start off with first block
        block_index = 1

        while block_index < len(chain):
            block = chain[block_index]

            if block['previous_hash'] != self.hash(previous_block):
                return False

            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False

            previous_block = block
            block_index += 1

        return True

    # Adds a transaction to the list of transactions to be added to the block
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({ 'sender': sender,
                                   'receiver': receiver,
                                   'amount': amount })
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1 # We return index of new block that will take these TXNs

    # Adds a node
    def add_node(self, address):
        parsed_url = urlparse(address) # We parse address of the node
        self.nodes.add(parsed_url.netloc)

    # Function to check for longest chain in network and replace existing chain if find a longer chanin in network (each node runs this)
    def replace_chain(self):
        network = self.nodes # Network is entire set of nodes globally
        longest_chain = None # We don't know what the longest chain in network is yet
        max_length = len(self.chain) # Initialise as length of blockchain in current chain
        for node in network:
            response = requests.get(f'http://{node}/get_chain') # We use the imported requests library
            if response.status_code == 200: # Check request worked
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain): # Check if this chain is longest so far and it is a valid chain
                    max_length = length # Update max_length variable
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False # This will only be returned if no longest_chain

# PART 2: Mining blockchain

# Creating a Web App
app = Flask(__name__)

# Creating an address for node on Port 5000
# This node provides the currency that is generated as part of the mining process
node_address = str(uuid4()).replace('-', '')
node_owner = 'Brian'

# Creating a Blockchain (instance)
blockchain = Blockchain()

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block() # Get last block of chain
    previous_proof = previous_block['proof'] # Now get proof
    proof = blockchain.proof_of_work(previous_proof) # This gives proof of future/ new block
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction( sender = node_address, receiver = node_owner, amount = 1 )
    block = blockchain.create_block(proof, previous_hash)
    response = {
        'message': 'Congratulations, you just mined a block!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'transactions': block['transactions'] }
    return jsonify(response), 200 # Returns response in JSON format plus a 200 HTTP status code

# Getting the full blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain) }
    return jsonify(response), 200

# Checking if the blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = { 'message': 'The Blockchain is valid' }
    else:
        response = { 'message': 'Error. The Blockchain is not valid' }
    return jsonify(response), 200

# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json() # We get the json file that is posted in the request
    transaction_keys = ['sender', 'receiver', 'amount'] # Check a TXN has all 3 keys
    if not all(key in json for key in transaction_keys): # Check all keys in transacton_keys are in the json file
        return 'Transaction keys are incomplete', 400 # We return a message and error status code
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount']) # We add transaction to transactions list and it returns index of the next block where these will be added to
    response = { 'message': f'This transaction will be added to block #{index}' }
    return jsonify(response), 201

# PART 2: Decentralising our blockchain

# Connecting new nodes
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json() # We will post a json file with list of all nodes in network (both existing and new joiners)
    nodes = json.get('nodes') # This is the list of addresses we pass in json file
    if nodes is None:
        return 'No node', 400
    for node in nodes:
        blockchain.add_node(node) # We add the nodes to the list of addresses
    response = { 'message': 'All the nodes are now connected. The Briancoin Blockchain now contains the following nodes',
                 'total_nodes': list(blockchain.nodes) }
    return response, 201

# Replacing the chain by the longest chain in the network if needed
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {
        'message': 'The chain was replaced by longest in the network',
        'new_chain': blockchain.chain }
    else:
        response = {
        'message': 'The chain was not replaced. Current chain is the longest',
        'chain': blockchain.chain }
    return jsonify(response), 200

# Running the app
app.run(host = '0.0.0.0', port = 5000)
