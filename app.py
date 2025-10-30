
from functools import wraps
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
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

@app.context_processor
def inject_now():
    return {'now': datetime.now}

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

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']



        if User.query.filter_by(username=username).first():
            return "Пользователь с таким именем уже существует", 400
        if User.query.filter_by(email=email).first():
            return "Пользователь с таким email уже существует", 400


        user = User(
            username=username,
            email=email,
            role='client'
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for('account'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password) and user.is_active:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('account'))
        else:
            return "Неверное имя пользователя или пароль", 401

    return render_template('login.html')


@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    current_user.first_name = request.form.get('first_name', '')
    current_user.last_name = request.form.get('last_name', '')
    current_user.phone_number = request.form.get('phone_number', '')

    db.session.commit()
    flash('Профиль успешно обновлен!', 'success')
    return redirect(url_for('account'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@login_manager.unauthorized_handler
def unauthorized():
    flash('Для доступа к этой странице необходимо войти в систему.', 'warning')
    return redirect(url_for('login'))


class DynamicTable:
    @classmethod
    def create_model(cls, table_name):
        """Создает динамическую модель для таблицы"""
        if hasattr(db.Model, table_name):
            return getattr(db.Model, table_name)

        meta = db.MetaData()
        meta.reflect(bind=db.engine)

        if table_name not in meta.tables:
            return None

        table = meta.tables[table_name]

        # Создаем динамический класс
        attrs = {'__table__': table}
        model = type(table_name, (db.Model,), attrs)
        return model


# Список всех таблиц в базе данных
def get_all_tables():
    inspector = inspect(db.engine)
    return inspector.get_table_names()


# Получить данные таблицы
def get_table_data(table_name):
    model = DynamicTable.create_model(table_name)
    if model:
        return model.query.all()
    return []


# Получить информацию о колонках таблицы
def get_table_columns(table_name):
    inspector = inspect(db.engine)
    columns = inspector.get_columns(table_name)
    return [{'name': col['name'], 'type': str(col['type'])} for col in columns]

@app.route('/Admins/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            session['admin_logged_in'] = True
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














class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10,2))
    duration_minutes = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    def to_dict(self):
        """Конвертирует объект Service в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price else 0.0,
            'duration_minutes': self.duration_minutes,
            'is_active': self.is_active
        }



@app.route('/Edit')
def edit_database():
    table_name = request.args.get('table', '')
    tables = get_all_tables()

    if table_name and table_name in tables:
        columns = get_table_columns(table_name)
        records = get_table_data(table_name)
        return render_template('Edit.html',
                               tables=tables,
                               selected_table=table_name,
                               columns=columns,
                               records=records)

    return render_template('Edit.html',
                           tables=tables,
                           selected_table=None,
                           columns=[],
                           records=[])


@app.route('/Admin/add/<table_name>', methods=['POST'])
@admin_required
def add_record(table_name):
    try:
        fields = []
        params = {}


        for field, value in request.form.items():
            if field and value:
                fields.append(field)
                if field == 'is_active' or field.endswith('_active'):
                    params[field] = True
                else:
                    params[field] = value

        if fields:
            placeholders = [f":{field}" for field in fields]
            sql = text(f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({', '.join(placeholders)})")
            db.session.execute(sql, params)
            db.session.commit()

        return redirect(f'/Admin/{table_name}')
    except Exception as e:
        return f"Ошибка добавления: {e}"

@app.route('/Admin/delete/<table_name>/<int:record_id>', methods=['POST'])
@admin_required
def admin_delete_record(table_name, record_id):
    try:
        sql = text(f"DELETE FROM {table_name} WHERE id = :record_id")

        db.session.execute(sql, {'record_id': record_id})
        db.session.commit()

        return redirect(f'/Admin/{table_name}')
    except Exception as e:
        db.session.rollback()
        return f"Ошибка удаления: {e}"


@app.route('/Edit/update/<table_name>/<int:record_id>', methods=['POST'])
def update_record(table_name, record_id):
    try:
        model = DynamicTable.create_model(table_name)
        if not model:
            return redirect(url_for('edit_database', table=table_name))

        record = model.query.get(record_id)
        if not record:
            return redirect(url_for('edit_database', table=table_name))

        for key, value in request.form.items():
            if hasattr(record, key):
                col_type = str(getattr(model, key).property.columns[0].type)

                if 'boolean' in col_type.lower():
                    setattr(record, key, key in request.form)
                elif 'integer' in col_type.lower():
                    setattr(record, key, int(value) if value else None)
                elif 'numeric' in col_type.lower() or 'decimal' in col_type.lower():
                    setattr(record, key, float(value) if value else None)
                else:
                    setattr(record, key, value)

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating record: {e}")

    return redirect(url_for('edit_database', table=table_name))


@app.route('/Edit/delete/<table_name>/<int:record_id>')
def delete_record(table_name, record_id):
    try:
        model = DynamicTable.create_model(table_name)
        if model:
            record = model.query.get(record_id)
            if record:
                db.session.delete(record)
                db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting record: {e}")

    return redirect(url_for('edit_database', table=table_name))
@app.route('/')
def index():
    return render_template('Main.html')
@app.route('/AboutClinic')
def about_clinic():
    return render_template('AboutClinic.html')

@app.route('/Services')
def services():
    return render_template('Services.html')

@app.route('/Services/<service_type>')
def services_detail(service_type):
    return render_template(f'Services/{service_type}.html', service=service_type)

@app.route('/Doctors')
def doctors():
    doctors_list = db.session.execute(text("""
        SELECT id, first_name, last_name, position, 
               EXTRACT(YEAR FROM AGE(CURRENT_DATE, hire_date)) as experience,
               description, phone_number, email
        FROM users 
        WHERE role IN ('doctor', 'employee', 'staff') 
          AND is_active = true
          AND position IS NOT NULL
        ORDER BY experience DESC
    """)).fetchall()
    return render_template('Doctors.html', doctors=doctors_list)

@app.route('/Doctors/<specialization>')
def doctors_specialization(specialization):
    return render_template(f'Doctors/{specialization}.html', specialization=specialization)

@app.route('/Reviews')
def reviews():
    return render_template('Reviews.html')

@app.route('/Price')
def price():
    return render_template('Price.html')
@app.route('/Account')
@login_required
def account():
    return render_template('Account.html')

@app.route('/Admin_dashboard')
@admin_required
def admin_dashboard():

    return render_template('Admin_dashboard.html')



@app.context_processor
def inject_services():
    services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
    return dict(services=services)





@app.route('/Admin/<table_name>')
@admin_required
def admin_services(table_name):
    data = db.session.execute(text(f"SELECT * FROM {table_name}")).fetchall()
    columns = [column.name for column in db.session.execute(text(f'SELECT * FROM {table_name} LIMIT 1')).cursor.description]


    return render_template('Admins/Admin_services.html', columns=columns, data=data, table_name=table_name)






@app.route('/Admins/Admin_services/update/<table_name>/<int:record_id>', methods=['POST'])
@admin_required
def admin_update_record(table_name, record_id):
    try:
        updates = []
        params = {}

        columns_info = get_table_columns(table_name)
        column_types = {col['name']: col['type'] for col in columns_info}

        for field_name, field_value in request.form.items():
            if field_name and field_value is not None:
                if field_name == 'id':
                    continue


                if field_value == '' or field_value == 'None':
                    if 'date' in column_types.get(field_name, '').lower():
                        field_value = None
                    elif 'integer' in column_types.get(field_name, '').lower():
                        field_value = None
                    elif 'numeric' in column_types.get(field_name, '').lower():
                        field_value = None
                    else:
                        field_value = None

                elif field_name == 'is_active' or field_name.endswith('_active'):
                    updates.append(f"{field_name} = :{field_name}")
                    params[field_name] = field_name in request.form  # True/False
                    continue

                elif ('integer' in column_types.get(field_name, '').lower() and
                      field_value not in ['', 'None']):
                    try:
                        field_value = int(field_value)
                    except (ValueError, TypeError):
                        field_value = None

                elif ('numeric' in column_types.get(field_name, '').lower() and
                      field_value not in ['', 'None']):
                    try:
                        field_value = float(field_value)
                    except (ValueError, TypeError):
                        field_value = None

                # Для дат
                elif 'date' in column_types.get(field_name, '').lower():
                    if field_value in ['', 'None']:
                        field_value = None


                updates.append(f"{field_name} = :{field_name}")
                params[field_name] = field_value

        if updates:
            params['record_id'] = record_id
            sql = text(f"UPDATE {table_name} SET {', '.join(updates)} WHERE id = :record_id")

            db.session.execute(sql, params)
            db.session.commit()

        return redirect(f'/Admin/{table_name}')
    except Exception as e:
        db.session.rollback()
        return f"Ошибка обновления: {e}"


@app.route('/Make_appointment', methods=['GET', 'POST'])
@login_required
def Make_appointment():
    if request.method == 'POST':

        service_id = request.form.get('service_id')
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')

        if not all([service_id, appointment_date, appointment_time]):
            flash('Заполните все поля', 'error')
            return redirect(url_for('Make_appointment'))

        try:
            appointment_datetime_str = f"{appointment_date} {appointment_time}"
            appointment_datetime = datetime.strptime(appointment_datetime_str, '%Y-%m-%d %H:%M')
            current_datetime = datetime.now()

            if appointment_datetime <= current_datetime:
                flash('Нельзя записаться на прошедшую дату или время!', 'error')
                return redirect(url_for('Make_appointment'))

            busy = db.session.execute(text("""
                            SELECT id FROM appointments 
                            WHERE appointment_date = :date 
                            AND appointment_time = :time
                            AND status_id != 3 
                        """), {
                'date': appointment_date,
                'time': appointment_time
            }).fetchone()

            if busy:
                flash('Это время уже занято. Выберите другое время.', 'error')
                return redirect(url_for('book_appointment'))

            db.session.execute(text("""
                INSERT INTO appointments 
                (client_id, service_id, appointment_date, appointment_time, duration_minutes, status_id, price, created_at)
                VALUES 
                (:client_id, :service_id, :appointment_date, :appointment_time, :duration, :status_id, :price, :created_at)
            """), {
                'client_id': current_user.id,
                'service_id': service_id,
                'appointment_date': appointment_date,
                'appointment_time': appointment_time,
                'duration': 60,
                'status_id': 1,
                'price': 0,
                'created_at': datetime.now()
            })

            db.session.commit()

            flash('Запись успешно создана! Мы свяжемся с вами для подтверждения.', 'success')
            return redirect(url_for('user_appointments'))

        except Exception as e:
            db.session.rollback()
            flash('Ошибка при записи', 'error')
            return redirect(url_for('Make_appointment'))

    services = Service.query.filter_by(is_active=True).all()
    current_datetime = datetime.now()
    available_times = []
    time_slots = ['09:00', '10:00', '11:00', '12:00', '14:00', '15:00', '16:00', '17:00']

    for time_slot in time_slots:
        slot_time = datetime.strptime(time_slot, '%H:%M').time()
        if current_datetime.time() < slot_time or current_datetime.date() < datetime.now().date():
            available_times.append(time_slot)

    return render_template('Make_appointment.html',
                           services=services,
                           current_date=current_datetime.strftime('%Y-%m-%d'),
                           current_time=current_datetime.strftime('%H:%M'),
                           available_times=available_times)


@app.route('/my_appointments')
@login_required
def user_appointments():

    appointments_list = db.session.execute(text("""
        SELECT a.*, s.name as service_name 
        FROM appointments a 
        LEFT JOIN services s ON a.service_id = s.id 
        WHERE a.client_id = :user_id 
        ORDER BY a.appointment_date DESC
    """), {'user_id': current_user.id}).fetchall()

    return render_template('my_appointments.html', appointments=appointments_list)


@app.route('/doctor_dashboard')
@login_required
def doctor_dashboard():
    """Главная страница врача"""
    if current_user.role not in ['doctor', 'employee', 'staff']:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))


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
        AND a.appointment_date >= :today
        ORDER BY a.appointment_date, a.appointment_time
    """), {
        'doctor_id': current_user.id,
        'today': today
    }).fetchall()

    return render_template('doctor_dashboard.html', appointments=appointments)


@app.route('/doctor/appointment/<int:appointment_id>')
@login_required
def doctor_appointment_detail(appointment_id):
    """Страница редактирования приема"""
    if current_user.role not in ['doctor', 'employee', 'staff']:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))


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
    """), {
        'appointment_id': appointment_id,
        'doctor_id': current_user.id
    }).fetchone()

    if not appointment:
        flash('Прием не найден', 'error')
        return redirect(url_for('doctor_dashboard'))

    return render_template('doctor_appointment_detail.html', appointment=appointment)


@app.route('/doctor/update_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def doctor_update_appointment(appointment_id):
    """Обновление данных приема"""
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

    return redirect(url_for('doctor_appointment_detail', appointment_id=appointment_id))



@app.context_processor
def inject_statuses():
    statuses = db.session.execute(text("""
        SELECT id, name FROM appointment_statuses ORDER BY id
    """)).fetchall()
    return dict(statuses=statuses)


@app.route('/patient_card')
@login_required
def patient_card():
    """Карта пациента"""
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
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
    """), {'user_id': current_user.id}).fetchall()

    return render_template('patient_card.html',
                           patient_info=patient_info,
                           appointments=appointments)



if __name__ == '__main__':
    app.run(debug=True)
