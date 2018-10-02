import hashlib
import json
from time import time
import uuid
import base64
from textwrap import dedent
from urllib.parse import urlparse
from flask import Flask, flash, redirect, jsonify, request,render_template, url_for
import socket
import fcntl
import struct
import requests


app = Flask(__name__)
node_identifier = str(uuid.uuid1()).replace('-', '')# Generate a globally unique address for this node
app.secret_key = node_identifier
resp=""
class blockchain(object):
    current_transactions = []
    ind1 = 0
    chain = [{
        'index': 1,
        'timestamp': time(),
        'transactions': 1,
        'proof': 0,
        'previous_hash': 0
    }]
    verified_proof = [0]
    nodes = {}
    addresses = ["http://10.10.10.4:800/chain","http://10.10.10.3:800/chain"]#"http://10.10.10.1:8000/chain"]
    e_addresses = ["http://10.10.10.4:800/proof","http://10.10.10.3:800/proof"]#,"http://10.10.10.1:8000/proof"]

    account1 = {}
    

    def new_block(self):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': self.proof_of_work(),
            'previous_hash': self.hash(self.chain[-1])
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append(
        {
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

    def hash(self, block):
        block_string = bytes(json.dumps(block),'utf-8')
        block_string = base64.b64encode(block_string)
        return hashlib.sha1(block_string).hexdigest()


    def proof_of_work(self):
        last_proof = -1
        proof = 0
        self.consensus()  #uncomment when multiple nodes have been added to the network
        while ((self.valid_proof(last_proof, proof) is False) or (proof in self.verified_proof)):
            self.consensus()    #uncomment when multiple nodes have been added to the network
            last_proof = proof
            proof += 1
        self.verified_proof.append(proof)
        self.ind1 = 0
        return proof

    def valid_proof(self,last_proof, proof):
        guess = str(last_proof) + str(proof)
        guess = guess.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:2] == "00"

    #do this later
    def get_ip(self):
        return "10.10.10.3:800"

    #do this later
    def get_mac():
        return "Mac-02"

    def register_nodes(self):#create a section where every node can view other nodes list of nodes/ips
        address = self.get_ip() #dont't forget to do this | put this in a try-except statement
        if address not in self.nodes:
            node = "node"+str((len(self.nodes)+1)) #change it to the mac-address of each host
            self.nodes[node]=self.get_ip()
        t = "http://"+self.get_ip()+"/chain"
        r = "http://"+self.get_ip()+"/proof"
        self.e_addresses.append(r)
        self.addresses.append(t)


    def resolve_conflicts(self):
        temp = self.chain #doesn't take into account blocks createdduring consensus
        if(self.consensus()==temp):
            return "Your Chain is valid!!!"
        else:
            return "Your Chain has been Updated!!!"

    def consensus(self):
        #check for the available nodes on the network -> store in an array
        #filter the addresses above by checking for valid chains
        #filter by ensuring their chain length is equal to their proof's length
        #search for the longest chain
        #check if the array that stores the proof is correct


        temp=self.chain
        a="http://"+self.get_ip()+"/proof"

        if(a in self.e_addresses):
            self.e_addresses.remove(a)
            self.e_addresses.insert(0,a)
            
        a="http://"+self.get_ip()+"/chain"
        temp1=self.verified_proof

        if(a in self.addresses):
            self.addresses.remove(a)
            self.addresses.insert(0,a)

        for i in range(len(self.addresses)):
            if(self.addresses[i] == "http://"+self.get_ip()+"/chain"):
                if(len(self.chain)!=len(self.verified_proof)):
                    self.chain = [{
                                'index': 1,
                                'timestamp': time(),
                                'transactions': 1,
                                'proof': 0,
                                'previous_hash': 0
                            }]
                    self.verified_proof = [0]
                    self.nodes = {}
                    self.current_transactions = []
                    self.addresses = ["http://10.10.10.4:800/chain","http://10.10.10.3:800/chain"]#"http://10.10.10.1:8000/chain"]
                    self.e_addresses = ["http://10.10.10.4:800/proof","http://10.10.10.3:800/proof"]#,"http://10.10.10.1:8000/proof"]

                if(len(self.chain)>1):
                    if(self.valid_chain(self.chain)!=True):
                        self.chain = [{
                                'index': 1,
                                'timestamp': time(),
                                'transactions': 1,
                                'proof': 0,
                                'previous_hash': 0
                            }]
                        self.verified_proof = [0]
                        self.nodes = {}
                        self.addresses = ["http://10.10.10.4:800/chain","http://10.10.10.3:800/chain"]
                        self.e_addresses = ["http://10.10.10.4:800/proof","http://10.10.10.3:800/proof"]
                        self.current_transactions = []
						#self.addresses = ["http://10.10.10.4:800/chain","http://10.10.10.3:800/chain"]#"http://10.10.10.1:8000/chain"]
						#self.e_addresses = ["http://10.10.10.4:800/proof","http://10.10.10.3:800/proof"]#,"http://10.10.10.1:8000/proof"]
            else:
                if(len(json.loads(requests.get(self.addresses[i]).text))>1):
                    query = self.addresses[i]
                    fakechain = json.loads(requests.get(self.addresses[i]).text)
                    if(self.valid_chain(fakechain)!=True):
                        self.addresses.remove(self.addresses[i])
                    if(len(fakechain)!=len(json.loads(requests.get(query[:-5]+"proof").text)) or (query not in self.addresses)):
                        self.e_addresses.remove(query[:-5]+"proof")


        for i in range(len(self.addresses)):
            if(self.addresses[i]=="http://"+self.get_ip()+"/chain"):#put the below section in a try-statement
                if(len(self.chain)<len(json.loads(requests.get(self.addresses[i+1]).text))):
                    temp = json.loads(requests.get(self.addresses[i+1]).text)
                    temp1 = json.loads(requests.get(self.e_addresses[i+1]).text)

            else:
                if(len(temp)<len(json.loads(requests.get(self.addresses[i]).text))):
                    temp = json.loads(requests.get(self.addresses[i]).text)
                    temp1 = json.loads(requests.get(self.e_addresses[i]).text)

        self.chain = temp
        self.verified_proof = temp1
        self.ind1 +=1
        print(self.ind1)

    def valid_chain(self, chain):
        i= 1

        while(i < len(chain)):
            block = chain[i]
            prev_b = chain[i-1]
            if(block['previous_hash'] != self.hash(prev_b)):
                return False
            i+=1
        return True


B = blockchain()

@app.route('/chain1')
def f_chain():
	return jsonify(B.chain)
@app.route('/chain', methods=['GET'])
def full_chain():
	#B.consensus()
	return json.dumps(B.chain)
 

@app.route('/')
def index():
	#B.consensus()
	return render_template('index.html')

@app.route('/proof',methods=['GET','POST'])
def proof():
	#B.consensus()
	return json.dumps(B.verified_proof)

@app.route('/transactions/new')
def new_transaction():
	#B.consensus()
	return render_template('new_transaction.html')
	
    

@app.route('/registeration',methods=['GET','POST'])
def register1():
	username = request.form['username'].strip()
	password = request.form['password'].strip()
	
	#try:
	try:
		if(username not in B.account1):
			B.account1[username]=password
			flash("**Account succesffully registered**")
			return "Account registered"
	except Exception:
		flash("**Account alredy exists**")
		return "Account Already Exists"
		
	
@app.route('/reg1',methods=['GET','POST'])
def regg():
	return render_template('regist.html')
@app.route('/login1',methods=['GET','POST'])
def loggg():
	return render_template('log.html')
	
@app.route('/login',methods=['GET','POST'])
def login1():
	username = request.form['username'].strip()
	password = request.form['password'].strip()
	
	#try:
	try:
		if(B.account1[username]==password):
			return redirect(url_for('mine1'))
	except Exception:
		return "No User"
		
@app.route('/transactions/mine', methods=['GET','POST'])
def mine1():
	#B.consensus()
	sender = request.form['sender']
	recipient = request.form['recipient']
	amount = request.form['amount']
	if((sender.strip()=="" or recipient.strip()=="")or(amount.strip()=="")):
		return render_template('ErrorPage.html')
	B.new_transaction(sender, recipient, amount)
	response = B.new_block()
	Reward()
	flash("**A new block has been mined and the miner has been rewarded**")
	return redirect(url_for('new_transaction'))


@app.route('/transactions/mine/reward')
def Reward():
	#B.consensus()
	B.new_transaction(
        "0",
        node_identifier,
        1
	)
	B.new_block()

@app.route('/nodes/register', methods=['GET','POST'])
def register_nodes():
	#B.consensus()
	B.register_nodes()
	return jsonify(B.nodes)

@app.route('/chain/resolve',methods=['GET','POST'])
def resolve_conflicts():
	#B.consensus()
	return B.resolve_conflicts()

if __name__ == '__main__':
	app.run(host='10.10.10.3',debug=True,port=800)
