from datetime import datetime, timezone
from hashlib import md5
from app import db, login
from flask_login import UserMixin # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
import sqlalchemy as sa # type: ignore
import sqlalchemy.orm as so # type: ignore
from time import time
import jwt # type: ignore
from app import app


followers = sa.Table(
    'followers',
    db.metadata,
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(256))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    posts = so.relationship('Post', back_populates='author')

    following = so.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers'
    )
    followers = so.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def follow(self, user):
        if not self.is_following(user):
            self.following.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        return user in self.following

    def followers_count(self):
        return len(self.followers)

    def following_count(self):
        return len(self.following)
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:  # noqa: E722
            return
        return db.session.get(User, id)
    
    
    def following_posts(self):
        followed_ids = [u.id for u in self.following]
        followed_ids.append(self.id)
        return sa.select(Post).where(Post.user_id.in_(followed_ids)).order_by(Post.timestamp.desc())
    

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = so.relationship('User', back_populates='posts')


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))