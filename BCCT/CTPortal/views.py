from django.shortcuts import render

import hashlib
import os
import time
import glob
from cryptography.fernet import Fernet
import json
import pandas as pd
from datetime import datetime,timedelta
import random

# Create your views here.
from django.http import HttpResponse


KEY_FILE = 'key.csv'

start_date = datetime(2019, 1, 1)
end_date = datetime(2020, 12, 31)


def load_or_generate_key():
    if os.path.exists(KEY_FILE):
        return pd.read_csv(KEY_FILE, header=None).values[0][0]
    else:
        key = Fernet.generate_key().decode('utf-8')
        pd.DataFrame([key]).to_csv(KEY_FILE, index=False, header=False)
        return key

key = load_or_generate_key()

# key = Fernet.generate_key().decode('utf-8')
cipher_suite = Fernet(key.encode('utf-8'))


def index(request):
    # print('Key Used ',key)
    chain = 'test'
    # create_blockchain(chain,10)
    ChainDF = getchainDF(chain)
    # if __name__ == '__main__':
    # create_blockchain('test',15)
    # verify_blockchain()
    ChainDataFrame = get_blockchain_data()
    ChainDataFrame.columns = ['ParticipantEnrollmentNumber','Group','DateofEnrollment','Age','Sex','Education','Allergy','Vaccine','CoMorbidity','FollowUpDate','NoOfAntiHistamines','LongCovidFatigueFollowUp','LongCovidFatigueFollowUpEnrollment','Consent']
    ChainDataFrame = json.loads(ChainDataFrame.to_json(orient='records'))

    NotesDF  = json.loads(ChainDF.to_json(orient='records'))
    # print(ChainDataFrame)

    if(verify_blockchain()):
        ChainStatusMessage = "Valid"
        return render(request,'index.html',{'CHAIN':ChainStatusMessage,'CDF':ChainDataFrame,'NDF':NotesDF})
    else:
        ChainStatusMessage = "InValid"
        return render(request,'index.html',{'CHAIN':ChainStatusMessage})


def getchainDF(name):
    ChainDF = pd.read_csv(name+'.csv')
    return (ChainDF)


class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = hash

def calculate_hash(index, previous_hash, timestamp, data):
    value = str(index) + str(previous_hash) + str(timestamp) + data
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

def create_genesis_block():
    data = encrypt_data({
        "Participant Enrollment Number": "0",
        "Group": "None",
        "DateofEnrollment":None,
        "Age": "0",
        "Sex": "None",
        "Education": "None",
        "Allergy": "None",
        "Vaccine": "None",
        "Co Morbidity": "None",
        "FollowUpDate": "None",
        "NoOfAntiHistamines": 0,
        "LongCovidFatigueFollowUp": "None",
        "LongCovidFatigueFollowUpEnrollment": "None",
        "Consent":"None",
        
    })
    return Block(0, "0", int(time.time()), data, calculate_hash(0, "0", int(time.time()), data))

def create_new_block(previous_block, data):
    index = previous_block.index + 1
    timestamp = int(time.time())
    encrypted_data = encrypt_data(data)
    hash = calculate_hash(index, previous_block.hash, timestamp, encrypted_data)
    return Block(index, previous_block.hash, timestamp, encrypted_data, hash)

def encrypt_data(data):
    data_str = json.dumps(data)
    encrypted_data = cipher_suite.encrypt(data_str.encode('utf-8'))
    return encrypted_data.decode('utf-8')

def decrypt_data(encrypted_data):
    decrypted_data = cipher_suite.decrypt(encrypted_data.encode('utf-8'))
    return json.loads(decrypted_data)

def save_block_to_file(block, folder='blocks'):
    os.makedirs(folder, exist_ok=True)
    data = [str(block.index), block.previous_hash, str(block.timestamp), block.data, block.hash]
    with open(f'{folder}/block_{block.index}.txt', 'w') as f:
        f.write('\n'.join(data))

def load_block_from_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.read().splitlines()
        return Block(int(lines[0]), lines[1], int(lines[2]), lines[3], lines[4])

def create_blockchain(name,num_blocks_to_add):
    chain_name = str(name)
    # key = Fernet.generate_key()
    blockchain = [create_genesis_block()]
    previous_block = blockchain[0]

    ChainDF = pd.DataFrame()

    for i in range(1, num_blocks_to_add+1):
        block_to_add = create_new_block(previous_block, {
            "Participant Enrollment Number": "L" + str(i),
            "Group": "A" if i%2 == 0 else "B",
            "DateofEnrollment":str(generate_random_date(start_date, end_date)),
            "Age": str(i*10),
            "Sex": "M" if i%2 == 0 else "F",
            "Education": "None",
            "Allergy": "Y" if i%2 == 0 else "N",
            "Vaccine": "Y" if i%2 == 0 else "N",
            "Co Morbidity": "Y" if i%2 == 0 else "N",
            "FollowUpDate": str(generate_random_date(start_date, end_date)),
            "NoOfAntiHistamines": i,
            "LongCovidFatigueFollowUp": "Y" if i%2 == 0 else "N",
            "LongCovidFatigueFollowUpEnrollment": "Y" if i%2 == 0 else "N",
            "Consent":"Y",
        })
        blockchain.append(block_to_add)
        previous_block = block_to_add
        print(f"Block #{block_to_add.index} has been added to the blockchain!")
        print(f"Hash: {block_to_add.hash}\n")
        now = datetime.now()
        
        ChainDict = {
        'Name' : chain_name,
        'Key' : key,
        'Time' : now.strftime("%d/%m/%Y %H:%M:%S"),
        'Hash': block_to_add.hash,
        'Mess' : f"Block #{block_to_add.index} Added",
        }
        IndDF = pd.DataFrame([ChainDict])
        ChainDF = pd.concat([ChainDF,IndDF])
        save_block_to_file(block_to_add)
    
    ChainDF.to_csv(name+'.csv',index=False)

def verify_blockchain(folder='blocks'):
    block_files = sorted(glob.glob(f'{folder}/*.txt'), key=os.path.getmtime)
    previous_hash = None
    for block_file in block_files:
        block = load_block_from_file(block_file)
        decrypted_data = decrypt_data(block.data)
        block_hash = calculate_hash(block.index, block.previous_hash, block.timestamp, block.data)
        if previous_hash is not None and previous_hash != block.previous_hash:
            print(f"Invalid block #{block.index}.")
            return False
        if block_hash != block.hash:
            print(f"Invalid hash in block #{block.index}.")
            return False
        previous_hash = block.hash
    print("Blockchain is valid.")
    return True

def get_blockchain_data(folder='blocks'):
    block_files = sorted(glob.glob(f'{folder}/*.txt'), key=os.path.getmtime)
    blockchain_data = []
    for block_file in block_files:
        block = load_block_from_file(block_file)
        decrypted_data = decrypt_data(block.data)
        blockchain_data.append(decrypted_data)
    return pd.DataFrame(blockchain_data)

def get_last_block_hash(folder='blocks'):
    block_files = sorted(glob.glob(f'{folder}/*.txt'), key=os.path.getmtime)
    if block_files:
        last_block = load_block_from_file(block_files[-1])
        return last_block.hash
    else:
        return None

def generate_random_date(start_date, end_date):
    return start_date + timedelta(
        seconds=random.randint(0, int((end_date - start_date).total_seconds())))
