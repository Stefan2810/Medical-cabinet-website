import pyodbc
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection function
def get_db_connection():
    logging.info("Establishing database connection...")
    try:
        conn = pyodbc.connect(
            r'DRIVER={ODBC Driver 11 for SQL Server};'
            r'SERVER=STEFAN\SQLEXPRESS;'
            r'DATABASE=TemaBD;'
            r'Trusted_Connection=yes;'
        )
        logging.info("Database connection established successfully.")
        return conn
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        raise

# Authenticate patient
def authenticate_patient(name, patient_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        logging.info(f"Authenticating patient with name: '{name}', ID: '{patient_id}'")

        cursor.execute("""
                SELECT * FROM Pacienti 
                WHERE LTRIM(RTRIM(LOWER(Nume))) = LTRIM(RTRIM(LOWER(?))) 
                AND ID_pacient = ?
            """, (name, patient_id))

        user = cursor.fetchone()
        logging.info(f"Patient authentication query result: {user}")
        return user
    except Exception as e:
        logging.error(f"Error authenticating patient: {e}")
        return None
    finally:
        if conn:
            conn.close()

# Authenticate doctor
def authenticate_doctor(name, doctor_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        logging.info(f"Authenticating doctor with name: '{name}', ID: '{doctor_id}'")

        cursor.execute("""
                SELECT * FROM Medici 
                WHERE LTRIM(RTRIM(LOWER(Nume))) = LTRIM(RTRIM(LOWER(?))) 
                AND ID_medic = ?
            """, (name, doctor_id))

        user = cursor.fetchone()
        logging.info(f"Doctor authentication query result: {user}")
        return user
    except Exception as e:
        logging.error(f"Error authenticating doctor: {e}")
        return None
    finally:
        if conn:
            conn.close()

def authenticate_admin(name, admin_id):
    conn=None
    try:
        conn=get_db_connection()
        cursor=conn.cursor()
        logging.info(f"Authenticating doctor with name: '{name}', ID: '{admin_id}'")
        cursor.execute ("""
                        SELECT * FROM Administrator 
                        WHERE LTRIM(RTRIM(LOWER(Nume))) = LTRIM(RTRIM(LOWER(?)))
                        AND ID_admin = ?
                        """,(name,admin_id)
                        ) 
        user = cursor.fetchone()
        logging.info(f"Admin authentication query result: {user}")
        return user
    except Exception as e:
        logging.error(f"Error authenticating admin: {e}")
        return None
    finally:
        if conn:
            conn.close()

# Get all patients
def get_all_patients():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID_pacient, Nume, CNP, Email, Nr_telefon, Adresa FROM Pacienti")
        patients = cursor.fetchall()
        logging.info(f"Fetched {len(patients)} patients.")
        return patients
    except Exception as e:
        logging.error(f"Error fetching patients: {e}")
        return []
    finally:
        if conn:
            conn.close()

# Get all doctors
def get_all_doctors():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID_medic, Nume, CNP, Email, Nr_telefon, Program FROM Medici")
        doctors = cursor.fetchall()
        logging.info(f"Fetched {len(doctors)} doctors.")
        return doctors
    except Exception as e:
        logging.error(f"Error fetching doctors: {e}")
        return []
    finally:
        if conn:
            conn.close()

# Insert a patient
def insert_patient(name, cnp, email, phone, address):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        logging.info(f"Inserting patient: Name={name}, CNP={cnp}, Email={email}, Phone={phone}, Address={address}")

        cursor.execute("""
            INSERT INTO Pacienti (Nume, CNP, Email, Nr_telefon, Adresa)
            VALUES (?, ?, ?, ?, ?)
        """, (name, cnp, email, phone, address))

        conn.commit()
        logging.info(f"Patient {name} added successfully.")
    except Exception as e:
        logging.error(f"Error inserting patient: {e}")
        raise
    finally:
        if conn:
            conn.close()

# Insert a doctor
def insert_doctor(name, cnp, email, phone, program):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Medici (Nume, CNP, Email, Nr_telefon, Program)
            VALUES (?, ?, ?, ?, ?)
        """, (name, cnp, email, phone, program))
        conn.commit()
        logging.info(f"Doctor {name} added successfully.")
    except Exception as e:
        logging.error(f"Error inserting doctor: {e}")
        raise
    finally:
        if conn:
            conn.close()

# Fetch patient appointments
def get_patient_appointments(patient_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.ID_programare, m.Nume AS Medic, p.Data 
            FROM Programari p
            INNER JOIN Medici m ON p.ID_medic = m.ID_medic
            WHERE p.ID_pacient = ?
            ORDER BY p.Data
        """, (patient_id,))
        appointments = cursor.fetchall()
        logging.info(f"Fetched {len(appointments)} appointments for patient ID {patient_id}.")
        return appointments
    except Exception as e:
        logging.error(f"Error fetching patient appointments: {e}")
        return []
    finally:
        if conn:
            conn.close()

# Fetch doctor schedule
def get_doctor_schedule(doctor_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.ID_programare, pa.Nume AS Pacient, p.Data 
            FROM Programari p
            INNER JOIN Pacienti pa ON p.ID_pacient = pa.ID_pacient
            WHERE p.ID_medic = ?
            ORDER BY p.Data
        """, (doctor_id,))
        schedule = cursor.fetchall()
        logging.info(f"Fetched {len(schedule)} schedule entries for doctor ID {doctor_id}.")
        return schedule
    except Exception as e:
        logging.error(f"Error fetching schedule for doctor ID {doctor_id}: {e}")
        return []
    finally:
        if conn:
            conn.close()

# Fetch consultations by doctor
def get_doctor_consultations(doctor_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.ID_consultatie, pa.Nume AS Pacient, c.Concluzii 
            FROM Consultatii c
            INNER JOIN Programari p ON c.ID_programare = p.ID_programare
            INNER JOIN Pacienti pa ON p.ID_pacient = pa.ID_pacient
            WHERE p.ID_medic = ?
            ORDER BY c.ID_consultatie
        """, (doctor_id,))
        consultations = cursor.fetchall()
        logging.info(f"Fetched {len(consultations)} consultations for doctor ID {doctor_id}.")
        return consultations
    except Exception as e:
        logging.error(f"Error fetching consultations for doctor ID {doctor_id}: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_patient_profile(patient_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            SELECT ID_pacient, Nume, CNP, Email, Nr_telefon, Adresa 
            FROM Pacienti
            WHERE ID_pacient = ?
        """
        cursor.execute(query, (patient_id,))
        result = cursor.fetchone()
        return result
    except Exception as e:
        logging.error(f"Error in get_patient_profile: {e}")
        return None
    finally:
        conn.close()

# Update patient email
def update_patient_email(patient_id, new_email):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Pacienti
            SET Email = ?
            WHERE ID_pacient = ?
        """, (new_email, patient_id))
        conn.commit()
        logging.info(f"Updated email for patient ID {patient_id} to {new_email}.")
    except Exception as e:
        logging.error(f"Error updating email for patient ID {patient_id}: {e}")
        raise
    finally:
        if conn:
            conn.close()

# Update patient details
def update_patient(patient_id, name, cnp, email, phone, address):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Pacienti
            SET Nume = ?, CNP = ?, Email = ?, Nr_telefon = ?, Adresa = ?
            WHERE ID_pacient = ?
        """, (name, cnp, email, phone, address, patient_id))
        conn.commit()
        logging.info(f"Updated patient with ID {patient_id}")
    except Exception as e:
        logging.error(f"Error updating patient: {e}")
        raise
    finally:
        if conn:
            conn.close()

# Delete patient
def delete_patient(patient_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Pacienti WHERE ID_pacient = ?", (patient_id,))
        conn.commit()
        logging.info(f"Deleted patient with ID {patient_id}")
    except Exception as e:
        logging.error(f"Error deleting patient: {e}")
        raise
    finally:
        if conn:
            conn.close()

# Update doctor details
def update_doctor(doctor_id, name, email, phone, program):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Medici
            SET Nume = ?, Email = ?, Nr_telefon = ?, Program = ?
            WHERE ID_medic = ?
        """, (name, email, phone, program, doctor_id))
        conn.commit()
        logging.info(f"Updated doctor with ID {doctor_id}")
    except Exception as e:
        logging.error(f"Error updating doctor: {e}")
        raise
    finally:
        if conn:
            conn.close()

