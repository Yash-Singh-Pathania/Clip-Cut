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

** Developer : unknown




Redis memory that is stored ram volatile , 
user logins : i login email yash@gmail.com 
passwrod 123 

fe -> your service , you will return saying that the password is right and my session id is 14667793 user 7 
in redis: 7 : 14667793 ( give it a time 4 hours ) what this means after 4 hours redis delte this ( not postgres) 

if my user decides to close the tab, i will still save the session id 
the 



