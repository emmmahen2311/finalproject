from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import render_template, redirect, url_for
from pymongo import MongoClient
from bson.json_util import dumps
# import pypandoc
from bson.objectid import ObjectId
import pythoncom
import win32com.client as win32
import os
import bcrypt
from datetime import datetime
import pandas as pd
import io
import xlsxwriter
import fitz  # PyMuPDF
import docx











# Helper function to read text from PDF
def read_pdf(file_path):
    text = ""
    with fitz.open(file_path) as pdf:
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            text += page.get_text("text")
    return text

# Helper function to read text from DOCX
def read_docx(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text

def read_doc(file_path):
    # Using Microsoft Word to open and read .doc file
    pythoncom.CoInitialize()
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    doc = word.Documents.Open(file_path)
    text = doc.Content.Text
    doc.Close()
    word.Quit()
    return text



app = Flask(__name__)


CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:3000"}})


client = MongoClient('localhost', 27017)



login_manager = LoginManager()
login_manager.init_app(app)


db = client.gvk_database




users = db.users

candidates = db.candidates


app.secret_key = os.urandom(24)



users.create_index([("username", 1)], unique=True)




class User(UserMixin):
    def __init__(self, username, password, id, isAdmin):
        self.username = username
        self.password = password
        self.id = id
        self.isAdmin = isAdmin

    def get_id(self):
        return self.id


@app.route("/download_file/<path:filename>", methods=["GET"])
def download_file(filename):
    print(filename)
    return send_from_directory(".", filename)

@app.route("/upload_file", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file part in the request", 400

    file = request.files["file"]

    if file.filename == "":
        return "No selected file", 400

    # Ensure the 'temp' directory exists
    os.makedirs("temp", exist_ok=True)

    # Save the file temporarily
    file_path = os.path.join("temp", file.filename)
    file.save(file_path)
    candidate_file = {"fileName":file_path}
    candidate_id = candidates.insert_one(candidate_file)
    # Process file based on type
    if file.filename.endswith(".pdf"):
        text = read_pdf(file_path)
    elif file.filename.endswith(".docx"):
        text = read_docx(file_path)
    else:
        return "Unsupported file type", 400
    print(candidate_id.inserted_id)
    return jsonify({"text": text, "candidateId":candidate_id.inserted_id.__str__()}), 200
    #return text



@login_manager.user_loader
def load_user(user_id):
    user = users.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(username=user['username'], password=user['password'], id=str(user['_id']), isAdmin=user["isAdmin"])
    return None


@app.route('/create_admin', methods=['GET'])
def create_admin():
    
    user_data = {"username": "admin", "password": "password", "isAdmin": True}
    user_data['password'] = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())
    users.insert_one(user_data)
    return 'Admin Created'




@app.route('/get_users', methods=['GET'])
@login_required
def get_users():
    users_list = users.find() 
    users_list = [user for user in users_list] 
    for user in users_list:
        user['_id'] = str(user['_id']) 
    return jsonify(users_list), 200 


@app.route('/', methods=['GET'])
def get_message():
    return "Python Flask Backend Server is running!!"

@app.route('/insert_candidate', methods=["POST"])
def insert_candidate():
    candidate = request.json
    organized_candidate = {key:value for (key, value) in candidate["candidate"].items()}
    candidates.update_one({'_id': ObjectId(organized_candidate["candidateId"])}, {"$set":organized_candidate}, upsert=False)
    #candidates.insert_one(organized_candidate)
    return jsonify({"message": "המועמד נוסף למסד הנתונים"}), 200


@app.route('/deleteCandidate/<id>', methods=["DELETE"])
def delete_candidate(id):
    result = candidates.delete_one({'_id': ObjectId(id)})
    
    if result.deleted_count == 1:
        return jsonify({"message": "המועמד נמחק"}), 200
    else:
        return jsonify({"error": "המועמד לא נמצא"}), 404


@app.route('/login', methods=["POST"])
def login():
    data = request.json
    username_input = data.get('username')
    password_input = data.get('password')


    user_from_db = users.find_one({'username': username_input})

    if user_from_db:
        if bcrypt.checkpw(password_input.encode('utf-8'), user_from_db['password']):
            user_obj = User(username=user_from_db['username'], password=user_from_db['password'], id=str(user_from_db['_id']), isAdmin=user_from_db["isAdmin"])
            login_user(user_obj) 

            print(current_user.is_authenticated)
            print(current_user.username)


            return jsonify({"message": "התחברת בהצלחה", "username": current_user.username , "isAuthenticated": current_user.is_authenticated}), 200
        else:
            return jsonify({"message": "אחד או יותר מפרטי ההזדהות שמסרת שגויים"}), 401   
    else:
        return jsonify({"message": "שם המשתמש שהזנת לא קיים"}), 404    



@app.route('/logout', methods=["POST"])
@login_required  
def logout():
    logout_user()  
    return jsonify({"message": "התנתקת בהצלחה"}), 200  


# @app.route('/create_candidate', methods=['GET'])
# def create_candidate():
#     today = datetime.today().strftime('%Y-%m-%d')
#     candidate_data = {"stage": 1, "name": "matan ohana", "job": "technician", "phone_sum": "bla bla", "phone_sum_date": today, "interview_sum": "bla bla", "years_exp": 2.5, "security_clearance": False, "safety": True, "101": False, "interview_date": today, "grade": 5, "field_exp": "yada yada", "add_info": "", "user_added": "admin"}
#     candidates.insert_one(candidate_data)
#     return 'Candidate Created'


@app.route('/allCandidates')
@login_required
def allCandidates():
    candidates_list = candidates.find() 
    candidates_list = [candidate for candidate in candidates_list] 
    for candidate in candidates_list:
        candidate['_id'] = str(candidate['_id']) 
    return jsonify(candidates_list), 200 


@app.route('/updateCandidate/<id>', methods=['PUT'])
def update_candidate(id):
    data = request.json  
    
    if "_id" in data:
        data.pop("_id")

 
    updated_candidate = candidates.find_one_and_update(
        {'_id': ObjectId(id)},
        {'$set': data},
        return_document=True  
    )

    if updated_candidate:

        updated_candidate['_id'] = str(updated_candidate['_id'])
        return jsonify({"message": "המועמד עודכן בהצלחה", "updated_candidate": updated_candidate}), 200
    else:
        return jsonify({"error": "מועמד לא נמצא"}), 404
    


@app.route('/export_candidates', methods=['GET'])
def export_candidates():

    candidates_data = list(candidates.find({}))
    

    df = pd.DataFrame(candidates_data)
    

    if '_id' in df.columns:
        df.drop(columns=['_id'], inplace=True)
    

    output = io.BytesIO()
    

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Candidates')
    

    output.seek(0)
    

    return send_file(output, as_attachment=True, download_name='candidates.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        



if __name__ == '__main__':
    app.run(debug=True, port=5000)
