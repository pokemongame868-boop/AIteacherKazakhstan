import streamlit as st
import pandas as pd
import random
import io
from datetime import datetime, timedelta
from database import (
    get_classes, get_students_by_class, get_student_tasks, 
    assign_task_to_students_db, get_task_statistics,
    add_student, delete_student, import_students_from_excel,
    get_student_by_id
)
from language import TEXT
from utils import points_to_grade, get_grade_class

# Тілді баптау
lang = st.session_state.get("lang", "kk")
t = TEXT[lang]

# Бөлім атауы
st.header("👨‍🎓 Оқушылар мен Тапсырмалар")

def generate_student_feedback(answer, task_name):
    """Оқушы жауабына AI фидбек жасау"""
    feedbacks = [
        f"**{task_name} тапсырмасына арналған AI талдау:**\n\n✅ **Жақсы жасалған:**\n- Жауап толық берілген\n- Түсініктемелер анық\n- Мысалдар келтірілген\n\n⚠️ **Жетілдіруге болатын:**\n- Кейбір түсіндірмелерді толықтыру\n- Қосымша мысалдар келтіру\n- Практикалық қолдануды көрсету\n\n🎯 **Келесі қадамдар:**\n1. Қателерді түзету\n2. Қосымша материалдар оқу\n3. Ұқсас тапсырмалар орындау",
    ]
    return random.choice(feedbacks)

def create_sample_excel():
    """Үлгі Excel файлын жасау"""
    students_data = {
        'Сынып атауы': ['10А', '10А', '10А', '10Б', '10Б', '11А'],
        'Оқушы аты': ['Алия Құрман', 'Данияр Жолдас', 'Айгерім Сағат', 
                      'Нұрлан Омаров', 'Мәдина Әлім', 'Бақыт Жансейітов'],
        'Оқушы коды': ['S001', 'S002', 'S003', 'S004', 'S005', 'S006'],
        'Баға (1-10)': [9, 8, 7, 8, 9, 10]
    }
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pd.DataFrame(students_data).to_excel(writer, sheet_name='Оқушылар', index=False)
        
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for idx, col in enumerate(writer.sheets[sheet_name]._worksheet.columns):
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 30)
                worksheet.column_dimensions[column].width = adjusted_width
    
    output.seek(0)
    return output

# --------------------------------------------------------------------
# БАСТАПҚЫ КОД - БІР ФОРМА ҒАНА, ІШ-ІШКЕ ЕМЕС
# --------------------------------------------------------------------

# Төмендегі бөлімдерді Streamlit табы (tabs) ретінде ұйымдастырамыз
tab1, tab2, tab3 = st.tabs(["👨‍🎓 Оқушыларды басқару", "📝 Тапсырмалар тарату", "📊 Тапсырмалар статистикасы"])

