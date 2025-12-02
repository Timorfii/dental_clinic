from functools import wraps
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g
from flask_login import LoginManager, UserMixin, login_required, logout_user, current_user, login_user
import bcrypt
from flask_sqlalchemy import SQLAlchemy
import logging
from sqlalchemy import inspect, text
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost/dental_clinic'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите в систему для доступа к этой странице.'
login_manager.login_message_category = 'info'

db = SQLAlchemy(app)
app.secret_key = os.urandom(24)

CLINICS_CONFIG = {
    'center': {
        'id': 1,
        'name': 'Центральная клиника',
        'slug': 'center',
        'path': 'clinic_center'
    },
    'north': {
        'id': 2,
        'name': 'Северная клиника',
        'slug': 'north',
        'path': 'clinic_north'
    }
}



class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='client')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    clinic_id = db.Column(db.Integer, default=1)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))


class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2))
    duration_minutes = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    clinic_id = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price else 0.0,
            'duration_minutes': self.duration_minutes,
            'is_active': self.is_active,
            'clinic_id': self.clinic_id
        }


class Clinic(db.Model):
    __tablename__ = 'clinics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    address = db.Column(db.String(500))
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



def get_clinic_name(clinic_id):
    clinic = db.session.execute(text("""
        SELECT name FROM clinics WHERE id = :clinic_id
    """), {'clinic_id': clinic_id}).fetchone()

    return clinic.name if clinic else f'Клиника #{clinic_id}'


def get_clinic_by_slug(clinic_slug):
    return CLINICS_CONFIG.get(clinic_slug, CLINICS_CONFIG['center'])


def clinic_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        clinic_slug = kwargs.get('clinic_slug')
        if clinic_slug not in ['center', 'north']:
            flash('Клиника не найдена', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)

    return decorated_function


@app.context_processor
def inject_now():
    return {'now': datetime.now}


@app.context_processor
def inject_clinics():
    clinic_slug = request.view_args.get('clinic_slug', 'center') if request.view_args else 'center'
    current_clinic = get_clinic_by_slug(clinic_slug)
    return {
        'current_clinic': current_clinic,
        'all_clinics': CLINICS_CONFIG.values()
    }


@app.context_processor
def inject_admin_clinic():
    if session.get('admin_logged_in'):
        clinic_id = session.get('admin_clinic_id', 1)
        return {
            'admin_clinic_id': clinic_id,
            'admin_clinic_name': get_clinic_name(clinic_id)
        }
    return {}