# Delete doctor
def delete_doctor(doctor_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Medici WHERE ID_medic = ?", (doctor_id,))
        conn.commit()
        logging.info(f"Deleted doctor with ID {doctor_id}")
    except Exception as e:
        logging.error(f"Error deleting doctor: {e}")
        raise
    finally:
        if conn:
            conn.close()

# Fetch all patients with their last consultation
def get_patients_last_consultation():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            SELECT 
                pa.Nume, 
                c.Concluzii,
                c.ID_consultatie AS Ultima_Consultatie
            FROM Pacienti pa
            INNER JOIN Programari p ON pa.ID_pacient = p.ID_pacient
            INNER JOIN Consultatii c ON p.ID_programare = c.ID_programare
            WHERE c.ID_consultatie = (
                SELECT MAX(c2.ID_consultatie)
                FROM Consultatii c2
                INNER JOIN Programari p2 ON c2.ID_programare = p2.ID_programare
                WHERE p2.ID_pacient = pa.ID_pacient
            )
        """
        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            print("No results in get_patients_last_consultation")
        logging.info(f"Fetched last consultations: {results}")
        return results
    except Exception as e:
        logging.error(f"Error in get_patients_last_consultation: {e}")
        return []
    finally:
        conn.close()


# Fetch all doctors and their number of consultations
def get_doctors_consultation_count():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.Nume AS Medic, COUNT(c.ID_consultatie) AS Nr_Consultatii
            FROM Medici m
            INNER JOIN Programari p ON m.ID_medic = p.ID_medic
            INNER JOIN Consultatii c ON p.ID_programare = c.ID_programare
            GROUP BY m.Nume
        """)
        results = cursor.fetchall()
        if not results:
            print("No resoult in get_doctors_consultation_count")
        logging.info(f"Fetched {len(results)} doctors with their consultation counts.")
        return results
    except Exception as e:
        logging.error(f"Error fetching doctors' consultation counts: {e}")
        return []
    finally:
        if conn:
            conn.close()

