from flask import Flask, render_template, request, redirect, url_for, session
import db_queries as db
import logging
import os
from db_queries import get_patients_last_consultation
from db_queries import get_doctors_consultation_count
from db_queries import get_patients_by_doctor

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Admin authentication
def authenticate_admin(username, password):
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

# Routes
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    context = {}
    user_type = request.form['user_type'].strip().lower()
    name = request.form['name'].strip()
    user_id = request.form['user_id'].strip()

    logging.info(f"Login attempt by {name} as {user_type}")

    if user_type == 'patient':
        user = db.authenticate_patient(name, user_id)
        logging.info(f"Patient authentication result: {user}")
        context['last_consultations'] = get_patients_last_consultation()
        if user:
            session['user_type'] = 'patient'
            session['user_id'] = user.ID_pacient
            session['user_name'] = user.Nume
            return redirect(url_for('patient_home'))
    elif user_type == 'doctor':
        user = db.authenticate_doctor(name, user_id)
        logging.info(f"Doctor authentication result: {user}")
        if user:
            session['user_type'] = 'doctor'
            session['user_id'] = user.ID_medic
            session['user_name'] = user.Nume
            consultation_counts = get_doctors_consultation_count()
            doctor_consultations = [{'name': row[0], 'count': row[1]} for row in consultation_counts if row[0].strip().lower() == user.Nume.strip().lower()]
            session['consultation_counts'] = doctor_consultations
            logging.info(f"Filtered consultations for {user.Nume}: {doctor_consultations}")
            return redirect(url_for('doctor_home'))
    elif user_type == 'admin':
        user = db.authenticate_admin(name, user_id)
        logging.info(f"Admin authentication result: {user}")
        context['doctors'] = db.get_all_doctors()
        if user:
            session['user_type'] = 'admin'
            session['user_id'] = user.ID_admin
            session['user_name'] = user.Nume
            return redirect(url_for('admin_home'))
        else:
            logging.warning(f"Admin login failed for {name}.",)
            return "Invalid admin credentials. Please try again."

    logging.warning("Invalid login credentials.")
    doctors = get_doctors_consultation_count()
    patients = get_patients_last_consultation()
    pc=get_patients_by_doctor(session['user_id'])
    if not doctors:
        logging.warning("No doctors' consultation counts found.")
    else:
        logging.info(f"Doctors' consultation counts: {doctors}")

    if not patients:
        logging.warning("No patients' last consultations found.")
    else:
        logging.info(f"Patients' last consultations: {patients}")
    if not pc:
        logging.warning("No patients for doctor.")
    else:
        logging.info(f"Patients for doc: {pc}")


    return "Invalid login credentials. Please try again."


@app.route('/patient/home')
def patient_home():
    data=db.get_most_requested_doctors()
    if 'user_type' not in session or session['user_type'] != 'patient':
        return redirect(url_for('index'))
    return render_template('home.html', user_name=session['user_name'], user_type='patient',data=data)

@app.route('/doctor/home')
def doctor_home():
    if 'user_type' not in session or session['user_type'] != 'doctor':
        return redirect(url_for('index'))
    consultation_counts = get_doctors_consultation_count()
    doctor_id = session.get('user_id')  # ID-ul doctorului din sesiune
    patients = db.get_patients_by_doctor(doctor_id)
    if not patients:
        logging.info(f"No patients found for doctor ID {doctor_id}.")
    logging.info(f"Transmitting consultation counts to template: {consultation_counts}")
    return render_template('home.html', consultation_counts=consultation_counts, patients=patients, user_name=session['user_name'], user_type='doctor')

