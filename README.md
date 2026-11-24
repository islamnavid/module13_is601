# Module 13 — JWT Authentication, Frontend Integration, and CI/CD

**Course:** IS601 — Python for Web API Development  
**Student:** Md Navidul Islam  
**Institution:** New Jersey Institute of Technology (NJIT)

## Project Overview

This project extends a FastAPI-based Calculations Application with user authentication, frontend integration, automated testing, and a CI/CD pipeline.

The application supports user registration, secure login using JSON Web Tokens (JWT), password validation, an authenticated calculations dashboard, and calculation history.

The project also integrates Playwright for end-to-end browser testing, Docker for containerization, GitHub Actions for continuous integration and deployment, and Trivy for vulnerability scanning.

## Technologies Used

- **Backend:** Python 3.12, FastAPI
- **Database:** PostgreSQL, SQLAlchemy
- **Authentication:** JWT, password hashing
- **Frontend:** HTML, CSS, JavaScript, Jinja2
- **Testing:** pytest, Playwright
- **Containerization:** Docker, Docker Compose
- **CI/CD:** GitHub Actions
- **Security Scanning:** Trivy
- **Container Registry:** Docker Hub

## Features

### 1. User Registration

Users can create accounts by providing:

- Username
- Email address
- First name
- Last name
- Password
- Password confirmation

The registration process includes input validation, duplicate-account checks, password validation, and secure password storage.

Passwords must contain at least eight characters, including uppercase letters, lowercase letters, and numbers.

### 2. JWT Authentication

The application implements token-based authentication using JSON Web Tokens.

The authentication functionality includes:

- User registration through `/auth/register`
- User login through `/auth/login`
- JWT generation following successful authentication
- Rejection of incorrect login credentials
- Authentication state management in the frontend
- Logout functionality

Invalid credentials result in an authentication error rather than granting access.

### 3. Frontend Integration

The application provides browser-accessible pages for registration, login, and calculations.

**Registration Page**

Allows users to enter their account information and displays validation messages when registration fails.

**Login Page**

Allows registered users to authenticate using their username and password.

**Calculations Dashboard**

Displays the authenticated user's information and provides access to calculation functionality and calculation history.

### 4. Calculations Functionality

Authenticated users can access the calculations dashboard, select a calculation type, enter numerical values, and view calculation history.

The dashboard also provides a logout option.

## Installation and Setup

### Prerequisites

Install the following software:

- Python 3.12
- Git
- Docker Desktop
- Docker Compose

### Clone the Repository

```bash
git clone https://github.com/islamnavid/module13_is601.git
cd module13_is601
```

### Create a Virtual Environment

On macOS or Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### Configure Environment Variables

Configure the database connection, JWT secret, and other required application settings using the project's environment configuration.

Do not commit actual passwords, database credentials, or JWT secrets to GitHub.

### Start the Application

Once the database is configured and available, initialize it:

```bash
python -m app.database_init
```

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Open the application at:

`http://localhost:8000`

FastAPI's interactive API documentation is available at:

`http://localhost:8000/docs`

## Authentication API

| Endpoint | Method | Description |
|---|---|---|
| `/auth/register` | POST | Register a new user |
| `/auth/login` | POST | Authenticate a user and return a JWT |

### Registration

The registration endpoint validates user information, checks for existing accounts, hashes passwords, and stores new users in PostgreSQL.

### Login

The login endpoint verifies user credentials and returns an authentication token for valid credentials.

Invalid credentials are rejected with an HTTP 401 response.

## Automated Testing

The project uses pytest for backend testing and Playwright for browser-based end-to-end testing.

### Run Backend Tests

```bash
python -m pytest -q
```

### Install Playwright Browser

```bash
python -m playwright install chromium
```

### Run End-to-End Tests

```bash
python -m pytest tests/e2e/ -v
```

### Playwright Test Scenarios

The four required browser testing scenarios are:

1. **Successful registration:** Verifies that a user can register with valid information.
2. **Successful login:** Verifies that a registered user can authenticate and access the dashboard.
3. **Short password registration:** Verifies that the registration form rejects passwords that do not meet the minimum length requirement.
4. **Incorrect password login:** Verifies that invalid credentials produce an error message.

These tests help validate the interaction between the frontend and authentication backend.

## Docker Containerization

The application is containerized using Docker.

### Build the Docker Image

```bash
docker build -t module13:test .
```

### Docker Hub

Docker Hub repository:

`navidislam/module13_is601`

Pull the published image:

```bash
docker pull navidislam/module13_is601:latest
```

The Docker image contains the Python application and its required dependencies.

The application requires