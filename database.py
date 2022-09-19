import pymongo
import logging as lg
import os


# This is for dynamic file creation to save the logging
path = os.getcwd() + "/Server_log"
isExist = os.path.exists(path)

if not isExist:
    os.makedirs('Server_log')
else:
    pass

path = os.getcwd()

logger = lg.getLogger(__name__)
logger.setLevel(lg.DEBUG)
formatter = lg.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s', '%d/%m/%Y %I:%M:%S %p')
file_handler = lg.FileHandler(os.path.join(path, "Server_log", "db_logfile.log"), 'w')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# create connection
def connect():
    try:
        client = pymongo.MongoClient("mongodb+srv://ineuron:Project1@cluster0.rp4qzrr.mongodb.net/?retryWrites=true&w=majority")
    except Exception as e:
        logger.error(e)
    else:
        # creating database and collection
        db = client['flipkart_db']
        coll = db['products']
        logger.info("Connection to mongodb is successful")
        logger.info("database and collection is created")
        return coll


# Inserting the data into the collection
def rec_insert(coll, record):
    try:
        coll.insert_one(record)
    except Exception as e:
        logger.error(e)


def succ_insert(coll):
    logger.info("Records uploaded to database successfully")
    return "Successfully inserted to the database"


# finding all the records
def show_res(coll):
    try:
        results = coll.find()
    except Exception as e:
        logger.error(e)
    else:
        logger.info("Record fetched from database successfully")
        return results


# for delete
def rec_del(coll):
    try:
        coll.drop()
        logger.info("Collection deleted successfully.")
    except Exception as e:
        logger.error(e)

