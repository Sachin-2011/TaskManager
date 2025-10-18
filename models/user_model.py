
# helper functions to use if you want to import from models
from werkzeug.security import generate_password_hash, check_password_hash
def create_user(mongo, username, password):
    hashed = generate_password_hash(password)
    mongo.db.users.insert_one({'username': username, 'password': hashed})

def find_user(mongo, username):
    return mongo.db.users.find_one({'username': username})
