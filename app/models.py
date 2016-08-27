# coding: utf-8
from app import app,db
from flask import g
from flask_login import current_user



class Role(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    
    
users_roles = db.Table(
    'users_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)


class User(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    phone=db.Column(db.String(128))
    
    nickname=db.Column(db.String(50),default='未设置的昵称')
    img=db.Column(db.String(100),default='default.jpg')
    owner=db.Column(db.Integer,default=0)
    
    shop_id=db.Column(db.Integer,db.ForeignKey('shop.id'))
    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return unicode(self.id)
 

    
    roles = db.relationship(
        'Role',
        secondary=users_roles,
        backref=db.backref('roles', lazy='dynamic')
    )

    def add_role(self, role):
        self.roles.append(role)

    def add_roles(self, roles):
        for role in roles:
            self.add_role(role)

    def get_roles(self):
        for role in self.roles:
            yield role




class Shop(db.Model):
    __tablename__ = 'shop'
    id = db.Column(db.Integer, primary_key = True)
    shopname = db.Column(db.String(150), unique=True, index=True)
    province=db.Column(db.String(100))
    city=db.Column(db.String(100))
    area=db.Column(db.String(100))
    address=db.Column(db.String(100))
    zipcode=db.Column(db.String(6))
    telphone=db.Column(db.String(15))
    users = db.relationship('User', backref='shop',lazy='dynamic')
    teachers = db.relationship('Teacher', backref='shop',lazy='dynamic')
    students = db.relationship('Student', backref='shop',lazy='dynamic')
    courses = db.relationship('Course', backref='shop',lazy='dynamic')
class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key = True)
    name=db.Column(db.String(30))
    shop_id=db.Column(db.Integer,db.ForeignKey('shop.id'))
    schedules = db.relationship('Schedule', backref='course',lazy='dynamic')
    
class Teacher(db.Model):
    __tablename__ = 'teacher'
    id = db.Column(db.Integer, primary_key = True)
    firstname=db.Column(db.String(30))
    lastname=db.Column(db.String(30))
    sex=db.Column(db.String(10))
    phone=db.Column(db.String(15))
    wx=db.Column(db.String(15))
    course=db.Column(db.String(30))
    fee=db.Column(db.Integer)
    education=db.Column(db.String(100))
    certificate=db.Column(db.String(100))
    resume=db.Column(db.Text)
    shop_id=db.Column(db.Integer,db.ForeignKey('shop.id'))
class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key = True)
    firstname=db.Column(db.String(30))
    lastname=db.Column(db.String(30))
    course=db.Column(db.String(30))
    sex=db.Column(db.String(10))
    school=db.Column(db.String(100))
    province=db.Column(db.String(100))
    city=db.Column(db.String(100))
    area=db.Column(db.String(100))
    address=db.Column(db.String(100))
    parent=db.Column(db.String(100))
    phone1=db.Column(db.String(15))
    phone2=db.Column(db.String(15))
    shop_id=db.Column(db.Integer,db.ForeignKey('shop.id'))
    

class Schedule(db.Model):
    __tablename__ = 'schedule'
    id = db.Column(db.Integer, primary_key = True)
    start_time=db.Column(db.Time)
    stop_time=db.Column(db.Time)
    teacher_id=db.Column(db.Integer)
    student_id=db.Column(db.Integer)
    status=db.Column(db.Integer)
    reason=db.Column(db.Integer)
    course_id=db.Column(db.Integer,db.ForeignKey('course.id'))
    def get_teacher_name(self,id):
        teacher_name=Teacher.query.get(id)
        return teacher_name
    def get_student_name(self,id):
        student_name=Student.query.get(id)
        return student_name
    
    



