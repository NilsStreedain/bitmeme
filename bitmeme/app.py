from flask import (Flask, g, render_template, flash, redirect, url_for, abort,
                   request, Markup)
from flask.ext.bcrypt import check_password_hash
from flask.ext.login import (LoginManager, login_user, logout_user,
                             login_required, current_user)
from flask_mail import Message, Mail
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from werkzeug.utils import secure_filename
from random import randint

import forms
import models
import os

app = Flask(__name__)
app.config.from_object('config.BaseConfig')
mail = Mail(app)

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


def generate_activation_url(form):
    token = serializer.dumps(form.email.data)
    return url_for('activate', token=token, _external=True)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config[
               'ALLOWED_EXTENSIONS']


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    'Connect to the database before each request.'
    try:
        g.db = models.db
        g.db.connect()
        g.user = current_user
    except models.OperationalError:
        pass


@app.after_request
def after_request(response):
    'Close the database connection after each request.'
    g.db.close()
    return response


@app.route('/', methods=('GET', 'POST'))
def index():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            confirmed=False)
        token = generate_activation_url(form)
        msg = Message(
            recipients=[form.email.data],
            body=render_template('activation_email.html', token=token),
            subject='Welcome!')
        mail.send(msg)

        return render_template('activate.html', form=form)

    if current_user.is_authenticated:
        return redirect(url_for('feed'))
    else:
        return render_template('index.html', form=form)


@app.route('/activate/<token>')
def activate(token, expiration=3600):
    try:
        serializer.loads(token, max_age=expiration)
    except (BadSignature, SignatureExpired):
        abort(404)

    models.User.confirmed = True
    return render_template('emailverified.html')


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash(
                Markup(
                    '<div class="preNote">Incorrect email or password!</div><div class="noteSuf">You have entered the wrong email or password.</div>'
                ), 'error')
        else:
            if check_password_hash(user.password, form.password.data):
                if models.User.confirmed:
                    login_user(user)
                    flash(
                        Markup(
                            '<div class="preNote">You\'ve been logged in!</div><div class="noteSuf">You have been successfully logged into your account.</div>'
                        ), 'success')
                    return redirect(url_for('feed'))

                else:
                    flash(
                        Markup(
                            '<div class="preNote">Your email hasn\'t been verified. </div><div class="noteSuf">Your account hasn\'t been acivated, check your email inbox and junk folder and click the link.</div>'
                        ), 'error')
            else:
                flash(
                    Markup(
                        '<div class="preNote">Your email hasn\'t been verified. </div><div class="noteSuf">Your account hasn\'t been acivated, check your email inbox and junk folder and click the link.</div>'
                    ), 'error')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(
        Markup(
            '<div class="preNote">Logout successful.</div><div class="noteSuf">You have been successfully logged out. Log back in to view your account.</div>'
        ), 'success')
    return redirect(url_for('index'))


@app.route('/post', methods=('GET', 'POST'))
@login_required
def post():
    form = forms.PostForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            file = request.files['image']

            if file and allowed_file(file.filename):
                filename = secure_filename(
                    str(randint(1, 100000000)) + file.filename)
                file.save(os.path.join(app.config['MEDIA_ROOT'], filename))
                models.Post.create(
                    user=g.user._get_current_object(),
                    content=form.content.data.strip(),
                    image=os.path.join(app.config['MEDIA_ROOT'], filename))
                return redirect(url_for('feed'))
            else:
                flash(
                    Markup(
                        '<div class="preNote">File extention not allowed.</div><div class="noteSuf">You can\'t use this type of image or file, try another.</div>'
                    ), 'error')
    return render_template('post.html', form=form)


@app.route('/feed', methods=('GET', 'POST'))
@login_required
def feed():
    feed = models.Post.select().where(
        current_user.following()
        or models.Post.user == g.user._get_current_object()).limit(100)

    # if request.method == 'POST':
    #     if form.validate_on_submit:
    #         models.Comment.create()
    return render_template('feed.html', feed=feed)


@app.route('/feed')
@app.route('/feed/<int:post_id>', methods=('GET', 'POST'))
@login_required
def feed_post(post_id):
    post = models.Post.select().where(models.Post.id == post_id).get()
    form = forms.CommentForm()
    comments = models.Comment.select().limit(100)

    if request.method == 'POST':
        if form.validate_on_submit:
            models.Comment.create(
                user=g.user._get_current_object(),
                post=post,
                content=form.content.data.strip())
            flash(
                Markup('<div class="preNote">Comment Posted!</div>'),
                'success')
            return redirect(url_for('feed_post', post_id=post.id))
    return render_template(
        'feed_post.html',
        form=form,
        post=post,
        comments=comments,
        user=current_user)


@app.route('/feed')
@app.route('/feed/<username>')
@login_required
def user_feed(username=None):
    if username and username != current_user.username:
        try:
            user = models.User.select().where(
                models.User.username**username).get()
            feed = user.posts.limit(100)
        except models.DoesNotExist:
            abort(404)
        else:
            feed = user.posts.limit(100)
    else:
        feed = current_user.get_feed().limit(100)
        user = current_user
    if username:
        template = 'user_feed.html'
    return render_template(template, feed=feed, user=user)


@app.route('/delete_comment/<int:comment_id>')
@login_required
def delete_comment(comment_id):
    comment = models.Comment.select().where(
        models.Comment.id == comment_id).get()
    post = models.Comment.select().where(
        models.Comment.id == comment_id).get().post
    comment.delete_instance()
    flash(Markup('<div class="preNote">Comment deleted!</div>'), 'success')
    return redirect(url_for('feed_post', id=post.id))


@app.route('/follow/<username>')
@login_required
def follow(username):
    try:
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:
        abort(404)
    else:
        try:
            models.Relationship.create(
                from_user=g.user._get_current_object(), to_user=to_user)
        except models.IntegrityError:
            pass
        else:
            flash('Following {}!'.format(to_user.username), 'success')
    return redirect(url_for('user_feed', username=to_user.username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    try:
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:
        abort(404)
    else:
        try:
            models.Relationship.get(
                from_user=g.user._get_current_object(),
                to_user=to_user).delete_instance()
        except models.IntegrityError:
            pass
        else:
            flash('Unfollowed {}'.format(to_user.username), 'success')
    return redirect(url_for('user_feed', username=to_user.username))


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    models.init()
    try:
        models.User.create_user(
            username='foo',
            email='foo@bar.com',
            password='12345678',
            confirmed=True)
    except ValueError:
        pass
    app.run(debug=True, host='localhost', port=8080)
