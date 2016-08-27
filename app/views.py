# coding: utf-8
from app import app,db,login_manager
from flask import current_app,g,render_template,flash,redirect,send_from_directory,request,session
from flask_login import login_user,logout_user,current_user,login_required
from .forms import *
from .models import *
import hashlib
from random import randint
from werkzeug import secure_filename
import flask_excel 
from flask_principal import Principal, Identity, AnonymousIdentity,identity_changed,identity_loaded, RoleNeed, UserNeed,Permission


POSTS_PER_PAGE=20

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/login')


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user

    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.name))

boss_permission = Permission(RoleNeed(u'老板'))




@app.route('/')

def index():
    return render_template('index.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated():
        return redirect('/dash')
    form=RegisterForm()
    if form.validate_on_submit():
        boss = Role('boss') 
        user=User(roles=[boss])
        user.username=form.username.data
        user.password_hash=hashlib.md5(form.password.data).hexdigest()
        user.phone=form.phone.data
        user.owner=1
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
            identity_changed.send(current_app._get_current_object(),
                                  identity=Identity(user.id))
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
    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())
    return redirect('/')

@app.route('/dash')
@login_required
@boss_permission.require()
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
    staffs=User.query.filter_by(owner=0).filter_by(shop_id=current_user.shop_id)
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
@app.route('/staff_password/<int:id>',methods=['GET','POST'])
@login_required
def staff_password(id):
    staff=User.query.filter_by(shop_id=current_user.shop_id).filter_by(id=id).first()
    form=StaffPasswordForm()
    if form.validate_on_submit():
        staff.password_hash=hashlib.md5(form.password.data).hexdigest()
        db.session.commit()
        flash('员工密码修改成功')
        return redirect('/staff')
    return render_template('staff_password.html',form=form,staff=staff)

@app.route('/staff_edit/<int:id>',methods=['GET','POST'])
@login_required
def staff_edit(id):
    staff=User.query.filter_by(shop_id=current_user.shop_id).filter_by(id=id).first()
    form=StaffEditForm()
    if form.validate_on_submit():
        if form.nickname.data:
            staff.nickname=form.nickname.data
            db.session.commit()
        if form.phone.data:
            staff.phone=form.phone.data
            db.session.commit()
        flash('员工资料修改成功')
        return redirect('/staff')
    return render_template('staff_edit.html',form=form,staff=staff)
@app.route('/staff_del/<int:id>')
@login_required
def staff_del(id):
    staff=User.query.filter_by(shop_id=current_user.shop_id).filter_by(id=id).first()
    db.session.delete(staff)
    db.session.commit()
    flash('员工删除成功')
    return redirect('/staff')

@app.route('/teacher')    
@app.route('/teacher/<int:page>')
@login_required
def teacher(page=1):
    pagination=Teacher.query.filter_by(shop_id=current_user.shop_id).paginate(page,POSTS_PER_PAGE, False)
    teachers=pagination.items
    return render_template('teacher.html',teachers=teachers,pagination=pagination)

@app.route('/teacher_add',methods=['GET','POST'])
@login_required
def teacher_add():
    form=TeacherForm()
    form.course.choices = [(course.name, course.name) for course in Course.query.filter_by(shop_id=current_user.shop_id)]
    if form.validate_on_submit():
        teacher=Teacher()
        teacher.firstname=form.firstname.data
        teacher.lastname=form.lastname.data
        teacher.sex=form.sex.data
        teacher.phone=form.phone.data
        teacher.wx=form.wx.data
        teacher.course=form.course.data
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
@app.route('/teacher_edit/<int:id>',methods=['GET','POST'])
@login_required
def teacher_edit(id):
    teacher=Teacher.query.filter_by(shop_id=current_user.shop_id).filter_by(id=id).first()
    form=TeacherForm()
    form.course.choices = [(course.name, course.name) for course in Course.query.filter_by(shop_id=current_user.shop_id)]
    if form.validate_on_submit():
        teacher.firstname=form.firstname.data
        teacher.lastname=form.lastname.data
        teacher.sex=form.sex.data
        teacher.phone=form.phone.data
        teacher.wx=form.wx.data
        teacher.course=form.course.data
        teacher.fee=form.fee.data
        
        if form.education.data:
            filename = 'teacher_education_'+str(randint(0,9))+str(randint(0,9))+str(randint(0,9))+secure_filename(form.education.data.filename)
            form.education.data.save(app.config['IMG_PATH']+'/'+filename)
            teacher.education=filename
        
        if form.certificate.data:
            filename = 'teacher_certificate_'+str(randint(0,9))+str(randint(0,9))+str(randint(0,9))+secure_filename(form.certificate.data.filename)
            form.certificate.data.save(app.config['IMG_PATH']+'/'+filename)
            teacher.certificate=filename
        
        teacher.resume=form.resume.data
        db.session.commit()
        flash('老师资料修改成功')
        return redirect('/teacher')
    form.firstname.data=teacher.firstname
    form.lastname.data=teacher.lastname
    form.sex.data=teacher.sex
    form.phone.data=teacher.phone
    form.wx.data=teacher.wx
    form.course.data=teacher.course
    form.fee.data=teacher.fee
    form.education.data=teacher.education
    form.resume.data=teacher.resume
    return render_template('teacher_edit.html',form=form,teacher=teacher)
