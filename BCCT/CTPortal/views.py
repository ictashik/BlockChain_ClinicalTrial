########################################################### Backend for Python - Clinical Trial Blockchain Implementaion ########################################################################
# Developed on the Django Framework with Python, this prototype leverages encryption libraries, such as hashlib and cryptography, to ensure data integrity. The core                            #
# infrastructure is an emulated file-based blockchain network, designed to synchronize the changes in one system to all other systems in the chain. This demonstrates                           #
# important blockchain benefits, including immutability, full traceability, and transparency. We used the methodology of a clinical trial on Long COVID conducted at                            #
# St. Johns Medical College, Bengaluru, to emulate the working of a clinical trial. (Supplementary file)                                                                                        #
#                                                                                                                                                                                               #
# The detailed description of the methodology and Python codes are open sourced and posted in the GitHub repository (https://github.com/ictashik/BlockChain_ClinicalTrial).                     #
# Briefly, the views.py file contains the basic backend of the code. The building block of the code is the class named Block, and each block indicates the full data of one participant.        #
# Function load_or_generate_key() either retrieves an existing encryption key or crafts a new one. The foundation of the blockchain is established via create_genesis_block(), while            #
# create_new_block(previous_block, data) appends subsequent blocks. Data confidentiality is upheld through encrypt_data(data) and decrypt_data(encrypted_data) utilizing Fernet encryption.     #
# The persistence of blocks in the system is managed by save_block_to_file(block) and load_block_from_file(filepath). The verify_blockchain() function ascertains the blockchain's consistency. #
# For user interaction, SaveBlock(request) captures new block data through a form interface. Although the proof-of-concept demonstrates the feasibility of integrating blockchain principles    #
# into clinical trial processes through a web portal, this model is preliminary and not suited for production deployment.                                                                       #
#################################################################################################################################################################################################

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
    #Name of the Chain
    chain = 'test'

    # create_blockchain(chain,10)
    ChainDF = getchainDF(chain)
    # if __name__ == '__main__':
    # create_blockchain('test',15)
    # verify_blockchain()
    ChainDataFrame = get_blockchain_data()
    
    print(ChainDataFrame)

    #define function to merge columns with same names together
    def same_merge(x): return ','.join(x[x.notnull()].astype(str))

    #define new DataFrame that merges columns with same names together
    ChainDataFrame = ChainDataFrame.groupby(level=0, axis=1).apply(lambda x: x.apply(same_merge, axis=1))
    ChainDataFrame =ChainDataFrame.sort_values(by=['ParticipantEnrollmentNumber']) 

    #Data Analytics
    ParticipantsCount = ChainDataFrame['ParticipantEnrollmentNumber'].count()
    MaleCount = ChainDataFrame[ChainDataFrame['Sex'] == 'M']['ParticipantEnrollmentNumber'].count()
    FeMaleCount = ChainDataFrame[ChainDataFrame['Sex'] == 'F']['ParticipantEnrollmentNumber'].count()
    OthersCount = ChainDataFrame[ChainDataFrame['Sex'] == 'O']['ParticipantEnrollmentNumber'].count()

    ChainDataFrame.to_csv('tes1t.csv',index=False)
    print(ChainDataFrame.columns)
    # ChainDataFrame.columns = ['ParticipantEnrollmentNumber','Group','DateofEnrollment','Age','Sex','Education','Allergy','Vaccine','CoMorbidity','FollowUpDate','NoOfAntiHistamines','LongCovidFatigueFollowUp','LongCovidFatigueFollowUpEnrollment','Consent']
    
    ChainDataFrame = json.loads(ChainDataFrame.to_json(orient='records'))
    

    NotesDF  = json.loads(ChainDF.to_json(orient='records'))
    # print(ChainDataFrame)

    if(verify_blockchain()):
        ChainStatusMessage = "Valid"
        return render(request,'index.html',{'CHAIN':ChainStatusMessage,'CDF':ChainDataFrame,'NDF':NotesDF,'ParticipantsCount':ParticipantsCount,'MaleCount':MaleCount,
                                            'FeMaleCount':FeMaleCount,'OthersCount':OthersCount,})
    else:
        ChainStatusMessage = "InValid"
        return render(request,'index.html',{'CHAIN':ChainStatusMessage})

