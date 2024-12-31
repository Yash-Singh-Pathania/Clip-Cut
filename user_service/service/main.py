import postgres_service.main as db
import redis_service.main as redis
from fastapi import FastAPI, APIRouter, HTTPException, status
import uuid
import time

salt = 'md5'
member_timeout = 30 # seconds

app = FastAPI()
router = APIRouter(
    prefix='/users',
    tags=['Users']
)

@router.post('/create', status_code=status.HTTP_201_CREATED)
def create_user(username: str, password: str):
    conn = db.get_conn()
    cursor = conn.cursor()

    if user_exists(cursor, username):
        conn.close()
        raise HTTPException(status_code=409, detail={
            "success": False,
            "message": "Username already exists"
        })

    cursor.execute(f"""
        insert into users (username, password_hash)
        values ('{username}', crypt('{password}', gen_salt('{salt}')))
    """)
    conn.commit()
    conn.close()

    session_id = generate_session_id()

    return {
        "success": True,
        "message": "Create user successful",
        "session_id": session_id
    }

def user_exists(cursor, username: str):
    cursor.execute(f"""
        select 1
        from users
        where username = '{username}'
   """)
    return cursor.fetchall() != []

def generate_session_id():
    id = str(uuid.uuid4())
    redis.client.set(id, time.time())
    return id

@router.get('/session_auth')
def authenticate_session_id(session_id: str):
    success = (redis.client.exists(session_id) and
            time.time() - float(redis.client.get(session_id)) < member_timeout)
    if not success:
        raise HTTPException(status_code=401, detail={
            "success": False,
            "message": "Invalid credentials"
        })
    return {
        "success": True,
        "message": "Authenticate session id successful",
    }

@router.get('/auth')
def authenticate_user(username: str, password: str):
    conn = db.get_conn()
    cursor = conn.cursor()
    cursor.execute(f"""
        select 1
        from users
        where
            username = '{username}' and
            password_hash = crypt('{password}', password_hash)
    """)
    if cursor.fetchall() == []:
        conn.close()
        raise HTTPException(status_code=401, detail={
            "success": False,
            "message": "Invalid credentials"
        })
    else:
        conn.commit()
        conn.close()
        session_id = generate_session_id()
        return {
            "success": True,
            "message": "Authenticate user successful",
            "session_id": session_id
        }

@router.delete('/delete', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(username: str, password: str):
    conn = db.get_conn()
    cursor = conn.cursor()

    cursor.execute(f"""
        select 1
        from users
        where
            username = '{username}' and
            password_hash = crypt('{password}', password_hash)
    """)
    if cursor.fetchall() == []:
        conn.close()
        raise HTTPException(status_code=401, detail={
            "success": False,
            "message": "Invalid credentials"
        })

    cursor.execute(f"""
        delete from users
        where
            username = '{username}' and
            password_hash = crypt('{password}', password_hash)
    """)
    conn.commit()
    conn.close()
    # todo delete session_id?
    return {
        "success": True,
        "message": "Delete user successful",
    }

# todo def forgot_password() ?

app.include_router(router)