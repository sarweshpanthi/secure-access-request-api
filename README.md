This is a basic FastAPI project that I built to show a security focused CI/CD pipeline that has security fuctions using Github Actions.

This app simulates a simple internal access request system.
1. A user logs in
2. They get a authentication token
3. They use that token to authorize and submit an access request
4. The API checks the requested role and returns a basic risk decision

I kept the app simple on purpose so the main focus stays on the pipeline: testing, dependency scanning, secret scanning, Docker image scanning, and publishing the image to GitHub Container Registry.

The API has 3 endpoints:
- GET /health which checks if the app is running
- POST /login which logs in a demo user that I have created which returns an authentication token
-POST /access-request which submits an access request and returns the risk decision

/access-request requires the authentication token from the demo user from login, if the token is invalid (if you don't have the logins), then you will be denied access to request.

-------------------------------------- DEMO USERS ---------------------------------------------
EMAIL                   PASSWORD

low@project.com    |  lowpass
medium@project.com |  mediumpass
high@project.com   |  highpass

-----------------------------------------------------------------------------------------------

In a real system, this would use a proper IdP (such as Okta, Azure AD, Jumpcloud, etc), but for this project, I have the simple in-memory demo users listed above.

-------------------------------------- RISK ENGINE LOGIC -----------------------------------

The risk engine uses simple LEAST PRIVILEGE rules:

Requested role	                                |      Result
No justification	                            |      Rejected
admin, owner, production-write, superuser	    |      High risk
write, developer, editor	                    |      Medium risk
read-only or lower privilege roles	            |      Low risk

Example: if a user requests admin, the API marks it as high risk and requires manual review.

-----------------------------------------------------------------------------------------------

-------------------------------------- RUN IT LOCALLY --------------------------------------

Create and activate a virtual environment:

python3 -m venv venv
source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Run the app:

uvicorn app.main:app --reload

Open the API docs:

http://127.0.0.1:8000/docs

-----------------------------------------------------------------------------------------------

-------------------------------------- HOW TO USE IT --------------------------------------

1. Login first

Go to POST /login in the FastAPI docs and use one of the demo users.

Example:

{
  "email": "high@project.com",
  "password": "highpass"
}

The API will return a token:

{
  "access_token": "generated-token-value",
  "token_type": "bearer"
}

Copy the access_token.

2. Authorize

Click the Authorize button in the top right corner of the FastAPI docs and paste the token.

3. Submit an access request

Use POST /access-request.

Example:

{
  "system": "github",
  "role": "admin",
  "justification": "Need temporary access for incident response."
}

Example response:

{
  "requested_by": "high@project.com",
  "system": "github",
  "role": "admin",
  "evaluation": {
    "risk": "high",
    "decision": "manual_review_required",
    "reason": "Privileged access requires manual review."
  }
}
----------------------------------------------------------------------------

-------------------------------------- Run Tests --------------------------------------
pytest

The tests cover login, invalid login, protected access requests, missing tokens, invalid tokens, and the risk engine logic.

-------------------------------------- Run with Docker --------------------------------------

Build the image:

docker build -t secure-access-request-api .

Run the container:

docker run -p 8000:8000 secure-access-request-api

Then open:

http://127.0.0.1:8000/health
-----------------------------------------------------------------------------------------------

-------------------------------------- Published Docker Image ---------------------------------

The Docker image is published to GitHub Container Registry by the GitHub Actions publish workflow:

ghcr.io/sarweshpanthi/secure-access-request-api:latest

For this challenge, publishing the image to GHCR is my deploy step.

-----------------------------------------------------------------------------------------------

-------------------------------------- GitHub Actions --------------------------------------

This repo has two workflows.

1. CI - Test and Security Scan

Runs on pushes and pull requests to main.

It does:

installs dependencies
runs tests with pytest
checks Python dependencies with pip-audit
scans for secrets with gitleaks

2. Docker Build, Scan, and Publish

Runs on pushes to main.

It does:

builds the Docker image
scans the image with Trivy
publishes the image to GitHub Container Registry

-------------------------------------- Security Choices --------------------------------------

The main security idea in the app is that the user does not get to type who they are in the access request. They log in first, get a token, and the API uses that token to identify the requester.

The pipeline also adds security checks before the image is published:

pip-audit checks for vulnerable Python dependencies
gitleaks checks for accidentally committed secrets
Trivy scans the Docker image
tests make sure the login and access request behavior does not break

-------------------------------------- WHAT I WOULD IMPROVE NEXT ------------------------------

If I was taking this to production, I would add:

1. hashed passwords instead of plain demo passwords
2. a real database for users and access requests
3. Logs of who requested access to what & the specific time stamps, as well as who approved/rejected it
4. Token expiration
5. proper RBAC roles for requesters, managers, and reviewers
6. a real identity provider like Okta or Azure AD

-------------------------------------- AI USAGE --------------------------------------

I used AI to help plan the repo structure, draft some workflow examples, and troubleshoot GitHub Actions errors. I tested the app locally and validated the workflows in GitHub Actions.
