# #SET UP:

# # 1. INSTALL BELOW LIBRARIES

#         #pip install -r requirements.txt

#         # pip install nltk

#         # pip install spacy==2.3.5

#         # pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.3.1/en_core_web_sm-2.3.1.tar.gz

#         # pip install pyresparser

# # 2. CREATE A FOLDER AND NAME IT (e.g. resume)
#         #2.1 create two more folders inside this folder (Logo and Uploaded_Resumes)
#         #2.2 create two python files (App.py and Courses.py)

# # 3. START YOUR SQL DATABASE

# # 4. CONTINUE WITH THE FOLLOWING CODE...
import base64
import datetime
import io
import random
import time
import ast
import nltk
import pandas as pd
import plotly.express as px
import pymysql
import streamlit as st
from PIL import Image
from pdfminer3.converter import TextConverter
from pdfminer3.layout import LAParams
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfpage import PDFPage
from pyresparser import ResumeParser
from pytube import YouTube
from streamlit_tags import st_tags
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos

nltk.download('stopwords')


def fetch_yt_video_title(link):
    """
    Fetches the title of a YouTube video from its link.

    Args:
        link (str): The YouTube video link.

    Returns:
        str: The title of the YouTube video.
    """
    return YouTube(link).title


def get_table_download_link(df, filename, text):
    """
    Generates a link allowing the data in a Pandas DataFrame to be downloaded.

    Args:
        df (pandas.DataFrame): The DataFrame to be downloaded.
        filename (str): The filename for the downloaded file.
        text (str): The text to display for the download link.

    Returns:
        str: The HTML link for downloading the DataFrame.
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


def pdf_reader(file_path):
    """
    Reads the text content from a PDF file.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        str: The text content of the PDF file.
    """
    with open(file_path, 'rb') as fh:
        resource_manager = PDFResourceManager()
        fake_file_handle = io.StringIO()
        converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
        page_interpreter = PDFPageInterpreter(resource_manager, converter)

        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)

        text = fake_file_handle.getvalue()
        converter.close()
        fake_file_handle.close()

    return text


def show_pdf(file_path):
    """
    Displays a PDF file in the Streamlit app.

    Args:
        file_path (str): The path to the PDF file.
    """
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = (F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" '
                   F'type="application/pdf"></iframe>')
    st.markdown(pdf_display, unsafe_allow_html=True)


def course_recommender(course_list):
    """
    Displays course recommendations and allows the user to choose the number of recommendations.

    Args:
        course_list (list): A list of tuples containing course names and links.

    Returns:
        list: A list of recommended course names.
    """
    st.subheader("**Courses & Certificates Recommendations 🎓**")
    recommended_courses = []
    num_recommendations = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)

    for idx, (course_name, course_link) in enumerate(course_list[:num_recommendations], start=1):
        st.markdown(f"({idx}) [{course_name}]({course_link})")
        recommended_courses.append(course_name)

    return recommended_courses


# CONNECT TO DATABASE

connection = pymysql.connect(host='localhost', user='root', password='nithin090#$%', db='cv')
cursor = connection.cursor()


def insert_data(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses, cursor, connection):
    """
    Inserts user data into the 'user_data' table.

    Args:
        name (str): The name of the user.
        email (str): The email of the user.
        res_score (str): The resume score of the user.
        timestamp (str): The timestamp of the user's session.
        no_of_pages (str): The number of pages in the user's resume.
        reco_field (str): The recommended field for the user.
        cand_level (str): The candidate level of the user.
        skills (str): The skills listed in the user's resume.
        recommended_skills (str): The recommended skills for the user.
        courses (str): The recommended courses for the user.
        cursor (pymysql.cursors.Cursor): The database cursor object.
        connection (pymysql.connections.Connection): The database connection object.
    """
    insert_sql = """
        INSERT INTO user_data (Name, Email_ID, resume_score, Timestamp, Page_no, Predicted_Field, User_level, Actual_skills, Recommended_skills, Recommended_courses)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    rec_values = (name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses)
    cursor.execute(insert_sql, rec_values)
    connection.commit()


