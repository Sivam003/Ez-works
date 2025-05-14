# EZ File - Document Verification System

EZ File is a web-based platform for secure user registration, email verification, and document upload. The system is built using **Flask**, **SQLAlchemy**, and **SQLite** for backend functionality.

---

## 📌 Project Status

✅ Implemented:
- Client signup with hashed passwords  
- Email verification through unique token  
- Login with token-based authentication  

🚧 In Progress:
- Document upload feature is under development (currently stuck at upload route)

---

## 🛠️ Tech Stack

- **Backend**: Flask, SQLAlchemy
- **Database**: SQLite
- **Authentication**: JWT tokens, bcrypt password hashing
- **Testing Tools**: Postman

---

## 🧪 What’s Working

- You can **sign up a new user** using `POST /auth/signup`
- You receive a **verification token** via API (in future: email)
- You can **verify the user** via `GET /auth/verify/<token>`
- Verified users can **log in** using `POST /auth/login` and receive an auth token

---

## 🚫 What’s Not Working Yet

The document upload route (`/file/upload`) is not functioning properly.
- Problem: "Method Not Allowed" error in browser
- Likely Cause: The route only accepts `POST`, and opening it via browser uses `GET`
- Fix in Progress: Testing via Postman using `POST` with `form-data` or `multipart/form-data`

---

## 🧪 API Routes


### Authentication

#### POST `/auth/signup`
- Registers a new user  
- JSON body:
{
  "email": "client@example.com",
  "password": "securepassword",
  "role": "client"
}

* **GET /auth/verify/<token>**: Verifies a user using their verification token
	+ Returns: Success/failure message
* **POST /auth/login**: Authenticates a user and returns a JWT token
	+ JSON body:
		- email: string
		- password: string
	+ Returns: JWT token if credentials are valid and user is verified

### Document Management

* **POST /file/upload**: Uploads a document (authenticated route)
	+ Headers: Authorization: Bearer <token>
	+ Form-data body:
		- document: file
		- subject: string
	+ Returns: Confirmation or error
* **GET /file/status/<file_id>**: Get verification status of uploaded file
	+ Access: Authenticated users only
	+ Returns: JSON with document verification details

### Operations Panel

* **GET /operations/files**: View list of pending files to be verified
	+ Access: role = operations only
	+ Returns: List of unverified documents
* **POST /operations/verify/<file_id>**: Mark a document as verified
	+ Access: role = operations only
	+ Returns: Success/failure message

### Admin Routes

* **GET /admin/users**: Get all registered users
	+ Access: role = admin only
	+ Returns: List of users
* **DELETE /admin/delete_user/<user_id>**: Deletes a user by ID
	+ Access: role = admin only
	+ Returns: Deletion status
* **POST /admin/create_user**: Create a new user with a specific role (e.g. operations)
	+ Access: role = admin only
	+ JSON body:
		- email: string
		- password: string
		- role: string
	+ Returns: Created user info or error

## Requirements
-------------

* Python 3.8+
* Flask 2.0+
* WTForms 3.0+
* Flask-Mail 0.9+
* SQLite 3.0+
* JWT
* itsdangerous

## Installation
--------------

1. Clone the repository
2. Create a virtual environment and activate it
3. Install dependencies using pip
4. Configure the `.env` file with your email and SMTP settings
5. Run the app using `flask run`

## Usage
-----

1. Register a new user using the `/auth/signup` endpoint
2. Verify your email using the `/auth/verify/<token>` endpoint
3. Login using the `/auth/login` endpoint and obtain a JWT token
4. Upload a document using the `/file/upload` endpoint
5. Verify the document using the `/operations/verify/<file_id>` endpoint
6. Delete a user using the `/admin/delete_user/<user_id>` endpoint

## 🚀 Deployment

To deploy this project, we recommend using **Heroku**, which is a simple platform-as-a-service (PaaS) that supports Python applications. Below are the steps to deploy the app on Heroku.

### Steps for Deployment:

1. **Prepare the Application for Production:**
   - Ensure all configurations are production-ready:
     - Set `SECRET_KEY` securely (using environment variables or `.env` file).
     - Configure the database for production (use PostgreSQL or any preferred database).
     - Ensure that `DEBUG = False` in your `config.py`.

2. **Install Required Dependencies:**
   - Make sure you have all dependencies listed in `requirements.txt`:
     ```bash
     pip freeze > requirements.txt
     ```
   - Install `gunicorn` as a WSGI server for production:
     ```bash
     pip install gunicorn
     ```
   - Add `gunicorn` to your `requirements.txt` file.

3. **Create a `Procfile`:**
   - In the root of your project directory, create a file named `Procfile` (without any file extension) with the following content:
     ```
     web: gunicorn app:app
     ```
     - `app:app` refers to the Flask application object created in your `app.py`.

4. **Set up PostgreSQL Database (for Production):**
   - If using Heroku’s PostgreSQL, provision a database:
     ```bash
     heroku addons:create heroku-postgresql:hobby-dev
     ```
   - Heroku will automatically set the `DATABASE_URL` environment variable. Use this in your app to configure the database connection:
     ```python
     import os
     app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
     ```

5. **Set up Environment Variables:**
   - Add necessary environment variables using the Heroku CLI:
     ```bash
     heroku config:set SECRET_KEY="your_secret_key"
     heroku config:set FLASK_ENV=production
     ```

6. **Push Code to GitHub:**
   - If not done already, push your code to GitHub:
     ```bash
     git push origin master
     ```

7. **Deploy the Application on Heroku:**
   - Link your Heroku app to your GitHub repository:
     ```bash
     heroku create <your-app-name>
     git remote add heroku https://git.heroku.com/<your-app-name>.git
     ```
   - Deploy the app to Heroku:
     ```bash
     git push heroku master
     ```

8. **Run Database Migrations:**
   - After deployment, run the database migrations:
     ```bash
     heroku run flask db upgrade
     ```

9. **Access the Application:**
   - Once deployed, you can access your app using:
     ```bash
     heroku open
     ```
   - Your app should now be live on Heroku!

---

### Future Steps:

1. **Set up Continuous Deployment (CD):**
   - Integrate **GitHub Actions** or **Heroku GitHub Integration** for continuous deployment. This way, your app will automatically deploy every time changes are pushed to GitHub.

2. **Configure Logging:**
   - Set up logging to monitor app errors and performance using Heroku’s built-in logging or third-party services:
     ```bash
     heroku logs --tail
     ```

3. **Monitor Application Performance:**
   - Use monitoring tools such as **New Relic**, **Datadog**, or **Heroku’s built-in monitoring** to track errors, response times, and database performance.

4. **Set up SSL/HTTPS:**
   - Ensure that SSL/HTTPS is enabled for secure connections. Heroku provides free SSL certificates for custom domains.

5. **Backup your Database:**
   - Use Heroku’s backup services to create regular backups of your database.

---

### Conclusion:

Deploying a Flask application to **Heroku** is simple and effective for small-scale projects. Once deployed, make sure to monitor the app’s performance, manage environment variables securely, and periodically back up your data to maintain the health of your application.

