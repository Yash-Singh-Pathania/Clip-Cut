Here’s a clearer and more structured set of requirements for a simple user authentication service that a developer can use as a guide:

---

**User Authentication Service Requirements**

**1. General Features:**
   - A simple user authentication system using username and password.
   - Automatically generate a unique identifier (UUID) for each user upon registration.
   - Include a "Forgot Password" option to allow users to reset their password.
   - If feasible, integrate OAuth to enable authentication via third-party services (e.g., Google, Facebook).

**2. Backend APIs:**
   - **Authenticate User API:**
     - Verify username and password.
     - Check if a username is already in use to ensure uniqueness.
   - **Create User API:**
     - Register a new user with a username and password.
     - Generate and assign a UUID to the user.
     - Store user details securely in the database.

**3. Security Requirements:**
   - Implement secure password storage using hash and salt techniques.
   - Ensure that all data transmissions are secured via HTTPS.
   - OAuth implementation should adhere to the latest security practices.

**4. Additional Considerations:**
   - Provide detailed API documentation for easy integration.
   - Consider scalability and potential future requirements in the system design.
   - Implement rate limiting and basic security checks to prevent abuse.

** Developer : Euan Leith


-----
(all from project root folder, don't need to run `cd`)
### Setup
PostgreSQL:
```markdown
brew install libpq
brew link --force libpq
pip install psycopg2
```
Service:
```markdown
python3 -m pip install -r user_service/requirements.txt
```

### Run
Start PostgreSQL/Redis:
```markdown
docker-compose up
```
In a different terminal, run FastAPI:
```markdown
fastapi dev user_service/service/main.py
```
Then should be accessible through Swagger at `http://127.0.0.1:8000/docs#`

Once finished, need to stop running FastAPI:
```markdown
sudo lsof -t -i tcp:8000 | xargs kill -9
```

### Endpoints
#### Create user

POST `/users/create`

Payload example:
```markdown
{
    "username": "myuser",
    "password": "mypassword"
}
```
Response example:
```markdown
{
    "success": true,
    "message": "Create user successful",
    "sesssion_id": 1234
}
```

#### Authenticate user (when logging in)
GET `/users/auth`

Payload example:
```markdown
{
    "username": "myuser",
    "password": "mypassword"
}
```
Response example:
```markdown
{
     "success": true,
     "message": "Authenticate user successful",
     "sesssion_id": 1234
}
```

#### Authenticate session id
GET `users/session_auth`

Payload example:
```markdown
{
    "session_id": 1234
}
```
Response example:
```markdown
{
     "success": true,
     "message": "Authenticate session id successful",
}
```

#### Delete user
DELETE `/users/delete`

Payload example:
```markdown
{
     "username": "myuser",
     "password": "mypassword"
}
```
Response example:
```markdown
{
     "success": true,
     "message": "Delete user successful",
}
```

---
todo add tests, run using:
```markdown
 python3 -m user_service.service.test_main
```
todo also Docker isn't working
