import io
import bson
from pymongo import MongoClient
import torch
import numpy as np
import pickle
import time
from wirehead.defaults import SWAP_THRESHOLD

###############################
### Functions for generator ###
###############################
def push_mongo(
    image_bytes,
    label_bytes,
    id,
    collection_bin,
    chunkSize=10
    ):
    """Pushes a chunkified serilized tuple containing two serialized (img: torch.Tensor, lab:torch.tensor)"""
    for chunk in chunk_binobj(image_bytes, id, "image", chunkSize):
        collection_bin.insert_one(chunk)
    for chunk in chunk_binobj(label_bytes, id, "label", chunkSize):
        collection_bin.insert_one(chunk)

def chunk_binobj(tensor_compressed, id, kind, chunksize):
    """Convert chunksize from megabytes to bytes"""
    chunksize_bytes = chunksize * 1024 * 1024
    # Calculate the number of chunks
    num_chunks = len(tensor_compressed) // chunksize_bytes
    if len(tensor_compressed) % chunksize_bytes != 0:
        num_chunks += 1
    # Yield chunks
    for i in range(num_chunks):
        start = i * chunksize_bytes
        end = min((i + 1) * chunksize_bytes, len(tensor_compressed))
        chunk = tensor_compressed[start:end]
        yield {
            "id": id,
            "chunk_id": i,
            "kind": kind,
            "chunk": bson.Binary(chunk),
        }

def tensor2bin(tensor: torch.Tensor) -> bytes:
    """Serialize a torch tensor into uint8"""
    tensor = tensor.to(torch.uint8)
    buffer = io.BytesIO()
    torch.save(tensor, buffer)
    tensor_binary = buffer.getvalue()
    return tensor_binary

#############################
### Functions for manager ###
#############################
def swap_mongo(db, n_swaps=0, debug=False):
    """
    Atomically swaps the read and write halves of mongo wirehead
    Input:
        db:                 : mongo database
        n_swaps (optional)  : total number of swaps
        debug (optional)    : toggles printing stats
    Returns (optional): 
        n_swaps + 1         : total number of swaps + 1
    """
    write_side = db['write']
    read_side = db['read']

    start_time = time.time()

    with db.client.start_session() as session:
        session.start_transaction():
            db['write'].rename('read', dropTarget=True, session=session)
            db.create_collection('write', session=session)
        session.commit_transaction()
    print("Swap operation completed in ", time.time() - start_time, " seconds")
    print(f"Total swaps performed: {n_swaps+1}")
    print(f"Total samples generated: {(n_swaps+1)*SWAP_THRESHOLD")
    return n_swaps + 1

def get_mongo_bytes(db):
    """Returns the size of mongo read and write halves in bytes"""
    raise NotImplementedError()

def get_mongo_write_size(db):
    """Returns the number of samples in the write half of mongo"""
    raise NotImplementedError()

if __name__=="__main__":
    print("This file contains functions that are used by other components of wirehead")