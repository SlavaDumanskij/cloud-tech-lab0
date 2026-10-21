import os
from flask import Flask,jsonify,request,send_from_directory
import psycopg2

app=Flask(__name__,static_folder='static')

DB_HOST=os.getenv('DB_HOST','localhost')
DB_PORT=os.getenv('DB_PORT','5432')
DB_NAME=os.getenv('DB_NAME','notes_db')
DB_USER=os.getenv('DB_USER','postgres')
DB_PASS=os.getenv('DB_PASS','postgres')

def get_db():
    return psycopg2.connect(host=DB_HOST,port=DB_PORT,dbname=DB_NAME,user=DB_USER,password=DB_PASS)

def init_db():
    conn=get_db()
    cur=conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            text TEXT NOT NULL
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def index():
    return send_from_directory('static','index.html')

@app.route('/api/notes',methods=['GET'])
def get_notes():
    conn=get_db()
    cur=conn.cursor()
    cur.execute('SELECT id, text FROM notes ORDER BY id DESC;')
    rows=cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{'id':r[0],'text':r[1]} for r in rows])

@app.route('/api/notes',methods=['POST'])
def add_note():
    data=request.get_json() or {}
    text=data.get('text','').strip()
    if not text:
        return jsonify({'error':'Empty text'}),400
    conn=get_db()
    cur=conn.cursor()
    cur.execute('INSERT INTO notes (text) VALUES (%s) RETURNING id;',(text,))
    new_id=cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'id':new_id,'text':text}),201

if __name__=='__main__':
    init_db()
    app.run(host='0.0.0.0',port=5000,debug=True)