@app.route('/teacher_del/<int:id>')
@login_required
def teacher_del(id):
    teacher=Teacher.query.filter_by(shop_id=current_user.shop_id).filter_by(id=id).first()
    db.session.delete(teacher)
    db.session.commit()
    flash('老师删除成功')
    return redirect('/teacher')

@app.route("/teacher_import", methods=['GET', 'POST'])
def teacher_import():
    if request.method == 'POST':
        def teacher_init_func(row):
            teacher = Teacher()
            teacher.firstname=row['firstname']
            teacher.lastname=row['lastname']
            teacher.fee=row['fee']
            teacher.course=row['course']
            teacher.sex=row['sex']
            teacher.resume=row['resume']
            teacher.phone=row['phone']
            teacher.wx=row['wx']
            teacher.shop_id=current_user.shop_id
            return teacher
        
        request.save_to_database(field_name='file', session=db.session,
                                      table=Teacher,
                                      initializer=teacer_init_func)
        return redirect('/teacher')
    return render_template('teacher_import.html')
@app.route("/teacher_export", methods=['GET'])
def teacher_export():
    teachers=Teacher.query.filter_by(shop_id=current_user.shop_id)
    
    column_names = ['firstname', 'lastname','sex','phone','wx','course','fee','resume']
    return flask_excel.make_response_from_query_sets(teachers,column_names, "xls")

@app.route('/student')    
@app.route('/student/<int:page>')
@login_required
def student(page=1):
    pagination=Student.query.filter_by(shop_id=current_user.shop_id).paginate(page,POSTS_PER_PAGE, False)
    students=pagination.items
    return render_template('student.html',students=students,pagination=pagination)

@app.route('/student_add',methods=['GET','POST'])
@login_required
def student_add():
    form=StudentForm()
    form.course.choices = [(course.name, course.name) for course in Course.query.filter_by(shop_id=current_user.shop_id)]
    if form.validate_on_submit():
        student=Student()
        student.firstname=form.firstname.data
        student.lastname=form.lastname.data
        student.sex=form.sex.data
        student.course=form.course.data
        student.school=form.school.data
        student.phone1=form.phone1.data
        student.province=form.province.data
        student.city=form.city.data
        student.area=form.area.data
        student.address=form.address.data
        student.parent=form.parent.data
        student.phone2=form.phone2.data
        
        
        student.shop_id=current_user.shop_id
        db.session.add(student)
        db.session.commit()
        flash('学生添加成功')
        return redirect('/student')
    return render_template('student_add.html',form=form)
@app.route('/student_edit/<int:id>',methods=['GET','POST'])
@login_required
def student_edit(id):
    student=Student.query.filter_by(shop_id=current_user.shop_id).filter_by(id=id).first()
    form=StudentForm()
    form.course.choices = [(course.name, course.name) for course in Course.query.filter_by(shop_id=current_user.shop_id)]
    if form.validate_on_submit():
        student.firstname=form.firstname.data
        student.lastname=form.lastname.data
        student.sex=form.sex.data
        student.course=form.course.data
        student.school=form.school.data
        student.phone1=form.phone1.data
        student.province=form.province.data
        student.city=form.city.data
        student.area=form.area.data
        student.address=form.address.data
        student.parent=form.parent.data
        student.phone2=form.phone2.data
        db.session.commit()
        flash('修改学生资料成功')
        return redirect('/student')
    form.firstname.data=student.firstname
    form.lastname.data=student.lastname
    form.sex.data=student.sex
    form.course.data=student.course
    form.school.data=student.school
    form.phone1.data=student.phone1
    form.province.data=student.province
    form.city.data=student.city
    form.area.data=student.area
    form.address.data=student.address
    form.parent.data=student.parent
    form.phone2.data=student.phone2
    return render_template('student_edit.html',form=form,student=student)
@app.route('/student_del/<int:id>')
@login_required
def student_del(id):
    student=Student.query.filter_by(shop_id=current_user.shop_id).filter_by(id=id).first()
    db.session.delete(student)
    db.session.commit()
    flash('删除学生成功')
    return redirect('/student')
@app.route("/student_import", methods=['GET', 'POST'])
def student_import():
    if request.method == 'POST':
        def student_init_func(row):
            #shop_id=Shop.query.filter_by(shopname=row['shop_id']).first()
            student = Student()
            student.firstname=row['firstname']
            student.lastname=row['lastname']
            student.school=row['school']
            student.course=row['course']
            student.sex=row['sex']
            student.province=row['province']
            student.city=row['city']
            student.area=row['area']
            student.address=row['address']
            student.parent=row['parent']
            student.phone1=row['phone1']
            student.phone2=row['phone2']
            student.shop_id=current_user.shop_id
            return student
        
        request.save_to_database(field_name='file', session=db.session,
                                      table=Student,
                                      initializer=student_init_func)
        return redirect('/student')
    return render_template('student_import.html')
@app.route("/student_export", methods=['GET'])
def student_export():
    students=Student.query.filter_by(shop_id=current_user.shop_id)
    
    column_names = ['firstname', 'lastname','course','sex','phone1','school','province','city','area','address','parent','phone2']
    return flask_excel.make_response_from_query_sets(students,column_names, "xls")



@app.route('/coursemanage')
@login_required
def coursemanage():
    return redirect('/course')


@app.route('/course')    
@app.route('/course/<int:page>')
@login_required
def course(page=1):
    pagination=Course.query.filter_by(shop_id=current_user.shop_id).paginate(page,POSTS_PER_PAGE, False)
    courses=pagination.items
    return render_template('course.html',courses=courses,pagination=pagination)