@app.route('/')
def index():
    return redirect(url_for('clinic_home', clinic_slug='center'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        clinic_slug = request.form.get('clinic_slug', 'center')

        if User.query.filter_by(username=username).first():
            return "Пользователь с таким именем уже существует", 400
        if User.query.filter_by(email=email).first():
            return "Пользователь с таким email уже существует", 400

        clinic_info = get_clinic_by_slug(clinic_slug)

        user = User(
            username=username,
            email=email,
            role='client',
            clinic_id=clinic_info['id']
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        login_user(user)

        return redirect(url_for('account', clinic_slug=clinic_slug))


    return render_template('register.html', clinics=CLINICS_CONFIG.values())


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        clinic_slug = request.form.get('clinic_slug', 'center')  # Получаем выбранную клинику

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password) and user.is_active:

            clinic_info = get_clinic_by_slug(clinic_slug)
            if user.clinic_id != clinic_info['id']:
                flash('Пользователь не зарегистрирован в этой клинике', 'error')
                return redirect(url_for('login'))

            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('account', clinic_slug=clinic_slug))
        else:
            flash('Неверное имя пользователя или пароль', 'error')
            return redirect(url_for('login'))


    return render_template('login.html', clinics=CLINICS_CONFIG.values())


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/<clinic_slug>')
def clinic_home(clinic_slug):
    clinic_info = get_clinic_by_slug(clinic_slug)
    return render_template('Main.html')



@app.route('/<clinic_slug>/AboutClinic')
def about_clinic(clinic_slug):
    clinic_info = get_clinic_by_slug(clinic_slug)
    return render_template('AboutClinic.html')


@app.route('/<clinic_slug>/Services')
def services(clinic_slug):
    clinic_info = get_clinic_by_slug(clinic_slug)
    clinic_id = clinic_info['id']

    services_list = Service.query.filter_by(
        clinic_id=clinic_id,
        is_active=True
    ).order_by(Service.name).all()

    return render_template('Services.html', services=services_list)


@app.route('/<clinic_slug>/Doctors')
def doctors(clinic_slug):
    clinic_info = get_clinic_by_slug(clinic_slug)
    clinic_id = clinic_info['id']

    doctors_list = db.session.execute(text("""
        SELECT id, first_name, last_name, position, 
               EXTRACT(YEAR FROM AGE(CURRENT_DATE, hire_date)) as experience,
               description, phone_number, email
        FROM users 
        WHERE role IN ('doctor', 'employee', 'staff') 
          AND is_active = true
          AND clinic_id = :clinic_id
          AND position IS NOT NULL
        ORDER BY experience DESC
    """), {'clinic_id': clinic_id}).fetchall()

    return render_template('Doctors.html', doctors=doctors_list)



@app.route('/<clinic_slug>/Reviews')
def reviews(clinic_slug):
    return render_template('Reviews.html')


@app.route('/<clinic_slug>/Price')
def price(clinic_slug):

    clinic_info = get_clinic_by_slug(clinic_slug)
    clinic_id = clinic_info['id']

    services_list = Service.query.filter_by(
        clinic_id=clinic_id,
        is_active=True
    ).all()

    return render_template('Price.html', services=services_list)


@app.route('/<clinic_slug>/Account')
@login_required
def account(clinic_slug):
    clinic_info = get_clinic_by_slug(clinic_slug)
    if current_user.clinic_id != clinic_info['id']:
        flash('Доступ запрещен - вы не зарегистрированы в этой клинике', 'error')
        # Перенаправляем в правильную клинику
        if current_user.clinic_id == 1:
            return redirect(url_for('account', clinic_slug='center'))
        else:
            return redirect(url_for('account', clinic_slug='north'))

    return render_template('Account.html')


@app.route('/<clinic_slug>/update_profile', methods=['POST'])
@login_required
def update_profile(clinic_slug):
    clinic_info = get_clinic_by_slug(clinic_slug)
    if current_user.clinic_id != clinic_info['id']:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('clinic_home', clinic_slug=clinic_slug))

    current_user.first_name = request.form.get('first_name', '')
    current_user.last_name = request.form.get('last_name', '')
    current_user.phone_number = request.form.get('phone_number', '')

    db.session.commit()
    flash('Профиль успешно обновлен!', 'success')
    return redirect(url_for('account', clinic_slug=clinic_slug))