@app.route('/admin/home', methods=['GET', 'POST'])
def admin_home():
    count=db.get_total_users()
    consultations = get_patients_last_consultation()
    inactive=db.get_inactive_patients_since_last_year()
    active=db.get_active_patients()
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Handle form submissions for adding, updating, or deleting patients/doctors
        action = request.form.get('action')
        if action == 'add_patient':
            # Add new patient
            name = request.form.get('name')
            cnp = request.form.get('cnp')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')

            try:
                db.insert_patient(name, cnp, email, phone, address)
                logging.info(f"Added new patient: {name}")
            except Exception as e:
                logging.error(f"Error adding patient: {e}")
                return "An error occurred while adding the patient. Please try again later."

        elif action == 'add_doctor':
            # Add new doctor
            name = request.form.get('name')
            specialization = request.form.get('specialization')
            email = request.form.get('email')
            phone = request.form.get('phone')

            try:
                db.insert_doctor(name, specialization, email, phone)
                logging.info(f"Added new doctor: {name}")
            except Exception as e:
                logging.error(f"Error adding doctor: {e}")
                return "An error occurred while adding the doctor. Please try again later."

        elif action == 'update_patient':
            # Update patient information
            patient_id = request.form.get('id')
            name = request.form.get('name')
            cnp = request.form.get('cnp')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')

            try:
                db.update_patient(patient_id, name, cnp, email, phone, address)
                logging.info(f"Updated patient ID {patient_id}")
            except Exception as e:
                logging.error(f"Error updating patient ID {patient_id}: {e}")
                return "An error occurred while updating the patient. Please try again later."

        elif action == 'update_doctor':
            # Update doctor information
            doctor_id = request.form.get('id')
            name = request.form.get('name')
            specialization = request.form.get('specialization')
            email = request.form.get('email')
            phone = request.form.get('phone')

            try:
                db.update_doctor(doctor_id, name, specialization, email, phone)
                logging.info(f"Updated doctor ID {doctor_id}")
            except Exception as e:
                logging.error(f"Error updating doctor ID {doctor_id}: {e}")
                return "An error occurred while updating the doctor. Please try again later."

        elif action == 'delete_patient':
            # Delete patient
            patient_id = request.form.get('id')
            try:
                db.delete_patient(patient_id)
                logging.info(f"Deleted patient ID {patient_id}")
            except Exception as e:
                logging.error(f"Error deleting patient ID {patient_id}: {e}")
                return "An error occurred while deleting the patient. Please try again later."

        elif action == 'delete_doctor':
            # Delete doctor
            doctor_id = request.form.get('id')
            try:
                db.delete_doctor(doctor_id)
                logging.info(f"Deleted doctor ID {doctor_id}")
            except Exception as e:
                logging.error(f"Error deleting doctor ID {doctor_id}: {e}")
                return "An error occurred while deleting the doctor. Please try again later."

        # Redirect to the admin home page after handling POST request
        return redirect(url_for('admin_home'))

    # For GET requests, fetch all patients and doctors
    try:
        patients = db.get_all_patients()
        doctors = db.get_all_doctors()
    except Exception as e:
        logging.error(f"Error fetching data for admin dashboard: {e}")
        patients = []
        doctors = []

    return render_template('admin.html', user_name=session['user_name'], patients=patients, doctors=doctors,total_users=count,consultations=consultations,inactive=inactive,active=active)

@app.route('/patient/view')
def patient_view():
    if 'user_type' not in session or session['user_type'] != 'patient':
        return redirect(url_for('index'))
    try:
        appointments = db.get_patient_appointments(session['user_id'])
    except Exception as e:
        logging.error(f"Error fetching appointments: {e}")
        return "An error occurred while fetching appointments. Please try again later."
    return render_template('patient.html', appointments=appointments)

@app.route('/patient/profile', methods=['GET', 'POST'])
def patient_profile():
    if 'user_type' not in session or session['user_type'] != 'patient':
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Handle email update
        new_email = request.form.get('new_email')
        if not new_email:
            return "Invalid email. Please try again."
        
        try:
            db.update_patient_email(session['user_id'], new_email)
            logging.info(f"Updated email for patient ID {session['user_id']} to {new_email}.")
            return redirect(url_for('patient_profile'))
        except Exception as e:
            logging.error(f"Error updating email for patient ID {session['user_id']}: {e}")
            return "An error occurred while updating the email. Please try again later."
    
    # For GET requests, fetch and display the profile
    try:
        profile = db.get_patient_profile(session['user_id'])
    except Exception as e:
        logging.error(f"Error fetching patient profile: {e}")
        return "An error occurred while fetching the profile. Please try again later."

    return render_template('patient_profile.html', profile=profile)


@app.route('/doctor/view')
def doctor_view():
    if 'user_type' not in session or session['user_type'] != 'doctor':
        return redirect(url_for('index'))
    try:
        consultations = db.get_doctor_consultations(session['user_id'])
        if not consultations:
            return render_template('doctor.html', consultations=[], message="No consultations found.")
    except Exception as e:
        logging.error(f"Error fetching consultations for doctor ID {session['user_id']}: {e}")
        return "An error occurred while fetching consultations. Please try again later."
    return render_template('doctor.html', consultations=consultations)


