from flask import Flask, render_template, redirect, request, url_for, session
import mysql.connector
from flask import flash

app = Flask(__name__, static_folder='static')
# Konfigurasi basis data
db_config = {
 "host": "localhost",
 "user": "root",
 "password": "",
 "database": "spm",
}


app.secret_key = "mysqlkey"
# Inisialisasi koneksi dan kursor
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()
# Daftar pilihan untuk elemen <select>
option_select = [
 "Sistem Informasi",
 "Ilmu Komunikasi",
 "Teknik Komputer",
 "Teknik Elektro",
 "Informatika"
]
@app.route("/")
def index():
  if 'its_logged_in' in session:
    return render_template('index.html')
  else:
    return redirect(url_for('login'))
  
@app.route("/mahasiswa_main")
def mahasiswa():
  cursor.execute("SELECT * FROM tb_mahasiswa")
  records = cursor.fetchall()
  return render_template('mahasiswa.html', data=records)
  
# membuat route untuk insert data dan update data
@app.route("/login", methods=["GET", "POST"])
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    cursor.execute("SELECT * FROM user WHERE username = %s AND password = %s ",(username, password))
    
    result = cursor.fetchone()
    if result:
      session['its_logged_in'] = True
      session['username'] = result[1]
      
      return redirect(url_for('index'))
    
    else :
      return render_template('login.html')
  else:
    return render_template('login.html')
  

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # For simplicity, storing the password in plain text (not recommended for production)
        cursor.execute("INSERT INTO user (username, password) VALUES (%s, %s)", (username, password))
        connection.commit()

        flash("Account created successfully! Please log in.")
        return redirect(url_for("login"))
    
    return render_template("signup.html")

  
@app.route("/logout")
def logout():
  session.pop("its_logged_in", True)
  session.pop("username", True)
  
  return redirect(url_for('login'))
    

@app.route("/mahasiswa", methods=['GET', 'POST'])
@app.route("/update_mahasiswa/<int:id_mahasiswa>", methods=['GET', 'POST'])
def insert_or_update_mahasiswa(id_mahasiswa=None):
  if request.method == 'POST':
    nama = request.form['nama']
    npm = request.form['npm']
    prodi = request.form['prodi']
    jenis_kelamin = request.form['jenis_kelamin']
    alamat = request.form['alamat']

    cursor.execute("SELECT * FROM tb_mahasiswa WHERE npm = %s", (npm,))
    existing_data = cursor.fetchone()
    if existing_data and (id_mahasiswa is None or id_mahasiswa != existing_data[0]):
        flash("NPM already exists. Please use a different NPM.")
        return redirect(request.url)
    if id_mahasiswa is None:
 #    Insert new data
      cursor.execute("INSERT INTO tb_mahasiswa (nama, npm, prodi, jenis_kelamin, alamat) VALUES(%s, %s, %s, %s, %s)", (nama, npm, prodi, jenis_kelamin, alamat))
    else:
 #    Update existing data
      cursor.execute("UPDATE tb_mahasiswa SET nama = %s, npm = %s, jenis_kelamin = %s, prodi = %s,alamat = %s WHERE id_mahasiswa = %s", (nama, npm, prodi, jenis_kelamin, alamat, id_mahasiswa))
    connection.commit()
    return redirect(url_for('index'))
  if id_mahasiswa is not None:
    cursor.execute("SELECT * FROM tb_mahasiswa WHERE id_mahasiswa = %s", (id_mahasiswa,))
    data = cursor.fetchone()
    return render_template('form.html', option=option_select, default_value=data[4], data=data,url=url_for('insert_or_update_mahasiswa', id=id_mahasiswa))
  return render_template('form.html', option=option_select, data=None)



@app.route("/delete_mahasiswa/<int:id_mahasiswa>")
def delete_mahasiswa(id_mahasiswa):
  
  cursor.execute("DELETE FROM tb_mahasiswa WHERE id_mahasiswa = %s", (id_mahasiswa,))
  connection.commit()
  return redirect(url_for('mahasiswa'))
  
@app.route("/nilai")
def nilai():
  # if 'its_logged_in' in session:
  cursor.execute("SELECT * FROM tb_mahasiswa")
  records = cursor.fetchall()
  return render_template('nilai.html', data=records)

@app.route("/nilai_mahasiswa/<int:id_mahasiswa>")
def nilai_mahasiswa(id_mahasiswa):
    # Mendapatkan data mahasiswa dari tabel tb_mahasiswa
    cursor.execute("SELECT * FROM tb_mahasiswa WHERE id_mahasiswa = %s", (id_mahasiswa,))
    mahasiswa_data = cursor.fetchone()

    if mahasiswa_data:
        # Mendapatkan data nilai mahasiswa dari tabel tb_nilai
        cursor.execute("SELECT * FROM tb_nilai WHERE id_mahasiswa = %s", (id_mahasiswa,))
        nilai_data = cursor.fetchall()

        return render_template('nilai_mahasiswa.html', mahasiswa_data=mahasiswa_data, nilai_data=nilai_data)
    else:
        # Jika mahasiswa tidak ditemukan, bisa di-handle sesuai kebutuhan
        return render_template('mahasiswa_not_found.html', id_mahasiswa=id_mahasiswa)
    
@app.route("/tambah_nilai/<int:id_mahasiswa>", methods=['GET', 'POST'])
def tambah_nilai(id_mahasiswa):
    if request.method == 'POST':
        mata_kuliah = request.form['mata_kuliah']
        tugas = request.form['tugas']
        uts = request.form['uts']
        uas = request.form['uas']

        # Hitung nilai akhir, misalnya dengan formula tertentu
        nilai_akhir = (float(tugas) + float(uts) + float(uas)) / 3

        # Tentukan predikat berdasarkan nilai akhir
        if nilai_akhir >= 80:
            predikat = 'A'
        elif nilai_akhir >= 70:
            predikat = 'B'
        elif nilai_akhir >= 60:
            predikat = 'C'
        else:
            predikat = 'D'

        # Insert nilai ke database
        cursor.execute("INSERT INTO tb_nilai (id_mahasiswa, mata_kuliah, tugas, uts, uas, predikat) VALUES (%s, %s, %s, %s, %s, %s)", (id_mahasiswa, mata_kuliah, tugas, uts, uas, predikat))
        connection.commit()

        return redirect(url_for('nilai_mahasiswa', id_mahasiswa=id_mahasiswa))

    return render_template('form_nilai.html', id_mahasiswa=id_mahasiswa)

if __name__ == "__main__":
 app.run(debug=True)
