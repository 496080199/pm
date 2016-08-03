# coding: utf-8
from flask_wtf import Form
from wtforms import StringField,PasswordField
from wtforms.validators import DataRequired,EqualTo,Length,Regexp
from flask_wtf.file import FileField

class RegisterForm(Form):
    username=StringField('用户名',validators=[DataRequired(message='用户名必填')])
    password=PasswordField('密码',validators=[DataRequired(message='密码必填')])
    password2=PasswordField('重复输入密码',validators=[DataRequired(message='重输密码必填'),EqualTo('password',message='密码不一致')])
    phone=StringField('手机号码',validators=[DataRequired(message='手机号码必填'),Length(min=11,max=11,message='请输入11位手机号'),Regexp('^(13[0-9]|14[0-9]|15[0-9]|18[0-9])',message='无效号码')])
class UserForm(Form):
    nickname=StringField('昵称',validators=[DataRequired(message='昵称必填')])
    img=FileField('头像')
class LoginForm(Form):
    username=StringField('用户名',validators=[DataRequired(message='用户名必填')])
    password=PasswordField('密码',validators=[DataRequired(message='密码必填')])
class ShopForm(Form):
    shopname=StringField('店铺名',validators=[DataRequired(message='店铺必填')])
    province=StringField('省')
    city=StringField('市')
    area=StringField('区')
    address=StringField('详细地址',validators=[DataRequired(message='详细地址必填')])
    zipcode=StringField('邮编',validators=[DataRequired(message='邮编必填')])
    telphone=StringField('电话',validators=[DataRequired(message='电话必填')])
class StaffForm(Form):
    username=StringField('用户名',validators=[DataRequired(message='用户名必填')])
    nickname=StringField('昵称',validators=[DataRequired(message='昵称必填')])
    password=PasswordField('密码',validators=[DataRequired(message='密码必填')])
    phone=StringField('手机号码',validators=[DataRequired(message='手机号码必填'),Length(min=11,max=11,message='请输入11位手机号'),Regexp('^(13[0-9]|14[0-9]|15[0-9]|18[0-9])',message='无效号码')])