@app.route('/doctor/schedule', methods=['GET', 'POST'])
def doctor_schedule():
    if 'user_type' not in session or session['user_type'] != 'doctor':
        return redirect(url_for('index'))

    try:
        doctor_id = session['user_id']
        conn = db.get_db_connection()

        # Dacă cererea este POST, actualizează programarea
        if request.method == 'POST':
            appointment_id = request.form.get('appointment_id')
            new_date = request.form.get('new_date')
            new_time = request.form.get('new_time')

            try:
                db.update_appointment_datetime(appointment_id, doctor_id, new_date, new_time)
                logging.info(f"Appointment {appointment_id} updated by doctor ID {doctor_id}.")
                return redirect(url_for('doctor_schedule'))
            except Exception as e:
                logging.error(f"Error updating appointment {appointment_id}: {e}")
                return "An error occurred while updating the appointment."

        # Dacă cererea este GET, afișează programările
        schedule = db.get_doctor_schedule(doctor_id)
        return render_template('doctor_schedule.html', schedule=schedule)

    except Exception as e:
        logging.error(f"Error fetching schedule for doctor ID {session['user_id']}: {e}")
        return "An error occurred while fetching the schedule. Please try again later."


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
@app.route('/admin/modify_patient', methods=['POST'])
def modify_patient():
    try:
        patient_id = request.form['id']
        name = request.form['name']
        cnp = request.form['cnp']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        db.update_patient(patient_id, name, cnp, email, phone, address)
        logging.info(f"Modified patient with ID {patient_id}")
        return redirect(url_for('admin_home'))
    except Exception as e:
        logging.error(f"Error modifying patient: {e}")
        return "An error occurred while modifying the patient. Please try again later."



# Delete a patient
@app.route('/admin/delete_patient', methods=['POST'])
def delete_patient():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('index'))
    
    try:
        patient_id = request.form.get('id')
        db.delete_patient(patient_id)
        logging.info(f"Deleted patient with ID {patient_id}")
        return redirect(url_for('admin_home'))
    except Exception as e:
        logging.error(f"Error deleting patient: {e}")
        return "An error occurred while deleting the patient. Please try again later."


# Modify a doctor
@app.route('/admin/modify_doctor', methods=['POST'])
def modify_doctor():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('index'))
    
    try:
        doctor_id = request.form.get('id')
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        program = request.form.get('program')

        db.update_doctor(doctor_id, name, email, phone, program)
        logging.info(f"Modified doctor with ID {doctor_id}")
        return redirect(url_for('admin_home'))
    except Exception as e:
        logging.error(f"Error modifying doctor: {e}")
        return "An error occurred while updating the doctor. Please try again later."


# Delete a doctor
@app.route('/admin/delete_doctor', methods=['POST'])
def delete_doctor():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('index'))
    
    try:
        doctor_id = request.form.get('id')
        db.delete_doctor(doctor_id)
        logging.info(f"Deleted doctor with ID {doctor_id}")
        return redirect(url_for('admin_home'))
    except Exception as e:
        logging.error(f"Error deleting doctor: {e}")
        return "An error occurred while deleting the doctor. Please try again later."

@app.route('/admin/add_patient', methods=['POST'])
def add_patient():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('index'))
    
    name = request.form['name'][:30]  # Truncate to 30 characters
    cnp = request.form['cnp'][:13]  # Ensure it's exactly 13 characters
    email = request.form['email'][:30]  # Truncate to 30 characters
    phone = request.form['phone'][:10]  # Ensure it's exactly 10 characters
    address = request.form['address'][:50]  # Truncate to 50 characters

    if len(cnp) != 13 or len(phone) != 10:
        return "Invalid CNP or phone number length. Please try again."

    try:
        db.insert_patient(name, cnp, email, phone, address)
        logging.info(f"Added patient {name}.")
        return redirect(url_for('admin_home'))
    except Exception as e:
        logging.error(f"Error adding patient: {e}")
        return "An error occurred while adding the patient. Please try again later."

@app.route('/admin/add_doctor', methods=['POST'])
def add_doctor():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('index'))
    
    try:
        name = request.form['name']
        cnp = request.form['cnp']
        email = request.form['email']
        phone = request.form['phone']
        program = request.form['program']
        
        db.insert_doctor(name, cnp, email, phone, program)
        logging.info(f"Doctor {name} added successfully.")
        return redirect(url_for('admin_home'))
    except Exception as e:
        logging.error(f"Error adding doctor: {e}")
        return "An error occurred while adding the doctor. Please try again later."

if __name__ == "__main__":
    app.run(debug=True)