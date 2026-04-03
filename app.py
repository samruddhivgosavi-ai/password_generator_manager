from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import io

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import os.path
import PyPDF2
import sqlite3
import spacy
from flask import *
app=Flask(__name__)
app.secret_key="system"
nlp=spacy.load("en_core_web_sm")

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

skills_dict = {
    "ml engineer": ["python","machine learning","deep learning","sql"],
    "data analyst": ["python","sql","excel","tableau","powerbi"],
    "python developer": ["html","css","bootstrap","javascript","flask","django","sql","c"],
    "web developer": ["html","css","javascript"]
}

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/upload",methods=["POST"])
def upload():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == 'POST':
        name = request.form["name"]
        job_role = request.form["job_role"]
        resume = request.files["resume"]

        if resume.filename == "":
            return "Please upload your resume!"

        if not resume.filename.endswith(".pdf"):
            return "Only PDF files are allowed!"

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], resume.filename)
        resume.save(filepath)

        text = ""
        with open(filepath, "rb") as file:
            reader = PyPDF2.PdfReader(file)

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text

        job_role_lower = job_role.lower()
        required_skills = skills_dict.get(job_role_lower, [])


        doc = nlp(text.lower())
        tokens = [token.lemma_.lower() for token in doc]

        matched_skills = []

        for skill in required_skills:
            skill_words = skill.lower().split()
            if all(word in tokens for word in skill_words):
                matched_skills.append(skill)


        skill_weights = {
            "python": 30,
            "machine learning": 30,
            "deep learning": 20,
            "sql": 20,
            "excel": 20,
            "tableau": 20,
            "powerbi": 20,
            "html": 10,
            "css": 10,
            "javascript": 20,
            "flask": 20,
            "django": 20
        }

        total_weight = 0
        matched_weight = 0

        for skill in required_skills:
            total_weight += skill_weights.get(skill, 10)

        for skill in matched_skills:
            matched_weight += skill_weights.get(skill, 10)

        if total_weight > 0:
            score = (matched_weight / total_weight) * 100
        else:
            score = 0

        documents = [text.lower()," ".join(required_skills)]

        tfidf = TfidfVectorizer()
        tfidf_matrix = tfidf.fit_transform(documents)

        similarity_score = cosine_similarity(
            tfidf_matrix[0:1], tfidf_matrix[1:2]
        )[0][0]

        similarity_percentage = similarity_score * 100

        similarity = round(similarity_percentage, 2)

        score = (score * 0.6) + (similarity_percentage * 0.4)

        missing_skills = list(set(required_skills) - set(matched_skills))

        matched_skills_str = ", ".join(matched_skills)

        if score >= 60:
            status = "Shortlisted in Screening Round"
            color = "success"
        elif score >= 40:
            status = "Average Candidate"
            color = "warning"
        else:
            status = "Rejected in Screening Round"
            color = "danger"

        con = sqlite3.connect("resume.db")
        cur = con.cursor()
        cur.execute(
            "insert into results (name,job_role,score,status,matched_skills) values(?,?,?,?,?)",
            (name, job_role, score, status,matched_skills_str)
        )
        con.commit()
        con.close()

        return render_template(
            "result.html",
            name=name,
            job_role=job_role,
            filename=resume.filename,
            matched_skills=matched_skills,
            required_skills=required_skills,
            missing_skills=missing_skills,
            score=score,
            text=text[:1000],
            status=status,
            color=color,
            similarity=similarity
        )

    return "Upload Failed"

@app.route("/upload_page")
def upload_page():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("index.html")

@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    con = sqlite3.connect("resume.db")
    cur = con.cursor()

    search=request.form.get("search")
    if search:
        cur.execute("select * from results where name like ?",('%' + search + '%',))
    else:
        cur.execute("select * from results order by id desc")

    data = cur.fetchall()
    con.close()

    return render_template("dashboard.html",data=data)

@app.route("/viewdata",methods=["GET","POST"])
def viewdata():
    con=sqlite3.connect("resume.db")
    cur=con.cursor()

    search = request.form.get("search")

    if search and search.strip() != "":
        cur.execute("select * from results where name like ?",('%' + search.strip() + '%',))
    else:
        cur.execute("select * from results")

    data=cur.fetchall()
    con.close()

    return render_template("viewdata.html",data=data)

@app.route("/delete/<int:id>")
def delete(id):
    con=sqlite3.connect("resume.db")
    cur=con.cursor()

    cur.execute("delete from results where id=?",(id,))

    con.commit()
    con.close()

    return redirect(url_for("dashboard"))

@app.route("/shortlisted")
def shortlisted():
    if "user" not in session:
        return redirect(url_for("login"))

    con=sqlite3.connect("resume.db")
    cur=con.cursor()

    cur.execute("select * from results where score >= 60")
    data=cur.fetchall()

    con.close()
    return render_template("dashboard.html",data=data)

@app.route("/rejected")
def rejected():
    if "user" not in session:
        return redirect(url_for("login"))

    con=sqlite3.connect("resume.db")
    cur=con.cursor()

    cur.execute("select * from results where score < 60")
    data=cur.fetchall()

    con.close()
    return render_template("dashboard.html",data=data)

@app.route("/edit/<int:id>")
def edit(id):
    if "user" not in session:
        return redirect(url_for("login"))

    con=sqlite3.connect("resume.db")
    cur=con.cursor()

    cur.execute("select * from results where id=?",(id,))
    data=cur.fetchone()

    con.close()
    return render_template("edit.html",data=data)

@app.route("/update", methods=["POST"])
def update():
    id=request.form["id"]
    name=request.form["name"]
    job_role=request.form["job_role"]

    con=sqlite3.connect("resume.db")
    cur=con.cursor()

    cur.execute("update results set name=?,job_role=? where id=?",(name,job_role,id))

    con.commit()
    con.close()

    return redirect(url_for("dashboard"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]

        if username == "admin" and password == "admin123":
            session["user"] = username
            return redirect(url_for("upload_page"))
        else:
            return render_template("login.html",error="Invalid Username or Password")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect(url_for("login"))

@app.route("/download_pdf")
def download_pdf():
    con = sqlite3.connect("resume.db")
    cur = con.cursor()
    cur.execute("select * from results")
    data = cur.fetchall()
    con.close()

    buffer=io.BytesIO()
    pdf = SimpleDocTemplate(buffer)

    table_data = [
        ["ID", "Name", "Job Role", "Score", "Status", "Skills"]
    ]

    for row in data:
        table_data.append(list(row))

    table = Table(table_data)

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])

    table.setStyle(style)

    pdf.build([table])

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="resume_data.pdf",
        mimetype='application/pdf'
    )

@app.route("/clear_all")
def clear_all():
    con=sqlite3.connect("resume.db")
    cur=con.cursor()

    cur.execute("delete from results")
    cur.execute("delete from sqlite_sequence where name='results'")

    con.commit()
    con.close()

    return redirect(url_for("viewdata"))

if __name__=="__main__":
    app.run(debug=True,use_reloader=False,port=4300)