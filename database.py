# database.py
import sqlite3
import pandas as pd
import hashlib
from datetime import datetime

def init_db():
    """Дерекқорды бастапқы жасау"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    c = conn.cursor()
    
    # Мұғалімдер кестесі
    c.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            full_name TEXT,
            school TEXT,
            city TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Сыныптар кестесі
    c.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            subject TEXT,
            grade_level TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES teachers (id)
        )
    ''')
    
    # Оқушылар кестесі (жаңартылған версия - логин/пароль бар)
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            student_code TEXT UNIQUE,
            username TEXT UNIQUE,  -- ЖАҢА: логин
            password TEXT NOT NULL, -- ЖАҢА: пароль
            grade_points INTEGER DEFAULT 0,
            ai_usage_hours REAL DEFAULT 0,
            python_level TEXT DEFAULT 'Бастапқы',
            last_activity DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (class_id) REFERENCES classes (id)
        )
    ''')
    
    # Student tasks кестесі
    # app.py - init_db() функциясында students_tasks кестесін жаңарту
    c.execute('''
        CREATE TABLE IF NOT EXISTS student_tasks (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           teacher_id INTEGER NOT NULL,
           student_id INTEGER NOT NULL,
           class_id INTEGER NOT NULL,
           task_name TEXT NOT NULL,
           task_description TEXT,
           task_file BLOB,
           file_type TEXT,
           due_date TIMESTAMP,
           status TEXT DEFAULT 'Жіберілмеді',
           points INTEGER DEFAULT 0,
           feedback TEXT,
           assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
           completed_date TIMESTAMP,
           student_answer_text TEXT,  # <<< ЖАҢА: оқушының жауап мәтіні
           student_answer_file BLOB,   # <<< ЖАҢА: оқушының жауап файлы
           student_answer_file_type TEXT, # <<< ЖАҢА: файл түрі
           student_submitted_date TIMESTAMP, # <<< ЖАҢА: жіберген уақыты
           FOREIGN KEY (teacher_id) REFERENCES teachers (id),
           FOREIGN KEY (student_id) REFERENCES students (id),
           FOREIGN KEY (class_id) REFERENCES classes (id)
        )
    ''')
    
    # AI статистикасы кестесі
    c.execute('''
        CREATE TABLE IF NOT EXISTS ai_statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            activity_date DATE NOT NULL,
            python_activities INTEGER DEFAULT 0,
            ai_assisted_tasks INTEGER DEFAULT 0,
            code_submissions INTEGER DEFAULT 0,
            FOREIGN KEY (teacher_id) REFERENCES teachers (id),
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    
    # БЖБ тапсырмалары кестесі
    c.execute('''
        CREATE TABLE IF NOT EXISTS bzb_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            class_id INTEGER NOT NULL,
            task_name TEXT NOT NULL,
            task_file BLOB,
            file_type TEXT,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completion_rate INTEGER DEFAULT 0,
            difficulty_level TEXT,
            ai_solution TEXT,
            FOREIGN KEY (teacher_id) REFERENCES teachers (id),
            FOREIGN KEY (class_id) REFERENCES classes (id)
        )
    ''')
    
    # Көрнекіліктер файлдары кестесі
    c.execute('''
        CREATE TABLE IF NOT EXISTS visual_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_data BLOB,
            file_type TEXT,
            file_size INTEGER,
            category TEXT,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES teachers (id)
        )
    ''')
    
    # Сабақ жоспарлары кестесі
    c.execute('''
        CREATE TABLE IF NOT EXISTS lesson_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            class_id INTEGER NOT NULL,
            lesson_name TEXT NOT NULL,
            subject TEXT,
            grade_level TEXT,
            lesson_type TEXT,
            duration_minutes INTEGER DEFAULT 40,
            goals TEXT,
            methods TEXT,
            equipment TEXT,
            stages TEXT,
            reflection TEXT,
            ai_suggestions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES teachers (id),
            FOREIGN KEY (class_id) REFERENCES classes (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Дерекқор сәтті бастапқыланды!")

def hash_password(password):
    """Құпия сөзді хэштеу"""
    return hashlib.sha256(password.encode()).hexdigest()

# =============== МҰҒАЛІМ ФУНКЦИЯЛАРЫ ===============

def register_user(username, password, email, full_name, school, city):
    """Пайдаланушыны тіркеу"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    c = conn.cursor()
    try:
        hashed_password = hash_password(password)
        c.execute(
            """INSERT INTO teachers (username, password, email, full_name, school, city) 
            VALUES (?, ?, ?, ?, ?, ?)""",
            (username, hashed_password, email, full_name, school, city)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    """Мұғалім кіруі"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    c = conn.cursor()
    hashed_password = hash_password(password)
    c.execute(
        """SELECT id, username, full_name, school, city FROM teachers 
        WHERE username=? AND password=?""",
        (username, hashed_password)
    )
    user = c.fetchone()
    conn.close()
    return user

# =============== СЫНЫП ФУНКЦИЯЛАРЫ ===============

def add_class(teacher_id, name, subject, grade_level, description):
    """Сынып қосу"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    c = conn.cursor()
    try:
        c.execute(
            """INSERT INTO classes (teacher_id, name, subject, grade_level, description) 
            VALUES (?, ?, ?, ?, ?)""",
            (teacher_id, name, subject, grade_level, description)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def get_classes(teacher_id=None):
    """Сыныптарды алу"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    c = conn.cursor()
    
    if teacher_id:
        c.execute("SELECT id, name, subject, grade_level FROM classes WHERE teacher_id = ? ORDER BY name", (teacher_id,))
    else:
        c.execute("SELECT id, name, subject, grade_level FROM classes ORDER BY name")
    
    classes = c.fetchall()
    conn.close()
    return classes

def delete_class(class_id):
    """Сыныпты жою"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    c = conn.cursor()
    try:
        # Алдымен осы сыныпқа байланысты оқушыларды жоямыз
        c.execute("DELETE FROM students WHERE class_id = ?", (class_id,))
        # БЖБ тапсырмаларын жою
        c.execute("DELETE FROM bzb_tasks WHERE class_id = ?", (class_id,))
        # Сабақ жоспарларын жою
        c.execute("DELETE FROM lesson_plans WHERE class_id = ?", (class_id,))
        # Student tasks жою
        c.execute("DELETE FROM student_tasks WHERE class_id = ?", (class_id,))
        # Содан кейін сыныпты жоямыз
        c.execute("DELETE FROM classes WHERE id = ?", (class_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Сыныпты жою қатесі: {e}")
        return False
    finally:
        conn.close()

# =============== ОҚУШЫ ФУНКЦИЯЛАРЫ ===============

def add_student(class_id, full_name, student_code, grade_points=5, username=None, password=None):
    """Оқушы қосу функциясы - ЛОГИН/ПАРОЛЬ ДЕРЕКҚОРҒА САҚТАЛАДЫ!"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    c = conn.cursor()
    try:
        # grade_points санға түрлендіру
        try:
            grade_points_int = int(grade_points)
            if grade_points_int < 1 or grade_points_int > 10:
                grade_points_int = 5
        except (ValueError, TypeError):
            grade_points_int = 5
        
        # Егер логин/пароль берілмесе, автоматты түрде жасау
        if not username or username.strip() == "":
            username = f"student_{student_code}"
        if not password or password.strip() == "":
            password = student_code  # Әдепкі пароль - студент коды
        
        # Парольді хэштеу
        hashed_password = hash_password(password)
        
        # Дерекқорға сақтау
        c.execute(
            """INSERT INTO students (class_id, full_name, student_code, username, password, grade_points) 
            VALUES (?, ?, ?, ?, ?, ?)""",
            (class_id, full_name, student_code, username, hashed_password, grade_points_int)
        )
        conn.commit()
        
        # Құрылған логин/парольді қайтару
        return True, username, password
    except sqlite3.IntegrityError as e:
        error_msg = str(e)
        if "UNIQUE constraint failed: students.username" in error_msg:
            return False, "Бұл логин бос емес, басқа логин таңдаңыз", None
        elif "UNIQUE constraint failed: students.student_code" in error_msg:
            return False, "Бұл оқушы коды бос емес, басқа код таңдаңыз", None
        else:
            return False, f"Қате: {error_msg}", None
    except Exception as e:
        return False, f"Қате: {str(e)}", None
    finally:
        conn.close()

def get_students_by_class(class_id):
    """Сынып бойынша оқушыларды алу"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    c = conn.cursor()
    c.execute("""
        SELECT id, class_id, full_name, student_code, username, 
               grade_points, ai_usage_hours, python_level, last_activity, created_at
        FROM students WHERE class_id = ? ORDER BY full_name
    """, (class_id,))
    students = c.fetchall()
    conn.close()
    return students

def get_student_by_id(student_id):
    """ID бойынша оқушыны алу"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    c = conn.cursor()
    c.execute("""
        SELECT id, class_id, full_name, student_code, username, 
               grade_points, ai_usage_hours, python_level, last_activity, created_at
        FROM students WHERE id = ?
    """, (student_id,))
    student = c.fetchone()
    conn.close()
    return student

def get_all_students(teacher_id):
    """Мұғалімнің барлық оқушыларын алу"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    c = conn.cursor()
    c.execute("""
        SELECT s.id, s.full_name, s.student_code, s.username, s.grade_points,
               s.python_level, c.name as class_name 
        FROM students s 
        JOIN classes c ON s.class_id = c.id 
        WHERE c.teacher_id = ? 
        ORDER BY c.name, s.full_name
    """, (teacher_id,))
    students = c.fetchall()
    conn.close()
    return students

def delete_student(student_id):
    """Оқушыны жою"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    c = conn.cursor()
    try:
        # Алдымен студент тапсырмаларын жою
        c.execute("DELETE FROM student_tasks WHERE student_id = ?", (student_id,))
        # AI статистикасын жою
        c.execute("DELETE FROM ai_statistics WHERE student_id = ?", (student_id,))
        # Оқушыны жою
        c.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Оқушыны жою қатесі: {e}")
        return False
    finally:
        conn.close()

def login_student(username, password):
    """Оқушы кіру функциясы - ДЕРЕКҚОРДАН ТЕКСЕРЕДІ!"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    c = conn.cursor()
    
    # Парольді хэштеу
    hashed_password = hash_password(password)
    
    c.execute(
        """SELECT s.id, s.full_name, s.student_code, s.grade_points, 
                  c.name as class_name, c.id as class_id, s.username
         FROM students s
         JOIN classes c ON s.class_id = c.id
         WHERE s.username = ? AND s.password = ?""",
        (username, hashed_password)
    )
    student = c.fetchone()
    conn.close()
    
    if student:
        # Оқушының соңғы белсенділігін жаңарту
        update_student_last_activity(student[0])
        
        return {
            'id': student[0],
            'full_name': student[1],
            'student_code': student[2],
            'grade_points': student[3],
            'class_name': student[4],
            'class_id': student[5],
            'username': student[6]
        }
    return None

def update_student_last_activity(student_id):
    """Оқушының соңғы белсенділігін жаңарту"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    c = conn.cursor()
    try:
        c.execute(
            "UPDATE students SET last_activity = DATE('now') WHERE id = ?",
            (student_id,)
        )
        conn.commit()
    except Exception as e:
        print(f"Белсенділікті жаңарту қатесі: {e}")
    finally:
        conn.close()

def change_student_password(student_id, new_password):
    """Оқушы паролін өзгерту"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    c = conn.cursor()
    try:
        hashed_password = hash_password(new_password)
        c.execute(
            "UPDATE students SET password = ? WHERE id = ?",
            (hashed_password, student_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Парольді өзгерту қатесі: {e}")
        return False
    finally:
        conn.close()

def get_student_credentials(student_id):
    """Оқушының логин/паролін алу (тек логин, пароль хэштелген)"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    c = conn.cursor()
    c.execute("SELECT username FROM students WHERE id = ?", (student_id,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return result[0]  # Тек логин қайтарылады
    return None

# =============== ТАПСЫРМА ФУНКЦИЯЛАРЫ ===============

def assign_task_to_students_db(teacher_id, class_id, task_name, task_description, deadline_date, selected_students, task_file=None):
    """Тапсырманы оқушыларға тарату"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    c = conn.cursor()
    
    try:
        task_file_bytes = task_file.read() if task_file else None
        file_type = task_file.type if task_file else None
        
        for student_id in selected_students:
            c.execute(
                """INSERT INTO student_tasks 
                (teacher_id, class_id, student_id, task_name, task_description, 
                 task_file, file_type, deadline_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    teacher_id,
                    class_id,
                    student_id,
                    task_name,
                    task_description,
                    task_file_bytes,
                    file_type,
                    deadline_date,
                    'assigned'
                )
            )
        
        conn.commit()
        return True, len(selected_students)
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_student_tasks(teacher_id=None, class_id=None, student_id=None):
    """Оқушы тапсырмаларын алу"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    
    query = """
    SELECT st.*, s.full_name as student_name, c.name as class_name
    FROM student_tasks st
    LEFT JOIN students s ON st.student_id = s.id
    LEFT JOIN classes c ON st.class_id = c.id
    WHERE 1=1
    """
    params = []
    
    if teacher_id:
        query += " AND st.teacher_id = ?"
        params.append(teacher_id)
    
    if class_id:
        query += " AND st.class_id = ?"
        params.append(class_id)
    
    if student_id:
        query += " AND st.student_id = ?"
        params.append(student_id)
    
    query += " ORDER BY st.assigned_date DESC"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def get_task_statistics(teacher_id):
    """Тапсырмалар статистикасын алу"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    query = """
    SELECT DISTINCT st.task_name, st.assigned_date, st.deadline_date, 
           c.name as class_name,
           COUNT(*) as total_students,
           SUM(CASE WHEN st.status = 'completed' THEN 1 ELSE 0 END) as completed,
           SUM(CASE WHEN st.status = 'graded' THEN 1 ELSE 0 END) as graded
    FROM student_tasks st
    JOIN classes c ON st.class_id = c.id
    WHERE st.teacher_id = ?
    GROUP BY st.task_name, st.assigned_date, c.name
    ORDER BY st.assigned_date DESC
    """
    
    df = pd.read_sql_query(query, conn, params=(teacher_id,))
    conn.close()
    return df

def update_task_answer(task_id, student_answer, answer_file=None):
    """Тапсырма жауабын жаңарту"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    c = conn.cursor()
    
    try:
        answer_file_bytes = answer_file.read() if answer_file else None
        
        # AI фидбек жасау
        ai_feedback = generate_ai_feedback(student_answer)
        
        c.execute(
            """UPDATE student_tasks 
            SET status = 'completed', 
                student_answer = ?, 
                answer_file = ?,
                ai_feedback = ?
            WHERE id = ?""",
            (student_answer, answer_file_bytes, ai_feedback, task_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Жауапты жаңарту қатесі: {e}")
        return False
    finally:
        conn.close()

def grade_task(task_id, grade, teacher_feedback):
    """Тапсырманы бағалау"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    c = conn.cursor()
    
    try:
        c.execute(
            """UPDATE student_tasks 
            SET status = 'graded', 
                grade = ?, 
                teacher_feedback = ?
            WHERE id = ?""",
            (grade, teacher_feedback, task_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Бағалау қатесі: {e}")
        return False
    finally:
        conn.close()

def generate_ai_feedback(answer):
    """AI фидбек жасау"""
    import random
    feedbacks = [
        "Жақсы жасалған! Жауап толық және анық берілген.",
        "Жауаптың негізгі бөлігі дұрыс, бірақ кейбір бөлімдерді толықтыруға болады.",
        "Түсініктемелер анық, бірақ қосымша мысалдар пайдалы болар еді.",
        "Жауаптың логикасы дұрыс, практикалық қолдануға назар аударыңыз."
    ]
    return random.choice(feedbacks)

# =============== STATISTICS ФУНКЦИЯЛАРЫ ===============

def get_class_count(teacher_id):
    """Сыныптар санын алу"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM classes WHERE teacher_id=?", (teacher_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def get_student_count(teacher_id):
    """Оқушылар санын алу"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    c = conn.cursor()
    c.execute("""SELECT COUNT(*) FROM students s 
                 JOIN classes c ON s.class_id = c.id 
                 WHERE c.teacher_id=?""", (teacher_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def get_top_students(teacher_id, limit=5):
    """Шын деректерден топ оқушыларды алу"""
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    try:
        query = """
        SELECT s.full_name, s.grade_points, s.python_level, c.name as class_name
        FROM students s
        JOIN classes c ON s.class_id = c.id
        WHERE c.teacher_id = ?
        ORDER BY s.grade_points DESC
        LIMIT ?
        """
        
        df = pd.read_sql_query(query, conn, params=(teacher_id, limit))
        return df
    except Exception as e:
        print(f"Топ оқушыларды алу кезінде қате: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# =============== IMPORT/EXPORT ФУНКЦИЯЛАРЫ ===============

def import_students_from_excel(df, teacher_id):
    """Excel-ден оқушыларды импорттау - ЛОГИН/ПАРОЛЬ ДЕРЕКҚОРҒА САҚТАЛАДЫ!"""
    imported = 0
    errors = []
    
    # Баған атауларын тексеру
    required_columns = ['Сынып атауы', 'Оқушы аты', 'Оқушы коды']
    
    for col in required_columns:
        if col not in df.columns:
            return 0, [f"Қажетті баған жоқ: {col}"]
    
    conn = sqlite3.connect('ai_qazaq_teachers.db')
    c = conn.cursor()
    
    try:
        for idx, row in df.iterrows():
            class_name = str(row['Сынып атауы']).strip()
            student_name = str(row['Оқушы аты']).strip()
            student_code = str(row['Оқушы коды']).strip()
            
            # Бағаны алу (1-10)
            grade_points = 5  # Әдепкі
            if 'Баға (1-10)' in df.columns and pd.notna(row['Баға (1-10)']):
                try:
                    grade_points = int(row['Баға (1-10)'])
                    if grade_points < 1 or grade_points > 10:
                        grade_points = 5
                except:
                    grade_points = 5
            
            if not class_name or not student_name or not student_code:
                errors.append(f"Жол {idx+2}: Міндетті өрістер бос")
                continue
            
            # Сыныпты табу
            c.execute("SELECT id FROM classes WHERE teacher_id=? AND name=?", 
                     (teacher_id, class_name))
            class_result = c.fetchone()
            
            if not class_result:
                errors.append(f"Жол {idx+2}: '{class_name}' сыныбы табылмады")
                continue
            
            class_id = class_result[0]
            
            # Оқушы бар-жоғын тексеру
            c.execute("SELECT id FROM students WHERE student_code=?", (student_code,))
            existing = c.fetchone()
            
            if existing:
                errors.append(f"Жол {idx+2}: '{student_code}' коды бар оқушы бар қой")
                continue
            
            # Логин/пароль құру
            username = f"student_{student_code}"
            hashed_password = hash_password(student_code)
            
            # Оқушы қосу
            c.execute(
                """INSERT INTO students (class_id, full_name, student_code, username, password, grade_points) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                (class_id, student_name, student_code, username, hashed_password, grade_points)
            )
            imported += 1
        
        conn.commit()
        
    except Exception as e:
        errors.append(f"Қате: {str(e)}")
    finally:
        conn.close()
    
    return imported, errors