@app.route('/<clinic_slug>/Make_appointment', methods=['GET', 'POST'])
@login_required
def Make_appointment(clinic_slug):
    clinic_info = get_clinic_by_slug(clinic_slug)
    clinic_id = clinic_info['id']

    if current_user.clinic_id != clinic_id:
        flash('Вы не можете записываться в эту клинику', 'error')
        if current_user.clinic_id == 1:
            return redirect(url_for('Make_appointment', clinic_slug='center'))
        else:
            return redirect(url_for('Make_appointment', clinic_slug='north'))

    if request.method == 'POST':
        service_id = request.form.get('service_id')
        doctor_id = request.form.get('doctor_id')
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')

        if not all([service_id, doctor_id, appointment_date, appointment_time]):
            flash('Заполните все поля', 'error')
            return redirect(url_for('Make_appointment', clinic_slug=clinic_slug))

        try:
            appointment_datetime_str = f"{appointment_date} {appointment_time}"
            appointment_datetime = datetime.strptime(appointment_datetime_str, '%Y-%m-%d %H:%M')
            current_datetime = datetime.now()

            if appointment_datetime <= current_datetime:
                flash('Нельзя записаться на прошедшую дату или время!', 'error')
                return redirect(url_for('Make_appointment', clinic_slug=clinic_slug))

            busy = db.session.execute(text("""
                SELECT id FROM appointments 
                WHERE employee_id = :doctor_id
                AND appointment_date = :date 
                AND appointment_time = :time
                AND status_id != 3 
                AND clinic_id = :clinic_id
            """), {
                'doctor_id': doctor_id,
                'date': appointment_date,
                'time': appointment_time,
                'clinic_id': clinic_id
            }).fetchone()

            if busy:
                flash('Это время уже занято. Выберите другое время.', 'error')
                return redirect(url_for('Make_appointment', clinic_slug=clinic_slug))

            service = Service.query.get(service_id)
            service_price = service.price if service else 0

            db.session.execute(text("""
                INSERT INTO appointments 
                (client_id, employee_id, service_id, clinic_id, appointment_date, appointment_time, 
                 duration_minutes, status_id, price, created_at)
                VALUES 
                (:client_id, :employee_id, :service_id, :clinic_id, :appointment_date, :appointment_time, 
                 :duration, :status_id, :price, :created_at)
            """), {
                'client_id': current_user.id,
                'employee_id': doctor_id,
                'service_id': service_id,
                'clinic_id': clinic_id,
                'appointment_date': appointment_date,
                'appointment_time': appointment_time,
                'duration': 60,
                'status_id': 1,
                'price': service_price,
                'created_at': datetime.now()
            })

            db.session.commit()
            flash('Запись успешно создана! Мы свяжемся с вами для подтверждения.', 'success')
            return redirect(url_for('user_appointments', clinic_slug=clinic_slug))

        except Exception as e:
            db.session.rollback()
            flash('Ошибка при записи', 'error')
            return redirect(url_for('Make_appointment', clinic_slug=clinic_slug))

    doctors = db.session.execute(text("""
        SELECT id, first_name, last_name, position 
        FROM users 
        WHERE role = 'doctor' 
          AND is_active = true
          AND clinic_id = :clinic_id
        ORDER BY first_name, last_name
    """), {'clinic_id': clinic_id}).fetchall()

    services = Service.query.filter_by(clinic_id=clinic_id, is_active=True).all()
    current_datetime = datetime.now()

    selected_doctor = request.args.get('doctor_id', '')
    selected_date = request.args.get('appointment_date', '')

    all_slots = []

    if selected_doctor and selected_date:
        time_slots = ['09:00', '10:00', '11:00', '12:00', '14:00', '15:00', '16:00', '17:00', '23:00']

        busy_slots = db.session.execute(text("""
            SELECT TO_CHAR(appointment_time, 'HH24:MI') as time
            FROM appointments 
            WHERE employee_id = :doctor_id 
            AND appointment_date = :date
            AND clinic_id = :clinic_id
            AND status_id != 3
        """), {
            'doctor_id': selected_doctor,
            'date': selected_date,
            'clinic_id': clinic_id
        }).fetchall()

        busy_times = [slot.time for slot in busy_slots]

        for slot in time_slots:
            all_slots.append({
                'time': slot,
                'available': slot not in busy_times
            })

    return render_template('Make_appointment.html',
                           services=services,
                           doctors=doctors,
                           current_date=current_datetime.strftime('%Y-%m-%d'),
                           selected_doctor=selected_doctor,
                           selected_date=selected_date,
                           all_slots=all_slots)


