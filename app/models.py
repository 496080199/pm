# coding: utf-8
from app import app,db
from flask_login import UserMixin

class User(UserMixin,db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    phone=db.Column(db.String(128))
    
    nickname=db.Column(db.String(50),default='未设置的昵称')
    img=db.Column(db.String(100),default='default.jpg')
    
    shop_id=db.Column(db.Integer,db.ForeignKey('shop.id'))
    role=db.Column(db.Integer,default=0)
    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return unicode(self.id)
 
    def __repr__(self):
        return '<User %r>' % (self.name)
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



