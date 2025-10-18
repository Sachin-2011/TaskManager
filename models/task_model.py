
# helper task functions for structure
from datetime import datetime
def create_task(mongo, user_id, title, description=''):
    mongo.db.tasks.insert_one({'user_id': user_id, 'title': title, 'description': description, 'completed': False, 'important': False, 'created_at': datetime.utcnow()})

def get_tasks(mongo, user_id, filter_by=None):
    q = {'user_id': user_id}
    if filter_by == 'important':
        q['important'] = True
    elif filter_by == 'completed':
        q['completed'] = True
    elif filter_by == 'incomplete':
        q['completed'] = False
    return list(mongo.db.tasks.find(q))