@app.route('/<clinic_slug>/my_appointments')
@login_required
def user_appointments(clinic_slug):
    clinic_info = get_clinic_by_slug(clinic_slug)
    clinic_id = clinic_info['id']

    if current_user.clinic_id != clinic_id:
        flash('Доступ запрещен', 'error')
        if current_user.clinic_id == 1:
            return redirect(url_for('user_appointments', clinic_slug='center'))
        else:
            return redirect(url_for('user_appointments', clinic_slug='north'))

    appointments_list = db.session.execute(text("""
        SELECT a.*, s.name as service_name 
        FROM appointments a 
        LEFT JOIN services s ON a.service_id = s.id 
        WHERE a.client_id = :user_id 
          AND a.clinic_id = :clinic_id
        ORDER BY a.appointment_date DESC
    """), {
        'user_id': current_user.id,
        'clinic_id': clinic_id
    }).fetchall()

    return render_template('my_appointments.html', appointments=appointments_list)


@app.route('/<clinic_slug>/patient_card')
@login_required
def patient_card(clinic_slug):
    clinic_info = get_clinic_by_slug(clinic_slug)
    clinic_id = clinic_info['id']

    if current_user.clinic_id != clinic_id:
        flash('Доступ запрещен', 'error')
        if current_user.clinic_id == 1:
            return redirect(url_for('patient_card', clinic_slug='center'))
        else:
            return redirect(url_for('patient_card', clinic_slug='north'))

    patient_info = db.session.execute(text("""
        SELECT id, first_name, last_name, email, phone_number, 
               date_of_birth, policy_number
        FROM users 
        WHERE id = :user_id
    """), {'user_id': current_user.id}).fetchone()

    appointments = db.session.execute(text("""
        SELECT 
            a.id,
            a.appointment_date,
            a.appointment_time,
            s.name as service_name,
            s.price,
            ast.name as status_name,
            u.first_name || ' ' || u.last_name as doctor_name,
            u.position as doctor_position,
            cmr.diagnosis,
            cmr.treatment,
            cmr.notes as doctor_notes,
            cmr.record_date
        FROM appointments a
        LEFT JOIN services s ON a.service_id = s.id
        LEFT JOIN appointment_statuses ast ON a.status_id = ast.id
        LEFT JOIN users u ON a.employee_id = u.id
        LEFT JOIN client_medical_records cmr ON cmr.appointment_id = a.id
        WHERE a.client_id = :user_id
          AND a.clinic_id = :clinic_id
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
    """), {
        'user_id': current_user.id,
        'clinic_id': clinic_id
    }).fetchall()

    return render_template('patient_card.html',
                           patient_info=patient_info,
                           appointments=appointments)


@app.route('/<clinic_slug>/doctor_dashboard')
@login_required
def doctor_dashboard(clinic_slug):
    if current_user.role not in ['doctor', 'employee', 'staff']:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('clinic_home', clinic_slug=clinic_slug))

    clinic_info = get_clinic_by_slug(clinic_slug)
    clinic_id = clinic_info['id']

    if current_user.clinic_id != clinic_id:
        flash('Вы не работаете в этой клинике', 'error')
        if current_user.clinic_id == 1:
            return redirect(url_for('doctor_dashboard', clinic_slug='center'))
        else:
            return redirect(url_for('doctor_dashboard', clinic_slug='north'))

    today = datetime.now().date()
    appointments = db.session.execute(text("""
        SELECT a.id, a.appointment_date, a.appointment_time, 
               s.name as service_name, 
               u.first_name, u.last_name, u.phone_number,
               ast.name as status_name
        FROM appointments a
        LEFT JOIN services s ON a.service_id = s.id
        LEFT JOIN users u ON a.client_id = u.id
        LEFT JOIN appointment_statuses ast ON a.status_id = ast.id
        WHERE a.employee_id = :doctor_id 
          AND a.clinic_id = :clinic_id
          AND a.appointment_date >= :today
        ORDER BY a.appointment_date, a.appointment_time
    """), {
        'doctor_id': current_user.id,
        'clinic_id': clinic_id,
        'today': today
    }).fetchall()

    return render_template('doctor_dashboard.html', appointments=appointments)