#Converts the CSV into Pandas Dataframe. CSV is for comparison with the chain data. Even if your Chain becomes invalid you can check the the csb file. 
def getchainDF(name):
    ChainDF = pd.read_csv(name+'.csv')
    return (ChainDF)

#Class Definition
class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = hash

# SHA 256 Hash Calculation for the Block Data
def calculate_hash(index, previous_hash, timestamp, data):
    value = str(index) + str(previous_hash) + str(timestamp) + data
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

#Creating the Genesis Block. Using Empty Data. 'data' is the dictionary that contains empty data. 
def create_genesis_block():
    data = encrypt_data({
        "ParticipantEnrollmentNumber": "0",
        "Group": "None",
        "DateofEnrollment":"None",
        "Age": "0",
        "Sex": "None",
        "Education": "None",
        "Allergy": "None",
        "Vaccine": "None",
        "CoMorbidity": "None",
        "FollowUpDate": "None",
        "NoOfAntiHistamines": "0",
        "LongCovidFatigueFollowUp": "None",
        "LongCovidFatigueFollowUpEnrollment": "None",
        "Consent":"None",
        
    })
    #Calling the constructor for creating a Block object. 
    return Block(0, "0", int(time.time()), data, calculate_hash(0, "0", int(time.time()), data))

#Creates a New Block. The Previous Hash and Data are the inputs. 
def create_new_block(previous_block, data):
    index = previous_block.index + 1
    timestamp = int(time.time())
    encrypted_data = encrypt_data(data)
    hash = calculate_hash(index, previous_block.hash, timestamp, encrypted_data)
    now = datetime.now()

    #Adding the same Data to CSV for Reference.
    ChainDF = pd.read_csv('test.csv')
    ChainDict = {
        'Name' : 'test',
        'Key' : key,
        'Time' : now.strftime("%d/%m/%Y %H:%M:%S"),
        'Hash': hash,
        'Mess' : f"Block #{index} Added",
        }
    IndDF = pd.DataFrame([ChainDict])
    ChainDF = pd.concat([ChainDF,IndDF])

    ChainDF.to_csv('test.csv',index=False)
    return Block(index, previous_block.hash, timestamp, encrypted_data, hash)

#The Data in the Dictionary is encrypted using Fernet Encryption. 
def encrypt_data(data):
    data_str = json.dumps(data)
    encrypted_data = cipher_suite.encrypt(data_str.encode('utf-8'))
    return encrypted_data.decode('utf-8')

#The Data in the Dictionary is decrypted using Fernet decryption. 
def decrypt_data(encrypted_data):
    decrypted_data = cipher_suite.decrypt(encrypted_data.encode('utf-8'))
    return json.loads(decrypted_data)

#Saving the Block as a txt file. 
def save_block_to_file(block, folder='blocks'):
    os.makedirs(folder, exist_ok=True)
    data = [str(block.index), block.previous_hash, str(block.timestamp), block.data, block.hash]
    with open(f'{folder}/block_{block.index}.txt', 'w') as f:
        f.write('\n'.join(data))

#Reading the file to get the block contents
def load_block_from_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.read().splitlines()
        #Calling class constructor to return the Block.
        return Block(int(lines[0]), lines[1], int(lines[2]), lines[3], lines[4])

