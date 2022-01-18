# Module 1 - Create a Blockchain

# Importing libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify

# Creating blockchain
class Blockchain:

    def __init__(self):
        self.chain = []
        # Values for genesis block are abitrary but we are using conventions
        # We must put previous hash in quotes as required by SHA256 encoding function
        self.create_block(proof = 1, previous_hash = '0')

    def create_block(self, proof, previous_hash):
        block = { 'index': len(self.chain) + 1,
                'timestamp': str(datetime.datetime.now()),
                'proof': proof,
                'previous_hash': previous_hash }
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            # This function can be anything but needs to be non-symmetrical (if reverse arguments not same)
            # .encode() is required for SHA256 function
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    # Method to help with consensus protocol
    def is_chain_valid(self, chain):
        previous_block = chain[0] # Start off with first block
        block_index = 1

        # Iterate through all blocks in chain
        while block_index < len(chain):
            block = chain[block_index]

            # Check previous hash field in block is equal to the hash of the prior block
            if block['previous_hash'] != self.hash(previous_block):
                return False

            # Check that hash operation starts with 4 leading zeros
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False

            previous_block = block
            block_index += 1

        # Only return this if no errors during the while loop
        return True

# Mining blockchain
