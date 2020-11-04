from app import app
from flask import flash, render_template, redirect, url_for, request, session
from flask_login import LoginManager, login_required, login_user, logout_user
from models import User
from forms import UserLoginForm, UserRegisterForm

# Configure login manager
app.config['USE_SESSION_FOR_NEXT'] = True
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
login_manager.login_message = None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():

    form = UserLoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate_user(username, password)
        if not user:
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=True)

        return redirect(url_for('index'))

    return render_template('auth/login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():

    form = UserRegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        user = User.create_user(username, email, password)
        if not user:
            flash('A user is already registered with that email or username')
            return redirect(url_for('register'))
        login_user(user, remember=True)
        return redirect(url_for('index'))
    return render_template('auth/register.html', form=form)

@app.route('/logout', methods=['POST'])
@login_required
def logout():

    session.clear()
    logout_user()
    return redirect(url_for('login'))