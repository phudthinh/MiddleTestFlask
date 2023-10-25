from main import db, app
from sqlalchemy import Sequence
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, Sequence('user_id_seq'), primary_key=True)
    first_name = db.Column(db.String(255), index = True, nullable = False)
    last_name = db.Column(db.String(255), index = True, nullable = False)
    email = db.Column(db.String(255), index = True, unique = True, nullable = False)
    password_hash = db.Column(db.String(1024), nullable = False)

    tasks = relationship("Task", back_populates="user")

    projects = relationship("Project", back_populates="user")

    def __repr__(self):
        return '<User full name: {} {}, email: {}>' .format(self.first_name, self.last_name, self.email)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Status(db.Model):
    status_id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable = False)

class Project(db.Model):
    project_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable = False)
    description = db.Column(db.String(255))
    deadline = db.Column(db.DateTime)

    status_id = db.Column(db.Integer, db.ForeignKey('status.status_id'))
    status = db.relationship('Status', backref='projects')

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    user = db.relationship('User', back_populates='projects')

    def __repr__(self):
        return '<Project name: {} of user {}>' .format(self.name, self.user_id)

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255))

    project_id = db.Column(db.Integer, db.ForeignKey('project.project_id'))
    project = db.relationship('Project', backref='tasks')

    status_id = db.Column(db.Integer, db.ForeignKey('status.status_id'))
    status = db.relationship('Status', backref='tasks')
    
    priority_id = db.Column(db.Integer, db.ForeignKey('priority.priority_id'))
    priority = db.relationship('Priority', back_populates='tasks')
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    user = db.relationship('User', back_populates='tasks')

    deadline = db.Column(db.DateTime)

    def __repr__(self):
        return '<Task description: {} of user {}>'.format(self.description, self.user_id)
    
    def getPriorityClasss(self):
        if self.priority_id == 1:
            return "table-danger"
        elif self.priority_id == 2:
            return "table-warning"
        elif self.priority_id == 3:
            return "table-info"
        else:
            return "table-primary"
    
class Priority(db.Model):
    priority_id = db.Column(db.Integer, Sequence('priority_id_seq'), primary_key=True)
    text = db.Column(db.String(255), nullable = False)

    tasks = relationship("Task", back_populates="priority")

    def __repr__(self):
        return '<Priority text: {} with {}>'.format(self.priority_id, self.text)