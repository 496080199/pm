from app import app,rbac
from flask import g,current_app,render_template



@app.route('/')
@rbac.allow(['anonymous'], methods=['GET'])
def index():
    return render_template('index.html')