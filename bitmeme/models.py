import datetime

from flask.ext.bcrypt import generate_password_hash
from flask.ext.login import UserMixin
from peewee import *

db = SqliteDatabase('users.db')


class User(UserMixin, Model):
    username = CharField(unique=True)
    password = CharField(max_length=20)
    email = CharField(unique=True)
    confirmed = BooleanField(default=False)
    confirmed_on = DateTimeField(default=datetime.datetime.now())
    joined_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
        order_by = ('-joined_at', )

    def get_posts(self):
        return Post.select().where(Post.user == self)

    def get_feed(self):
        return Post.select().where((Post.user << self.following())
                                   and (Post.user == self))

    def following(self):
        """The users that we are following."""
        return (User.select().join(Relationship,
                                   on=Relationship.to_user).where(
                                       Relationship.from_user == self))

    def followers(self):
        """Get users following the current user"""
        return (User.select().join(Relationship,
                                   on=Relationship.from_user).where(
                                       Relationship.to_user == self))

    @classmethod
    def create_user(cls, username, email, password, confirmed):
        try:
            with db.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    confirmed=False)
        except IntegrityError:
            raise ValueError("User already exists")


class Post(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(rel_model=User, related_name='posts')
    content = TextField()
    image = CharField()

    class Meta:
        database = db
        order_by = ('-timestamp', )


class Comment(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(rel_model=User, related_name='comments')
    post = IntegerField()
    content = TextField()

    class Meta:
        database = db
        order_by = ('timestamp', )


class Relationship(Model):
    from_user = ForeignKeyField(User, related_name='relationships')
    to_user = ForeignKeyField(User, related_name='related_to')

    class Meta:
        database = db
        indexes = ((('from_user', 'to_user'), True), )


def init():
    db.connect()
    db.create_tables([User, Post, Relationship, Comment], safe=True)
    db.close()