#Creating New Blockchain. 
def create_blockchain(name,num_blocks_to_add):
    chain_name = str(name)
    # key = Fernet.generate_key()
    blockchain = [create_genesis_block()]
    previous_block = blockchain[0]

    ChainDF = pd.DataFrame()


    #Test Data Generation. Completely Random
    for i in range(1, num_blocks_to_add+1):
        block_to_add = create_new_block(previous_block, {
            "ParticipantEnrollmentNumber": "L" + str(i),
            "Group": "A" if i%2 == 0 else "B",
            "DateofEnrollment":str(generate_random_date(start_date, end_date)),
            "Age": str(i*10),
            "Sex": "M" if i%2 == 0 else "F",
            "Education": "None",
            "Allergy": "Y" if i%2 == 0 else "N",
            "Vaccine": "Y" if i%2 == 0 else "N",
            "CoMorbidity": "Y" if i%2 == 0 else "N",
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
        
        #The Same Data is saved as a CSV file for Reference.
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


# Verification of the Integrity of the Blockchain. If any of the hashes don't match, this function will return False.
def verify_blockchain(folder='blocks'):
    block_files = sorted(glob.glob(f'{folder}/*.txt'), key=os.path.getmtime)
    previous_hash = None
    for block_file in block_files:
        block = load_block_from_file(block_file)
        decrypted_data = decrypt_data(block.data)
        block_hash = calculate_hash(block.index, block.previous_hash, block.timestamp, block.data)
        #Checks if the previous block's hash and that marked in the current block is same. 
        if previous_hash is not None and previous_hash != block.previous_hash:
            print(f"Invalid block #{block.index}.")
            return False
        if block_hash != block.hash:
            print(f"Invalid hash in block #{block.index}.")
            return False
        previous_hash = block.hash
    print("Blockchain is valid.")
    return True

#Getting the Blockchain Data into pandas Dataframe.
def get_blockchain_data(folder='blocks'):
    block_files = sorted(glob.glob(f'{folder}/*.txt'), key=os.path.getmtime)
    blockchain_data = []
    for block_file in block_files:
        block = load_block_from_file(block_file)
        decrypted_data = decrypt_data(block.data)
        blockchain_data.append(decrypted_data)
    return pd.DataFrame(blockchain_data)

#Getting the Hash of last Block. 
def get_last_block_hash(folder='blocks'):
    block_files = sorted(glob.glob(f'{folder}/*.txt'), key=os.path.getmtime)
    if block_files:
        last_block = load_block_from_file(block_files[-1])
        return last_block.hash
    else:
        return None

#Random Date Generation
def generate_random_date(start_date, end_date):
    return start_date + timedelta(
        seconds=random.randint(0, int((end_date - start_date).total_seconds())))

#Returns the Last Block as Object.
def get_last_block(folder='blocks'):
    block_files = sorted(glob.glob(f'{folder}/*.txt'), key=os.path.getmtime)
    if block_files:
        last_block = load_block_from_file(block_files[-1])
        return last_block
    else:
        return None


#Saving a New Block. This utilized the Data transferred through POST. request is the input for this function. this should be called through Django Frontend. 
def SaveBlock(request):
    NewData = {
        "ParticipantEnrollmentNumber" : str(request.POST.get('ParticipantEnrollmentNumber')),
        "Group" : str(request.POST.get('Group')),
        "DateofEnrollment" : str(request.POST.get('DateofEnrollment')),
        "Age" : str(request.POST.get('Age')),
        "Sex" : str(request.POST.get('Sex')),
        "Education" : str(request.POST.get('Education')),
        "Allergy" : str(request.POST.get('Allergy')),
        "Vaccine" : str(request.POST.get('Vaccine')),
        "CoMorbidity" : str(request.POST.get('CoMorbidity')),
        "FollowUpDate" : str(request.POST.get('FollowUpDate')),
        "NoOfAntiHistamines" : str(request.POST.get('NoOfAntiHistamines')),
        "LongCovidFatigueFollowUp" : str(request.POST.get('LongCovidFatigueFollowUp')),
        "LongCovidFatigueFollowUpEnrollment" : str(request.POST.get('LongCovidFatigueFollowUpEnrollment')),
        "Consent" : str(request.POST.get('Consent')),
    }

    # print(NewData)
    save_block_to_file(create_new_block(get_last_block(), NewData))


    return index(request)