with tab1:
    st.subheader("👨‍🎓 Оқушыларды басқару")
    
    # Excel үлгісін жүктеп алу - БІРІНШІ БӨЛІМ, ФОРМА ЕМЕС
    st.markdown("---")
    st.subheader("📥 Excel үлгісі")
    
    sample_excel = create_sample_excel()
    st.download_button(
        label="📥 Excel үлгісін жүктеп алу",
        data=sample_excel,
        file_name="student_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_template"
    )
    
    # Сыныптарды алу
    teacher_id = st.session_state.user[0] if 'user' in st.session_state and st.session_state.user else None
    classes = get_classes(teacher_id) if teacher_id else []
    
    if not classes:
        st.info(f"ℹ️ {t['no_classes']}")
    else:
        class_map = {f"{c[1]} (ID: {c[0]})": c[0] for c in classes}
        
        # Сыныпты таңдау
        selected_class_display = st.selectbox(f"📚 {t['select_class']}", list(class_map.keys()), key="class_select_1")
        selected_class_id = class_map[selected_class_display]
        
        # Оқушыларды көрсету
        students = get_students_by_class(selected_class_id)
        
        if students:
            st.subheader(f"👨‍🎓 {selected_class_display.split('(')[0]} - Оқушылар тізімі")
            
            # Логиндерді жүктеп алу - ФОРМА ЕМЕС
            login_data = []
            for student in students:
                login_data.append({
                    'Оқушы аты': student[2],
                    'Код': student[3],
                    'Логин': student[4],
                    'Пароль': student[3],
                    'Ұпай': student[5] if len(student) > 5 else 0
                })
            
            login_df = pd.DataFrame(login_data)
            csv_data = login_df.to_csv(index=False).encode('utf-8')
            
            col_download1, col_download2 = st.columns(2)
            
            with col_download1:
                st.download_button(
                    label="📥 Логиндерді CSV файлына жүктеп алу",
                    data=csv_data,
                    file_name=f"logins_{selected_class_display.split('(')[0]}.csv",
                    mime="text/csv",
                    key="download_logins"
                )
            
            with col_download2:
                excel_output = io.BytesIO()
                with pd.ExcelWriter(excel_output, engine='xlsxwriter') as writer:
                    login_df.to_excel(writer, sheet_name='Логиндер', index=False)
                excel_output.seek(0)
                
                st.download_button(
                    label="📥 Логиндерді Excel файлына жүктеп алу",
                    data=excel_output,
                    file_name=f"logins_{selected_class_display.split('(')[0]}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_logins_excel"
                )
            
            # Кестені дайындау
            student_data = []
            for student in students:
                grade_points = student[5] if len(student) > 5 else 0
                grade_letter = points_to_grade(grade_points)
                grade_class = get_grade_class(grade_letter)
                
                if grade_points >= 9:
                    study_progress = "Өте жақсы"
                elif grade_points >= 7:
                    study_progress = "Жақсы"
                elif grade_points >= 5:
                    study_progress = "Орташа"
                elif grade_points >= 3:
                    study_progress = "Қанағаттанарлық"
                else:
                    study_progress = "Қанағаттанарлық"
                
                student_data.append({
                    'ID': student[0],
                    'Аты-жөні' if lang == 'kk' else 'ФИО': student[2],
                    'Код': student[3],
                    'Логин': student[4],
                    'Ұпай' if lang == 'kk' else 'Баллы': grade_points,
                    'Баға' if lang == 'kk' else 'Оценка': grade_letter,
                    'Оқу үлгерімі' if lang == 'kk' else 'Успеваемость': study_progress,
                })
            
            students_df = pd.DataFrame(student_data)
            
            # HTML таблицасы
            html_table = f"""
            <table class="student-table">
                <thead>
                    <tr>
                        <th>{'Аты-жөні' if lang == 'kk' else 'ФИО'}</th>
                        <th>Код</th>
                        <th>Логин</th>
                        <th>{'Ұпай' if lang == 'kk' else 'Баллы'}</th>
                        <th>{'Баға' if lang == 'kk' else 'Оценка'}</th>
                        <th>{'Оқу үлгерімі' if lang == 'kk' else 'Успеваемость'}</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for idx, row in students_df.iterrows():
                grade_class = get_grade_class(row['Баға' if lang == 'kk' else 'Оценка'])
                
                progress_color = {
                    'Өте жақсы': '#28a745',
                    'Жақсы': '#20c997',
                    'Орташа': '#ffc107',
                    'Қанағаттанарлық': '#fd7e14',
                    'Қанағаттанарлық': '#dc3545'
                }.get(row['Оқу үлгерімі' if lang == 'kk' else 'Успеваемость'], '#6c757d')
                
                html_table += f"""
                <tr>
                    <td>{row['Аты-жөні' if lang == 'kk' else 'ФИО']}</td>
                    <td>{row['Код']}</td>
                    <td><code>{row['Логин']}</code></td>
                    <td>{row['Ұпай' if lang == 'kk' else 'Баллы']}</td>
                    <td><span class="grade-badge {grade_class}">{row['Баға' if lang == 'kk' else 'Оценка']}</span></td>
                    <td><span style="color: {progress_color}; font-weight: bold;">{row['Оқу үлгерімі' if lang == 'kk' else 'Успеваемость']}</span></td>
                </tr>
                """
            
            html_table += "</tbody></table>"
            st.markdown(html_table, unsafe_allow_html=True)
            
            # Әр оқушыға әрекеттер
            for idx, row in students_df.iterrows():
                with st.expander(f"👤 {row['Аты-жөні' if lang == 'kk' else 'ФИО']} - {row['Код']}", key=f"student_{row['ID']}"):
                    col_info, col_actions = st.columns([3, 1])
                    
                    with col_info:
                        st.write(f"**Логин:** `{row['Логин']}`")
                        st.write(f"**Пароль:** `{row['Код']}` (әдепкі)")
                        st.write(f"**{'Ұпай' if lang == 'kk' else 'Баллы'}:** {row['Ұпай' if lang == 'kk' else 'Баллы']}")
                        st.write(f"**Баға:** {row['Баға' if lang == 'kk' else 'Оценка']}")
                        st.write(f"**{'Оқу үлгерімі' if lang == 'kk' else 'Успеваемость'}:** {row['Оқу үлгерімі' if lang == 'kk' else 'Успеваемость']}")
                        
                        full_student_info = get_student_by_id(row['ID'])
                        if full_student_info and len(full_student_info) > 8:
                            st.write(f"**Соңғы белсенділік:** {full_student_info[8] if full_student_info[8] else 'Жоқ'}")
                    
                    with col_actions:
                        if st.button(f"🗑️ {t['delete_student']}", key=f"del_student_{row['ID']}"):
                            if delete_student(row['ID']):
                                st.success(f"✅ Оқушы жойылды!")
                                st.rerun()
                            else:
                                st.error("❌ Оқушыны жою кезінде қате пайда болды")
        
        else:
            st.info(f"ℹ️ {t['no_students']}")
        
        # Жаңа оқушы қосу ФОРМАСЫ - БІР ҒАНА ФОРМА
        st.markdown("---")
        st.subheader(f"➕ {t['add_student']}")
        
        # ФОРМА 1: Оқушы қосу
        with st.form("add_student_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                full_name = st.text_input(t['student_name'], key="full_name")
            with col2:
                student_code = st.text_input(t['student_id'], key="student_code")
            with col3:
                grade_points = st.slider(t['select_grade'], 1, 10, 5, key="grade_points")
                st.write(f"**{t['points']}:** {grade_points} ({points_to_grade(grade_points)})")
            
            st.markdown("---")
            st.subheader("🔐 Логин/Пароль")
            
            col_login, col_pass = st.columns(2)
            
            with col_login:
                generate_login = st.checkbox("Логинді автоматты жасау", value=True, key="gen_login")
                if not generate_login:
                    username = st.text_input("Логин", value=f"student_{student_code}", key="username_input")
                else:
                    username = f"student_{student_code}"
                    st.info(f"**Логин:** `{username}`")
            
            with col_pass:
                generate_pass = st.checkbox("Парольді автоматты жасау", value=True, key="gen_pass")
                if not generate_pass:
                    password = st.text_input("Пароль", value=student_code, key="password_input", type="password")
                else:
                    password = student_code
                    st.info(f"**Пароль:** `{password}`")
            
            submitted = st.form_submit_button(f"✅ {t['add']}", use_container_width=True)
            
            if submitted:
                if full_name and student_code and username and password:
                    success, message, generated_pass = add_student(
                        selected_class_id, full_name, student_code, grade_points, 
                        username, password
                    )
                    if success:
                        st.success(f"✅ {t['student_added']}")
                        st.info(f"**Логин:** `{username}`\n**Пароль:** `{generated_pass}`")
                        st.warning("⚠️ Бұл логин/пароль дерекқорға сақталды!")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error("❌ Барлық өрістерді толтырыңыз!")
        
        # Excel импорттау - ФОРМА ЕМЕС
        st.markdown("---")
        st.subheader(f"📥 {t['import_students']}")
        
        uploaded_file = st.file_uploader(t['import_excel'], type=['xlsx', 'csv'], key="excel_upload")
        
        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file)
                st.success(f"✅ {t['excel_import_success']}")
                st.write("Алғашқы 5 жол:")
                st.dataframe(df.head(), use_container_width=True)
                
                if st.button(f"📥 Импорттау", key="import_button"):
                    teacher_id = st.session_state.user[0] if 'user' in st.session_state and st.session_state.user else None
                    if teacher_id:
                        imported, errors = import_students_from_excel(df, teacher_id)
                        if imported > 0:
                            st.success(f"✅ {imported} оқушы импортталды!")
                            st.rerun()
                        if errors:
                            st.warning("⚠️ Кейбір қателер пайда болды:")
                            for error in errors[:5]:
                                st.error(f"• {error}")
                    else:
                        st.error("❌ Мұғалім ID табылмады")
            except Exception as e:
                st.error(f"❌ {t['excel_import_error']}: {e}")

with tab2:
    st.subheader("📝 Тапсырмалар тарату")
    
    if teacher_id and classes:
        # Сыныпты таңдау
        class_map = {f"{c[1]} (ID: {c[0]})": c[0] for c in classes}
        selected_class_display_2 = st.selectbox(f"📚 {t['select_class']}", list(class_map.keys()), key="class_select_2")
        selected_class_id_2 = class_map[selected_class_display_2]
        
        # Оқушыларды алу
        students_2 = get_students_by_class(selected_class_id_2)
        
        if students_2:
            # ФОРМА 2: Тапсырма тарату
            with st.form("assign_task_form"):
                col_task1, col_task2 = st.columns(2)
                
                with col_task1:
                    task_name = st.text_input("Тапсырма атауы", key="task_name")
                    task_description = st.text_area("Тапсырма сипаттамасы", height=100, key="task_desc")
                
                with col_task2:
                    task_file = st.file_uploader(
                        "Тапсырма файлы (қосымша)",
                        type=['pdf', 'doc', 'docx', 'txt', 'jpg', 'png', 'zip'],
                        key="task_file"
                    )
                    
                    deadline_date = st.date_input("Мерзімі", value=datetime.now() + timedelta(days=7), key="deadline")
                
                st.subheader("👨‍🎓 Тапсырманы кімге тарату")
                
                student_options = {}
                for student in students_2:
                    student_options[f"{student[2]} ({student[3]}) - Логин: {student[4]}"] = student[0]
                
                selected_students_display = st.multiselect(
                    "Оқушыларды таңдаңыз",
                    list(student_options.keys()),
                    default=list(student_options.keys()),
                    key="student_select"
                )
                
                selected_students_ids = [student_options[name] for name in selected_students_display]
                
                submitted_task = st.form_submit_button("📤 Тапсырманы тарату", use_container_width=True)
                
                if submitted_task:
                    if task_name and selected_students_ids:
                        success, result = assign_task_to_students_db(
                            teacher_id, selected_class_id_2, task_name, task_description, 
                            deadline_date, selected_students_ids, task_file
                        )
                        
                        if success:
                            st.success(f"✅ Тапсырма {result} оқушыға таратылды!")
                            st.info(f"📝 Тапсырма атауы: {task_name}")
                            st.rerun()
                        else:
                            st.error(f"❌ Қате: {result}")
                    else:
                        st.error("❌ Тапсырма атауын енгізіңіз және оқушыларды таңдаңыз")
        else:
            st.info("📭 Бұл сыныпта оқушылар жоқ. Алдымен оқушы қосыңыз.")
    else:
        st.info("ℹ️ Сыныптар жоқ немесе мұғалім кірмеген")

with tab3:
    st.subheader("📊 Тапсырмалар статистикасы")
    
    if teacher_id:
        tasks_stats = get_task_statistics(teacher_id)
        
        if not tasks_stats.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_tasks = len(tasks_stats)
                st.metric("Жалпы тапсырмалар", total_tasks)
            
            with col2:
                total_students = tasks_stats['total_students'].sum()
                st.metric("Жалпы оқушылар", total_students)
            
            with col3:
                completed_tasks = tasks_stats['completed'].sum() + tasks_stats['graded'].sum()
                completion_rate = (completed_tasks / total_students * 100) if total_students > 0 else 0
                st.metric("Орындалуы", f"{completion_rate:.1f}%")
            
            with col4:
                avg_per_task = tasks_stats['total_students'].mean() if total_tasks > 0 else 0
                st.metric("Бір тапсырмаға", f"{avg_per_task:.1f} оқушы")
            
            st.markdown("---")
            st.subheader("📋 Таратылған тапсырмалар")
            
            for idx, task in tasks_stats.iterrows():
                completion_rate = ((task['completed'] + task['graded']) / task['total_students'] * 100) if task['total_students'] > 0 else 0
                
                with st.expander(f"📝 {task['task_name']} - {task['class_name']} ({completion_rate:.1f}% орындалды)", key=f"task_{idx}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Сынып:** {task['class_name']}")
                        st.write(f"**Берілген:** {task['assigned_date']}")
                    
                    with col2:
                        st.write(f"**Жалпы оқушы:** {task['total_students']}")
                        st.write(f"**Орындаған:** {task['completed']}")
                    
                    with col3:
                        st.write(f"**Орындалуы:** {completion_rate:.1f}%")
                        
                        if st.button("👁️ Толық қарау", key=f"view_task_{idx}"):
                            tasks_df = get_student_tasks(teacher_id=teacher_id)
                            
                            if not tasks_df.empty:
                                task_tasks = tasks_df[tasks_df['task_name'] == task['task_name']]
                                
                                if not task_tasks.empty:
                                    display_cols = ['student_name', 'status', 'grade']
                                    st.dataframe(task_tasks[display_cols], use_container_width=True)
        else:
            st.info("📭 Тапсырмалар әлі таратылмаған")
    else:
        st.info("ℹ️ Мұғалім кірмеген")

# --------------------------------------------------------------------
# CSS СТИЛЬДЕРІ
# --------------------------------------------------------------------

st.markdown("""
<style>
.student-table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
    font-size: 0.9rem;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.student-table th {
    background-color: #0066CC;
    color: white;
    padding: 12px;
    text-align: left;
    font-weight: bold;
}
.student-table td {
    border: 1px solid #ddd;
    padding: 10px;
}
.student-table tr:nth-child(even) {
    background-color: #f9f9f9;
}
.student-table tr:hover {
    background-color: #f1f1f1;
}
.grade-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 15px;
    font-size: 0.9rem;
    font-weight: bold;
    min-width: 30px;
    text-align: center;
}
.grade-a {
    background-color: #28a745;
    color: white;
}
.grade-b {
    background-color: #20c997;
    color: white;
}
.grade-c {
    background-color: #ffc107;
    color: black;
}
.grade-d {
    background-color: #fd7e14;
    color: white;
}
.grade-f {
    background-color: #dc3545;
    color: white;
}
code {
    background-color: #f8f9fa;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: monospace;
    color: #e83e8c;
}
</style>
""", unsafe_allow_html=True)