# Fetch all patients who visited a specific doctor
def get_patients_by_doctor(doctor_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT DISTINCT pa.Nume AS Pacient
            FROM Pacienti pa
            WHERE pa.ID_pacient IN (
                SELECT p.ID_pacient
                FROM Programari p
                WHERE p.ID_medic = ?
            )
        """
        cursor.execute(query, (doctor_id,))
        results = cursor.fetchall()

        if not results:
            print("No results in get_patients_by_doctor")
        logging.info(f"Fetched {len(results)} patients for doctor ID {doctor_id}.")
        return results
    except Exception as e:
        logging.error(f"Error fetching patients for doctor ID {doctor_id}: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_total_users():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT (
                (SELECT COUNT(*) FROM Pacienti) +
                (SELECT COUNT(*) FROM Medici)
            ) AS TotalUtilizatori
        """
        cursor.execute(query)
        result = cursor.fetchone()

        if result:
            total_users = result.TotalUtilizatori
            logging.info(f"Total number of users: {total_users}")
            return total_users
        else:
            logging.warning("No results in get_total_users.")
            return 0
    except Exception as e:
        logging.error(f"Error fetching total users: {e}")
        return 0
    finally:
        if conn:
            conn.close()

def get_most_requested_doctors():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Subcerere pentru numărul maxim de programări
        query = """
            WITH MaxProgramari AS (
                SELECT COUNT(*) AS NrProgramari, ID_medic
                FROM Programari
                GROUP BY ID_medic
            )
            SELECT m.Nume, mp.NrProgramari
            FROM MaxProgramari mp
            INNER JOIN Medici m ON m.ID_medic = mp.ID_medic
            WHERE mp.NrProgramari = (
                SELECT MAX(NrProgramari) FROM MaxProgramari
            )
        """
        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            logging.warning("No doctors found.")
            return {"message": "Nu există medici cu programări."}

        if len(results) == 1:
            # Dacă există un singur medic cu cele mai multe programări
            doctor = {
                "Nume": results[0].Nume,
                "NrProgramari": results[0].NrProgramari
            }
            logging.info(f"Most requested doctor: {doctor['Nume']} with {doctor['NrProgramari']} appointments.")
            return {"single": doctor}
        else:
            # Dacă există mai mulți medici cu același număr maxim de programări
            doctors = [{"Nume": row.Nume, "NrProgramari": row.NrProgramari} for row in results]
            logging.info(f"Multiple doctors are equally requested: {[d['Nume'] for d in doctors]}")
            return {"multiple": doctors}

    except Exception as e:
        logging.error(f"Error fetching most requested doctors: {e}")
        return {"message": "Eroare la preluarea medicilor."}
    finally:
        if conn:
            conn.close()

def update_appointment_datetime(appointment_id, doctor_id, new_date, new_time):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifică și actualizează programarea
        query = """
            UPDATE Programari
            SET Data = ?
            WHERE ID_programare = ?
            AND ID_medic = (
                SELECT ID_medic FROM Programari WHERE ID_programare = ?
            )
        """
        # Formatează data și ora pentru baza de date
        new_datetime = f"{new_date} {new_time}:00"  # Format `YYYY-MM-DD HH:MM:SS`
        cursor.execute(query, (new_datetime, appointment_id, appointment_id))
        conn.commit()

        if cursor.rowcount > 0:
            logging.info(f"Updated appointment ID {appointment_id} to {new_datetime}.")
        else:
            logging.warning(f"Appointment ID {appointment_id} not found or does not belong to doctor ID {doctor_id}.")
    except Exception as e:
        logging.error(f"Error updating appointment datetime: {e}")
        raise
    finally:
        if conn:
            conn.close()

def get_inactive_patients_since_last_year():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query SQL
        query = """
            SELECT p.ID_pacient, p.Nume, (select pr.Data from Programari pr where pr.ID_pacient=p.ID_pacient)as DataUltimeiProgramari
            FROM Pacienti p
            WHERE NOT EXISTS (
                SELECT 1
                FROM Programari pr
                WHERE pr.ID_pacient = p.ID_pacient
                  AND YEAR(pr.Data) > YEAR(GETDATE()) - 1   
            );
        """
        cursor.execute(query)
        results = cursor.fetchall()

        logging.info(f"Found {len(results)} inactive patients since last year.")
        return results
    except Exception as e:
        logging.error(f"Error fetching inactive patients: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_active_patients():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query SQL
        query = """
            SELECT p.ID_pacient, p.Nume, (select pr.Data from Programari pr where pr.ID_pacient=p.ID_pacient)as DataUltimeiProgramari
            FROM Pacienti p
            WHERE EXISTS (
                SELECT 1
                FROM Programari pr
                WHERE pr.ID_pacient = p.ID_pacient
                  AND YEAR(pr.Data) > YEAR(GETDATE()) - 1
            );
        """
        cursor.execute(query)
        results = cursor.fetchall()

        logging.info(f"Found {len(results)} inactive patients since last year.")
        return results
    except Exception as e:
        logging.error(f"Error fetching inactive patients: {e}")
        return []
    finally:
        if conn:
            conn.close()