st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon='./Logo/logo3.png',
)

def run():
    img = Image.open('./Logo/logo3.png')
    #img = img.resize((250,250))
    st.image(img)
    st.title("AI Resume Refiner")
    st.sidebar.markdown("# Choose User")
    activities = ["User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    link = '[©Developed by Nithin M A](https://www.linkedin.com/in/nithin-m-a-/)'
    st.sidebar.markdown(link, unsafe_allow_html=True)

    # Create the DB
    db_sql = """CREATE DATABASE IF NOT EXISTS CV;"""
    cursor.execute(db_sql)

    # Create table
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                     Name varchar(500) NOT NULL,
                     Email_ID VARCHAR(500) NOT NULL,
                     resume_score VARCHAR(8) NOT NULL,
                     Timestamp VARCHAR(50) NOT NULL,
                     Page_no VARCHAR(5) NOT NULL,
                     Predicted_Field BLOB NOT NULL,
                     User_level BLOB NOT NULL,
                     Actual_skills BLOB NOT NULL,
                     Recommended_skills BLOB NOT NULL,
                     Recommended_courses BLOB NOT NULL,
                     PRIMARY KEY (ID));
                    """
    cursor.execute(table_sql)
    if choice == 'User':
        st.markdown('''<h5 style='text-align: left; color: #021659;'> Upload your resume, and get smart 
        recommendations</h5>''',
                    unsafe_allow_html=True)
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            with st.spinner('Uploading your Resume...'):
                time.sleep(4)
            save_image_path = './Uploaded_Resumes/' + pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                ## Get the whole resume data
                resume_text = pdf_reader(save_image_path)

                st.header("**Resume Analysis**")
                st.success("Hello " + resume_data['name'])
                st.subheader("**Your Basic info**")
                try:
                    st.text('Name: ' + resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Resume pages: ' + str(resume_data['no_of_pages']))
                except:
                    pass
                cand_level = ''
                if resume_data['no_of_pages'] == 1:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>You are at Fresher level!</h4>''',
                                unsafe_allow_html=True)
                elif resume_data['no_of_pages'] == 2:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',
                                unsafe_allow_html=True)
                elif resume_data['no_of_pages'] >= 3:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',
                                unsafe_allow_html=True)

                # st.subheader("**Skills Recommendation💡**")
                ## Skill shows
                keywords = st_tags(label='### Your Current Skills',
                                   text='See our skills recommendation below',
                                   value=resume_data['skills'], key='1')

                ##  keywords
                ds_keyword = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep Learning', 'flask',
                              'streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                               'javascript', 'angular js', 'c#', 'flask']
                android_keyword = ['android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy']
                ios_keyword = ['ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode']
                uiux_keyword = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes',
                                'storyframes',
                                'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator', 'illustrator',
                                'adobe after effects', 'after effects',
                                'adobe premier pro', 'premier pro', 'adobe indesign', 'indesign', 'wireframe', 'solid',
                                'grasp', 'user research', 'user experience']

                recommended_skills = []
                reco_field = ''
                rec_course = ''
                ## Courses recommendation
                for i in resume_data['skills']:
                    ## Data science recommendation
                    if i.lower() in ds_keyword:
                        print(i.lower())
                        reco_field = 'Data Science'
                        st.success("** Our analysis says you are looking for Data Science Jobs.**")
                        recommended_skills = ['Data Visualization', 'Predictive Analysis', 'Statistical Modeling',
                                              'Data Mining', 'Clustering & Classification', 'Data Analytics',
                                              'Quantitative Analysis', 'Web Scraping', 'ML Algorithms',
                                              'Keras', 'Pytorch', 'Probability', 'Scikit-learn', 'Tensorflow',
                                              "Flask", 'Streamlit']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='2')
                        st.markdown('''<h4 style='text-align: left; 
                        color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job</h4>''',
                                    unsafe_allow_html=True)
                        rec_course = course_recommender(ds_course)
                        break

                    ## Web development recommendation
                    elif i.lower() in web_keyword:
                        print(i.lower())
                        reco_field = 'Web Development'
                        st.success("** Our analysis says you are looking for Web Development Jobs **")
                        recommended_skills = ['React', 'Django', 'Node JS', 'React JS', 'php', 'laravel', 'Magento',
                                              'wordpress', 'Javascript', 'Angular JS', 'c#', 'Flask', 'SDK']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='3')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;
                        '>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                                    unsafe_allow_html=True)
                        rec_course = course_recommender(web_course)
                        break

                    ## Android App Development
                    elif i.lower() in android_keyword:
                        print(i.lower())
                        reco_field = 'Android Development'
                        st.success("** Our analysis says you are looking for Android App Development Jobs **")
                        recommended_skills = ['Android', 'Android development', 'Flutter', 'Kotlin', 'XML', 'Java',
                                              'Kivy', 'GIT', 'SDK', 'SQLite']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='4')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;
                        '>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                                    unsafe_allow_html=True)
                        rec_course = course_recommender(android_course)
                        break

                    ## IOS App Development
                    elif i.lower() in ios_keyword:
                        print(i.lower())
                        reco_field = 'IOS Development'
                        st.success("** Our analysis says you are looking for IOS App Development Jobs **")
                        recommended_skills = ['IOS', 'IOS Development', 'Swift', 'Cocoa', 'Cocoa Touch', 'Xcode',
                                              'Objective-C', 'SQLite', 'Plist', 'StoreKit', "UI-Kit", 'AV Foundation',
                                              'Auto-Layout']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='5')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;
                        '>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                                    unsafe_allow_html=True)
                        rec_course = course_recommender(ios_course)
                        break

                    ## Ui-UX Recommendation
                    elif i.lower() in uiux_keyword:
                        print(i.lower())
                        reco_field = 'UI-UX Development'
                        st.success("** Our analysis says you are looking for UI-UX Development Jobs **")
                        recommended_skills = ['UI', 'User Experience', 'Adobe XD', 'Figma', 'Zeplin', 'Balsamiq',
                                              'Prototyping', 'Wireframes', 'Storyframes', 'Adobe Photoshop', 'Editing',
                                              'Illustrator', 'After Effects', 'Premier Pro', 'Indesign', 'Wireframe',
                                              'Solid', 'Grasp', 'User Research']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='6')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;
                        '>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                                    unsafe_allow_html=True)
                        rec_course = course_recommender(uiux_course)
                        break

                ## Insert into table
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date + '_' + cur_time)

                ### Resume writing recommendation
                st.subheader("**Resume Tips & Ideas💡**")
                resume_score = 0
                if 'Objective' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;
                    '>[+] Awesome! You have added Objective</h4>''', unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;
                    '>[-] Please add your career objective, it will give your career intension to the Recruiters.</h4>''',
                                unsafe_allow_html=True)

                if 'Declaration' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;
                    '>[+] Awesome! You have added Declaration/h4>''', unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;
                    '>[-] Please add Declaration. 
                    It will give the assurance that everything written on your resume is true and fully acknowledged by you</h4>''',
                                unsafe_allow_html=True)

                if 'Hobbies' or 'Interests' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;
                    '>[+] Awesome! You have added your Hobbies</h4>''', unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;
                    '>[-] Please add Hobbies. It will show your persnality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',
                                unsafe_allow_html=True)

                if 'Achievements' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;
                    '>[+] Awesome! You have added your Achievements </h4>''', unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;
                    '>[-] Please add Achievements. It will show that you are capable for the required position.</h4>''',
                                unsafe_allow_html=True)

                if 'Projects' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;
                    '>[+] Awesome! You have added your Projects</h4>''', unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;
                    '>[-] Please add Projects. It will show that you have done work related the required position or not.</h4>''',
                                unsafe_allow_html=True)

                st.subheader("**Resume Score📝**")
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score += 1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)
                st.success('** Your Resume Writing Score: ' + str(score) + '**')
                st.warning("** Note: This score is calculated based on the content that you have in your Resume. **")
                st.balloons()

                insert_data(resume_data['name'], resume_data['email'], str(resume_score), timestamp,
                            str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']),
                            str(recommended_skills), str(rec_course))

                ## Resume writing video
                st.header("**Bonus Video for Resume Writing Tips💡**")
                resume_vid = random.choice(resume_videos)
                res_vid_title = fetch_yt_video(resume_vid)
                st.subheader("✅ **" + res_vid_title + "**")
                st.video(resume_vid)

                ## Interview Preparation Video
                st.header("**Bonus Video for Interview Tips💡**")
                interview_vid = random.choice(interview_videos)
                int_vid_title = fetch_yt_video(interview_vid)
                st.subheader("✅ **" + int_vid_title + "**")
                st.video(interview_vid)

                connection.commit()
            else:
                st.error('Something went wrong..')
    else:
        ## Admin Side
        st.success('Welcome to Admin Side')
        # st.sidebar.subheader('**ID / Password Required!**')

        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')
        if st.button('Login'):
            if ad_user == 'nithinma' and ad_password == 'nithin123':
                st.success("Welcome Nithin M A!")
                # Display Data
                cursor.execute('''SELECT*FROM user_data''')
                data = cursor.fetchall()
                st.header("**User's Data**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Total Page',
                                                 'Predicted Field', 'User Level', 'Actual Skills', 'Recommended Skills',
                                                 'Recommended Course'])
                # Deserialize BLOB/TEXT columns
                df['Predicted Field'] = df['Predicted Field'].apply(
                    lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)
                df['User Level'] = df['User Level'].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)
                df['Actual Skills'] = df['Actual Skills'].apply(
                    lambda x: ast.literal_eval(x.decode('utf-8')) if isinstance(x, bytes) else x)
                df['Recommended Skills'] = df['Recommended Skills'].apply(
                    lambda x: ast.literal_eval(x.decode('utf-8')) if isinstance(x, bytes) else x)
                df['Recommended Course'] = df['Recommended Course'].apply(
                    lambda x: ast.literal_eval(x.decode('utf-8')) if isinstance(x, bytes) else x)
                st.dataframe(df)
                st.markdown(get_table_download_link(df, 'User_Data.csv', 'Download Report'), unsafe_allow_html=True)
                ## Admin Side Data
                query = 'select * from user_data;'
                plot_data = pd.read_sql(query, connection)

                ## Pie chart for predicted field recommendations
                predicted_field_counts = plot_data['Predicted_Field'].value_counts().reset_index().dropna().drop_duplicates()
                predicted_field_counts.columns = ['Predicted_Field','count']
                predicted_field_counts['Predicted_Field'] = predicted_field_counts['Predicted_Field'].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)
                st.subheader("**Pie-Chart for Predicted Field Recommendation**")
                fig = px.pie(predicted_field_counts, values='count', names='Predicted_Field', title='Predicted Field according to the Skills')
                st.plotly_chart(fig)

                ### Pie chart for User's👨‍💻 Experienced Level
                user_level_counts = plot_data['User_level'].value_counts().reset_index().dropna().drop_duplicates()
                user_level_counts.columns = ['User_level', 'count']
                user_level_counts['User_level'] = user_level_counts['User_level'].apply(
                    lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)
                st.subheader("**Pie-Chart for User's Experienced Level**")
                fig = px.pie(user_level_counts, values='count', names='User_level', title="Pie-Chart📈 for User's👨‍💻 Experienced Level")
                st.plotly_chart(fig)

            else:
                st.error("Wrong ID & Password Provided")


run()
