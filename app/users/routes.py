from flask import Blueprint,redirect,render_template,url_for,flash,request,session
from app import db,bcrypt,limiter
from app.forms import RegisterForm,LoginForm,UpdateAccount,UpdatePassword,ResetPasswordForm,ResetRequestForm
from app.models import User
from app.users.utilities import save_prof_pic,send_reset_email
from flask_login import login_user,logout_user,current_user,login_required

users=Blueprint('users',__name__)

@users.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm()
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    if form.validate_on_submit():
        hashed_pw=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=User(username=form.username.data,email=form.email.data,password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Your account created successfully. You can login now.')
        return redirect(url_for('users.login'))
    return render_template('register.html',form=form)

@users.route('/login',methods=['GET','POST'])
@limiter.limit("5 per minute")
def login():
    form=LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            response = redirect(url_for('main.home'))
            # Prevent cache of login response
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '-1'
            return response
        else:
            flash('Incorrect email or password. Please check your credentials','danger')
    return render_template('login.html',form=form)

@users.route('/account',methods=['GET','POST'])
@login_required
def account():
    form1 =UpdateAccount()
    form2 =UpdatePassword()
    if request.method=='POST':
        if 'form1_submit' in request.form and form1.validate_on_submit():
            if form1.picture.data:
                pic_file=save_prof_pic(form1.picture.data)
                current_user.image_file=pic_file
            current_user.username=form1.username.data
            current_user.email=form1.email.data
            db.session.commit()
            flash('Profile Updated Successfully','success')
            return redirect(url_for('users.account'))
        elif 'form2_submit' in request.form and form2.validate_on_submit():
            if bcrypt.check_password_hash(current_user.password,form2.old_password.data):
                hashed_pw=bcrypt.generate_password_hash(form2.new_password.data).decode('utf-8')
                current_user.password=hashed_pw
                db.session.commit()
                flash(f"Password changed successfully","success")
                return redirect(url_for('main.home'))
            else:
                flash('Wrong password','danger')
    elif request.method=='GET':
        form1.username.data=current_user.username
        form1.email.data=current_user.email
    img_file=url_for('static',filename='profile_pics/'+current_user.image_file)
    return render_template('account.html',form1=form1,form2=form2,image_file=img_file)


@users.route('/logout')
def logout():
    logout_user()
    session.clear()
    response = redirect(url_for('main.home'))
    # Delete session cookie completely
    response.delete_cookie('remember_token')
    response.delete_cookie('session')
    # Prevent browser back-forward cache
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    response.headers['X-Cache-Control'] = 'no-store'
    return response


@users.route('/reset_password',methods=['GET','POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form=ResetRequestForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email as been sent. Please check your mailbox.','info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html',form=form)

@users.route('/reset_password/<token>',methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    user=User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token','error')
        return redirect(url_for('users.reset_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pw=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password=hashed_pw
        db.session.commit()
        flash('Password updated successfully. Please login','success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html',form=form)