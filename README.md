# Medical System Web Application

## Project Overview
This is a **Flask-based Medical System Web Application** that provides role-based access to patients, doctors, and administrators. The system allows users to:
- **Patients**: View their appointments and update their profile.
- **Doctors**: Manage their consultation schedules and view patient details.
- **Admins**: Manage users (patients and doctors), view consultation data, and monitor system activity.

## Tech Stack
- **Backend**: [Flask](https://flask.palletsprojects.com/) (Python Web Framework)
- **Frontend**: HTML, CSS, JavaScript, [Jinja2](https://jinja.palletsprojects.com/)
- **Database**: Microsoft SQL Server (via [pyodbc](https://github.com/mkleehammer/pyodbc))
- **Logging**: Python 'logging' module
- **Deployment**: Local environment with Flask

---

## Project Structure
-  Main Flask application --> app.py
-  Database connection and queries --> db_quereis.py
-  Frontend HTML templates --> templates
-  Admin Dashboard -- admin.html  
-  Doctor Dashboard -- doctor.html
-  Login Page -- login.html
-  Patient Dashboard -- patient.html
-  Common Home Page -- home.html


---

## Features & Functionality
- # Authentication System
  Patients, Doctors, and Admins can log in through /login.
  The session is maintained using Flask-Session.
- # Patient Features
  View personal appointments.
  Update email via profile settings.
- # Doctor Features
  View all their scheduled consultations.
  Modify consultation schedules.
- # Admin Features
  Add, update, or delete doctors and patients.
  View statistics like inactive patients, total users, and recent consultations.

---

## Database Scheme Overview
This project connects to Microsoft SQL Server and uses the following key tables:

Pacienti (Patients)
Medici (Doctors)
Programari (Appointments)
Consultatii (Consultations)
Administrator (Admins)

# To-Do & Future Improvements
- Implement User Authentication & Session Management.
- Implement Email Notifications for upcoming appointments.
- Add support for multi-language UI.
