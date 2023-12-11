import os 
from flask import Flask,render_template,flash,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

##############DATABASE CONFIGURATION#################
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app,db)
app.app_context().push()
##############BLOG MODEL##################

class Posts(db.Model):
    
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(200))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(200))
    
###################FORMS####################

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content',validators=[DataRequired()],widget=TextArea())
    author = StringField('Author',validators=[DataRequired()])
    slug = StringField('Slug',validators=[DataRequired()]) 
    submit = SubmitField('Submit')

##############VIEWS SECTIONS########################

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_post', methods=['GET','POST'])
def add_post():
    posts = Posts.query.all()
    
    form = PostForm()
    
    if form.validate_on_submit():
        
        post = Posts(title=form.title.data,content=form.content.data,author=form.author.data,slug=form.slug.data)
        
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''
        
        db.session.add(post)
        db.session.commit()
        flash('Blog post Submitted Successfully!')
    return render_template('add_post.html', form=form, posts=posts)

@app.route('/posts')
def posts():
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)

@app.route('/posts/delete/<int:id>')
def delete_post(id):
    
    post_to_delete = Posts.query.get_or_404(id)
    
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash('Post deleted successfully!')
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)
    except:
        flash('Please check the page and try again!')
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)

@app.route('/posts/edit/<int:id>')
def edit_post(id):
    
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        
        db.session.add(post)
        db.session.commit()
        flash('Blog post has been updated!')
        return redirect('posts',id=post.id)

    form.title.data = post.title
    form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template('edit_post.html', post=post, form=form)
if __name__ == "__main__":
    app.run(debug=True)