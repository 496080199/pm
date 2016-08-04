# coding: utf-8
from app import app,db,login_manager
from flask import g,render_template,flash,redirect,send_from_directory
from flask_login import login_user,logout_user,current_user,login_required
from .forms import *
from .models import *
import hashlib
from random import randint
from werkzeug import secure_filename



@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/login')
@app.before_request
def before_request():
    g.user = current_user




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated():
        return redirect('/dash')
    form=RegisterForm()
    if form.validate_on_submit():
        user=User()
        user.username=form.username.data
        user.password_hash=hashlib.md5(form.password.data).hexdigest()
        user.phone=form.phone.data
        db.session.add(user)
        db.session.commit()
        flash('注册成功')
        return redirect('/login')
    return render_template('register.html',form=form)
@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated():
        return redirect('/dash')
    form=LoginForm()     
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user and hashlib.md5(form.password.data).hexdigest()== user.password_hash:
            login_user(user)
            return redirect('/dash')
    return render_template('login.html',form=form)
@app.route("/edituser",methods=['GET','POST'])
@login_required
def edituser():
    form=UserForm()
    if form.validate_on_submit():
        current_user.nickname=form.nickname.data
        if form.img.data:
            filename = str(randint(0,9))+str(randint(0,9))+str(randint(0,9))+secure_filename(form.img.data.filename)
            form.img.data.save(app.config['IMG_PATH']+'/'+filename)
            current_user.img=filename
        
        db.session.commit()
        return redirect('/dash')
    form.nickname.data=current_user.nickname
    form.img.data=current_user.img
    return render_template('edituser.html',form=form)
@app.route('/img/<filename>')
def uploaded_img(filename):
    return send_from_directory(app.config['IMG_PATH'],filename)
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/dash')
@login_required
def dash():
    return render_template('dash.html')
@app.route('/addshop',methods=['GET','POST'])
@login_required
def addshop():
    form=ShopForm()
    if form.validate_on_submit():
        shop=Shop(shopname=form.shopname.data,province=form.province.data,city=form.city.data,area=form.area.data,address=form.address.data,zipcode=form.zipcode.data,telphone=form.telphone.data)
        db.session.add(shop)
        db.session.commit()
        current_user.shop_id=shop.id
        current_user.role=1
        db.session.commit()
        flash('创建店铺成功.')
        return redirect('/dash')
    return render_template('shop.html',title='创建店铺',action='addshop',form=form)
@app.route('/editshop',methods=['GET','POST'])
@login_required
def editshop():
    shop=current_user.shop
    form=ShopForm()
    if form.validate_on_submit():
        shop.shopname=form.shopname.data
        shop.province=form.province.data
        shop.city=form.city.data
        shop.area=form.area.data
        shop.address=form.address.data
        shop.zipcode=form.zipcode.data
        shop.telphone=form.telphone.data
        db.session.commit()
        flash('修改店铺成功.')
        return redirect('/dash')
    form.shopname.data=shop.shopname
    form.province.data=shop.province
    form.city.data=shop.city
    form.area.data=shop.area
    form.address.data=shop.address
    form.zipcode.data=shop.zipcode
    form.telphone.data=shop.telphone
    return render_template('shop.html',title='修改店铺',action='editshop',form=form)

@app.route('/personmanage')
@login_required
def personmanage():
    return redirect('/staff')

@app.route('/staff')
@login_required
def staff():
    staffs=User.query.filter_by(shop_id=current_user.shop_id).filter_by(role=2)
    return render_template('staff.html',staffs=staffs)

@app.route('/staff_add',methods=['GET','POST'])
@login_required
def staff_add():
    form=StaffForm()
    if form.validate_on_submit():
        user=User(username=current_user.username+'_'+form.username.data,password_hash=hashlib.md5(form.password.data).hexdigest(),phone=form.phone.data,nickname=form.nickname.data,shop_id=current_user.shop_id,role=2)
        db.session.add(user)
        db.session.commit()
        flash('员工添加成功')
        return redirect('/staff')
    return render_template('staff_add.html',form=form)
@app.route('/staff_password')
@login_required
def staff_password():
    pass

@app.route('/teacher')
@login_required
def teacher():
    teachers=Teacher.query.filter_by(shop_id=current_user.shop_id)
    return render_template('teacher.html',teachers=teachers)

@app.route('/teacher_add',methods=['GET','POST'])
@login_required
def teacher_add():
    form=TeacherForm()
    form.course_id.choices = [(g.id, g.name) for g in Course.query.all()]
    if form.validate_on_submit():
        teacher=Teacher()
        teacher.firstname=form.firstname.data
        teacher.lastname=form.lastname.data
        teacher.sex=form.sex.data
        teacher.phone=form.phone.data
        teacher.wx=form.wx.data
        teacher.course_id=form.course_id.data
        teacher.fee=form.fee.data
        
        filename = 'teacher_education_'+str(randint(0,9))+str(randint(0,9))+str(randint(0,9))+secure_filename(form.education.data.filename)
        form.education.data.save(app.config['IMG_PATH']+'/'+filename)
        teacher.education=filename
        
        if form.certificate.data:
            filename = 'teacher_certificate_'+str(randint(0,9))+str(randint(0,9))+str(randint(0,9))+secure_filename(form.certificate.data.filename)
            form.certificate.data.save(app.config['IMG_PATH']+'/'+filename)
            teacher.certificate=filename
        
        teacher.resume=form.resume.data
        
        teacher.shop_id=current_user.shop_id
        db.session.add(teacher)
        db.session.commit()
        flash('老师添加成功')
        return redirect('/teacher')
    return render_template('teacher_add.html',form=form)