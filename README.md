# Campus Hire Backend (FinalsBackEndCampusHire)

This is the backend repository for the **Campus Hire** recruitment platform. It provides the server-side logic, database management, and APIs required to handle user authentication, job postings, and the recruitment process.

Built with **Python** and **Django**.

## 🚀 Features

- **User Management**: Handles user registration, authentication, and profiles (via `userapp` and `registration`).
- **Recruitment Logic**: Manages job listings, applications, and recruitment workflows (via `job_recruitmentapp`).
- **Media Management**: Support for uploading and serving media files (resumes, profile pictures).
- **Admin Interface**: Built-in Django admin for managing database records.

## 🛠️ Tech Stack

- **Framework**: Django (Python)
- **Database**: SQLite (default for development)
- **Dependencies**: Managed via `requirements.txt`

## 📂 Project Structure

- `job_recruitment/` - Main project configuration (settings, URLs, WSGI).
- `job_recruitmentapp/` - Core application containing logic for job posts and hiring.
- `userapp/` - Application handling user-related models and views.
- `registration/` - Custom registration logic and flows.
- `media/` - Directory for user-uploaded files.
- `manage.py` - Django's command-line utility for administrative tasks.

## 💻 Getting Started

Follow these instructions to set up the project on your local machine for development and testing.

### Prerequisites

Ensure you have the following installed:
- [Python 3.x](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)
- [Git](https://git-scm.com/downloads)

### Installation

1. **Clone the repository**
   ```bash
   git clone [https://github.com/heisenberg1122/FinalsBackEndCampusHire.git](https://github.com/heisenberg1122/FinalsBackEndCampusHire.git)
   cd FinalsBackEndCampusHire
Create a Virtual Environment It is recommended to use a virtual environment to manage dependencies.

Windows:

Bash

python -m venv venv
venv\Scripts\activate
macOS / Linux:

Bash

python3 -m venv venv
source venv/bin/activate
Install Dependencies

Bash

pip install -r requirements.txt
(Note: If the project includes Node.js dependencies as indicated by package-lock.json, you may also need to run npm install if you are working on frontend assets served by Django.)

Apply Database Migrations Initialize the database schema.

Bash

python manage.py makemigrations
python manage.py migrate
Create a Superuser (Optional) Access the admin panel by creating an admin account.

Bash

python manage.py createsuperuser
Run the Development Server

Bash

python manage.py runserver
The server will start at http://127.0.0.1:8000/.

🔗 API Endpoints
Documentation of key endpoints available in the application (Example):

Admin Panel: /admin/

Home/Index: / (Check job_recruitment/urls.py for all defined routes)

🤝 Contributors
github.com/heisenberg1122
github.com/brad-git03
github.com/NicoleAndreaBolus

License
This project is for academic/final project purposes.