@app.route('/<clinic_slug>/doctor/appointment/<int:appointment_id>')
@login_required
def doctor_appointment_detail(clinic_slug, appointment_id):
    if current_user.role not in ['doctor', 'employee', 'staff']:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('clinic_home', clinic_slug=clinic_slug))

    clinic_info = get_clinic_by_slug(clinic_slug)
    clinic_id = clinic_info['id']

    if current_user.clinic_id != clinic_id:
        flash('Вы не работаете в этой клинике', 'error')
        if current_user.clinic_id == 1:
            return redirect(url_for('doctor_dashboard', clinic_slug='center'))
        else:
            return redirect(url_for('doctor_dashboard', clinic_slug='north'))

    appointment = db.session.execute(text("""
        SELECT a.*, 
               s.name as service_name,
               u.first_name, u.last_name, u.phone_number, u.email,
               u.date_of_birth, u.policy_number,
               ast.name as status_name,
               cmr.diagnosis, cmr.treatment, cmr.notes as doctor_notes
        FROM appointments a
        LEFT JOIN services s ON a.service_id = s.id
        LEFT JOIN users u ON a.client_id = u.id
        LEFT JOIN appointment_statuses ast ON a.status_id = ast.id
        LEFT JOIN client_medical_records cmr ON cmr.appointment_id = a.id
        WHERE a.id = :appointment_id 
          AND a.employee_id = :doctor_id
          AND a.clinic_id = :clinic_id
    """), {
        'appointment_id': appointment_id,
        'doctor_id': current_user.id,
        'clinic_id': clinic_id
    }).fetchone()

    if not appointment:
        flash('Прием не найден', 'error')
        return redirect(url_for('doctor_dashboard', clinic_slug=clinic_slug))

    return render_template('doctor_appointment_detail.html', appointment=appointment)


@app.route('/<clinic_slug>/doctor/update_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def doctor_update_appointment(clinic_slug, appointment_id):
    if current_user.role not in ['doctor', 'employee', 'staff']:
        return jsonify({'success': False, 'message': 'Доступ запрещен'})

    try:
        diagnosis = request.form.get('diagnosis', '')
        treatment = request.form.get('treatment', '')
        notes = request.form.get('doctor_notes', '')
        status_id = request.form.get('status_id')

        existing_record = db.session.execute(text("""
            SELECT id FROM client_medical_records 
            WHERE appointment_id = :appointment_id
        """), {'appointment_id': appointment_id}).fetchone()

        if existing_record:
            db.session.execute(text("""
                UPDATE client_medical_records 
                SET diagnosis = :diagnosis, treatment = :treatment, 
                    notes = :notes, record_date = CURRENT_TIMESTAMP,
                    employee_id = :doctor_id
                WHERE appointment_id = :appointment_id
            """), {
                'diagnosis': diagnosis,
                'treatment': treatment,
                'notes': notes,
                'doctor_id': current_user.id,
                'appointment_id': appointment_id
            })
        else:
            db.session.execute(text("""
                INSERT INTO client_medical_records 
                (client_id, appointment_id, employee_id, diagnosis, treatment, notes)
                SELECT client_id, :appointment_id, :doctor_id, :diagnosis, :treatment, :notes
                FROM appointments WHERE id = :appointment_id
            """), {
                'appointment_id': appointment_id,
                'doctor_id': current_user.id,
                'diagnosis': diagnosis,
                'treatment': treatment,
                'notes': notes
            })

        if status_id:
            db.session.execute(text("""
                UPDATE appointments 
                SET status_id = :status_id 
                WHERE id = :appointment_id
            """), {
                'status_id': status_id,
                'appointment_id': appointment_id
            })

        db.session.commit()
        flash('Данные приема успешно обновлены', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при обновлении: {str(e)}', 'error')

    return redirect(url_for('doctor_appointment_detail',
                            clinic_slug=clinic_slug,
                            appointment_id=appointment_id))


@app.route('/Admins/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            session['admin_logged_in'] = True
            session['admin_clinic_id'] = 1
            return redirect(url_for('admin_dashboard'))
        else:
            return "Error", 401
    return render_template('Admins/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/Admin_dashboard')
@admin_required
def admin_dashboard():
    clinics = db.session.execute(text("""
        SELECT id, name, is_active 
        FROM clinics 
        ORDER BY name
    """)).fetchall()


    selected_clinic_id = request.args.get('clinic_id', session.get('admin_clinic_id', 1))
    selected_clinic_id = int(selected_clinic_id)

    session['admin_clinic_id'] = selected_clinic_id

    return render_template('Admin_dashboard.html',
                           clinics=clinics,
                           selected_clinic_id=selected_clinic_id)


@app.route('/Admin/<table_name>')
@admin_required
def admin_manage_table(table_name):
    clinic_id = session.get('admin_clinic_id', 1)


    tables_with_clinic_id = ['services', 'appointments', 'users', 'medications', 'equipment']

    if table_name in tables_with_clinic_id:
        data = db.session.execute(text(f"""
            SELECT * FROM {table_name} 
            WHERE clinic_id = :clinic_id
        """), {'clinic_id': clinic_id}).fetchall()
    else:
        data = db.session.execute(text(f"SELECT * FROM {table_name}")).fetchall()

    columns = [column.name for column in
               db.session.execute(text(f'SELECT * FROM {table_name} LIMIT 1')).cursor.description]

    return render_template('Admins/Admin_services.html',
                           columns=columns,
                           data=data,
                           table_name=table_name,
                           clinic_id=clinic_id)


@app.route('/Admin/add/<table_name>', methods=['POST'])
@admin_required
def add_record(table_name):
    try:
        clinic_id = session.get('admin_clinic_id', 1)
        fields = []
        params = {}

        for field, value in request.form.items():
            if field and value:
                fields.append(field)
                if field == 'is_active' or field.endswith('_active'):
                    params[field] = True
                else:
                    params[field] = value

        tables_with_clinic_id = ['services', 'appointments', 'users', 'medications', 'equipment']
        if table_name in tables_with_clinic_id and 'clinic_id' not in fields:
            fields.append('clinic_id')
            params['clinic_id'] = clinic_id

        if fields:
            placeholders = [f":{field}" for field in fields]
            sql = text(f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({', '.join(placeholders)})")
            db.session.execute(sql, params)
            db.session.commit()

        return redirect(f'/Admin/{table_name}')
    except Exception as e:
        return f"Ошибка добавления: {e}"


@app.route('/<clinic_slug>/Admin/<table_name>')
@admin_required
def admin_clinic_manage_table(clinic_slug, table_name):
    clinic_info = get_clinic_by_slug(clinic_slug)
    clinic_id = clinic_info['id']

    session['admin_clinic_id'] = clinic_id

    tables_with_clinic_id = ['services', 'appointments', 'users', 'medications', 'equipment']

    if table_name in tables_with_clinic_id:
        data = db.session.execute(text(f"""
            SELECT * FROM {table_name} 
            WHERE clinic_id = :clinic_id
        """), {'clinic_id': clinic_id}).fetchall()
    else:
        data = db.session.execute(text(f"SELECT * FROM {table_name}")).fetchall()

    columns = [column.name for column in
               db.session.execute(text(f'SELECT * FROM {table_name} LIMIT 1')).cursor.description]

    return render_template('Admins/Admin_services.html',
                           columns=columns,
                           data=data,
                           table_name=table_name,
                           clinic_id=clinic_id)


@app.route('/Admin/update/<table_name>/<int:record_id>', methods=['POST'])
@admin_required
def update_record(table_name, record_id):
    try:
        clinic_id = session.get('admin_clinic_id', 1)

        updates = {}
        for key, value in request.form.items():
            if key:
                if value in ['', 'None', None]:
                    updates[key] = None
                elif key == 'is_active' or key.endswith('_active'):
                    updates[key] = value.lower() in ['true', '1', 'yes', 'on']
                elif key == 'password' and value:
                    if table_name == 'users':
                        from werkzeug.security import generate_password_hash
                        updates['password_hash'] = generate_password_hash(value)
                elif 'date' in key.lower() or 'time' in key.lower():
                    if value:
                        updates[key] = value
                    else:
                        updates[key] = None
                elif 'price' in key.lower() or 'cost' in key.lower():
                    try:
                        updates[key] = float(value) if value else None
                    except:
                        updates[key] = None
                else:
                    updates[key] = value

        if 'password' in updates:
            del updates['password']

        if updates:
            set_parts = []
            params = {'id': record_id, 'clinic_id': clinic_id}

            for key, value in updates.items():
                if value is None:
                    set_parts.append(f"{key} = NULL")
                else:
                    set_parts.append(f"{key} = :{key}")
                    params[key] = value

            set_clause = ', '.join(set_parts)

            tables_with_clinic_id = ['services', 'appointments', 'users', 'medications', 'equipment']
            if table_name in tables_with_clinic_id:
                sql = text(f"""
                    UPDATE {table_name} 
                    SET {set_clause} 
                    WHERE id = :id 
                    AND clinic_id = :clinic_id
                """)
                result = db.session.execute(sql, params)
            else:
                sql = text(f"""
                    UPDATE {table_name} 
                    SET {set_clause} 
                    WHERE id = :id
                """)
                del params['clinic_id']
                result = db.session.execute(sql, params)

            db.session.commit()

        return redirect(f'/Admin/{table_name}')
    except Exception as e:
        db.session.rollback()
        return f"Ошибка обновления: {e}"


@app.route('/Admin/delete/<table_name>/<int:record_id>', methods=['POST'])
@admin_required
def delete_record(table_name, record_id):
    try:
        clinic_id = session.get('admin_clinic_id', 1)

        tables_with_clinic_id = ['services', 'appointments', 'users', 'medications', 'equipment']
        if table_name in tables_with_clinic_id:
            sql = text(f"""
                DELETE FROM {table_name} 
                WHERE id = :id 
                AND clinic_id = :clinic_id
            """)
            db.session.execute(sql, {'id': record_id, 'clinic_id': clinic_id})
        else:
            sql = text(f"DELETE FROM {table_name} WHERE id = :id")
            db.session.execute(sql, {'id': record_id})

        db.session.commit()
        return redirect(f'/Admin/{table_name}')
    except Exception as e:
        return f"Ошибка удаления: {e}"

@app.route('/<clinic_slug>/api/available_slots')
def get_available_slots(clinic_slug):
    try:
        clinic_info = get_clinic_by_slug(clinic_slug)
        clinic_id = clinic_info['id']

        doctor_id = request.args.get('doctor_id')
        date = request.args.get('date')

        if not doctor_id or not date:
            return jsonify({'error': 'Не указаны doctor_id или date'}), 400

        all_slots = ['09:00', '10:00', '11:00', '12:00', '14:00', '15:00', '16:00', '17:00']

        busy_slots = db.session.execute(text("""
            SELECT TO_CHAR(appointment_time, 'HH24:MI') as time
            FROM appointments 
            WHERE employee_id = :doctor_id 
            AND appointment_date = :date
            AND clinic_id = :clinic_id
            AND status_id != 3
        """), {
            'doctor_id': doctor_id,
            'date': date,
            'clinic_id': clinic_id
        }).fetchall()

        busy_times = [slot.time for slot in busy_slots]

        available_slots = []
        for slot in all_slots:
            available_slots.append({
                'time': slot,
                'available': slot not in busy_times
            })

        return jsonify({
            'success': True,
            'slots': available_slots,
            'date': date,
            'doctor_id': doctor_id,
            'clinic_id': clinic_id
        })

    except Exception as e:
        logger.error(f"Error getting available slots: {e}")
        return jsonify({'error': str(e)}), 500

@app.context_processor
def inject_statuses():
    statuses = db.session.execute(text("""
        SELECT id, name FROM appointment_statuses ORDER BY id
    """)).fetchall()
    return dict(statuses=statuses)



if __name__ == '__main__':
    app.run(debug=True)