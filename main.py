from flask import Flask, render_template, request, redirect, url_for, flash, session
from forms import SignUpForm, SignInForm, TaskForm, ProjectForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

import models

@app.route('/')
def main():
    if 'user' in session:
        return redirect('/userHome')
    
    todoList = [
        {
            'name': 'Do homework',
            'description': 'Math, science, history'
        },
        {
            'name': 'Clean room',
            'description': 'Put everything in its place'
        }
    ]

    return render_template('index.html', todoList=todoList)

@app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    form = SignUpForm()
    if form.validate_on_submit():
        print("Validate on submit")
        _fname = form.inputFirstName.data
        _lname = form.inputLastName.data
        _email = form.inputEmail.data
        _password = form.inputPassword.data
        
        newUser = models.User(first_name=_fname, last_name=_lname, email=_email)
        newUser.set_password(_password)
        db.session.add(newUser)
        db.session.commit()

        return render_template('signUpSuccess.html', user = newUser)
    else:
        return render_template('signUp.html', form=form)
    
@app.route('/signIn', methods=['GET', 'POST'])
def signIn():
    form = SignInForm()

    if form.validate_on_submit():
        _email = form.inputEmail.data
        _password = form.inputPassword.data

        user = db.session.query(models.User).filter_by(email=_email).first()
        if(user is None):
            flash("Email or password is incorrect")
        else:
            if(user.check_password(_password)):
                session['user'] = user.user_id
                return redirect('/userHome')
            else:
                flash("Email or password is incorrect")
    return render_template('signIn.html', form=form)

@app.route('/userHome')
def userHome():
    _user_id = session.get('user')
    
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        projects = db.session.query(models.Project).filter_by(user_id=_user_id).all()
        tasks = db.session.query(models.Task).filter_by(user_id=_user_id).all()
        for project in projects:
            updateProjectStatus(project.project_id)

        return render_template('userHome.html', user=user, projects=projects, tasks=tasks)
    else:
        return redirect('/')
    
@app.route('/newProject', methods=['GET', 'POST'])
def newProject():
    _user_id = session.get('user')
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        form = ProjectForm()
        form.inputStatus.choices = [(p.status_id, p.text) for p in db.session.query(models.Status).all()]

        if request.method == 'POST' and form.validate_on_submit():
            project_name = form.inputName.data
            project_description = form.inputDescription.data
            project_deadline = form.inputDeadline.data
            _status_id = form.inputStatus.data
            status = db.session.query(models.Status).filter_by(status_id=_status_id).first()
            
            _project_id = request.form['project_id']
            if (_project_id == "0"):
                new_project = models.Project(
                    name=project_name,
                    description=project_description,
                    deadline=project_deadline,
                    status=status,
                    user=user
                )
                db.session.add(new_project)
            else:
                project = db.session.query(models.Project).filter_by(project_id=_project_id).first()
                project.name = project_name
                project.description = project_description
                project.deadline = project_deadline
                project.status = status

            db.session.commit()

            return redirect('/userHome')

        return render_template('newProject.html', form=form, user=user)

    return redirect('/')

@app.route('/editProject', methods=['GET', 'POST'])
def editProject():
    _user_id = session.get('user')
    form = ProjectForm()
    form.inputStatus.choices = [(p.status_id, p.text) for p in db.session.query(models.Status).all()]
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        _project_id = request.form['project_id']
        if _project_id:
            project = db.session.query(models.Project).filter_by(project_id=_project_id).first()
            form.inputName.default = project.name
            form.inputDescription.default = project.description
            form.inputDeadline.default = project.deadline
            form.inputStatus.default = project.status_id
            form.process()
            return render_template('/newProject.html', form=form, user=user, project=project)
                
    return redirect('/')

@app.route('/deleteProject', methods=['GET', 'POST'])
def deleteProject():
    _user_id = session.get('user')
    if _user_id:
        _project_id = request.form.get('project_id')
        if _project_id:
            project = db.session.query(models.Project).filter_by(project_id=_project_id).first()
            db.session.delete(project)
            db.session.commit()

        return redirect('/userHome')
    
    return redirect('/')

@app.route('/newTask', methods=['GET', 'POST'])
def newTask():
    _user_id = session.get('user')
    form = TaskForm()
    form.inputPriority.choices = [(p.priority_id, p.text) for p in db.session.query(models.Priority).all()]
    form.inputStatus.choices = [(p.status_id, p.text) for p in db.session.query(models.Status).all()]
    form.inputProjectID.choices = [(p.project_id, p.name) for p in db.session.query(models.Project).all()]

    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        if form.validate_on_submit():
            _description = form.inputDescription.data
            _priority_id = form.inputPriority.data
            _deadline = form.inputDeadline.data
            priority = db.session.query(models.Priority).filter_by(priority_id=_priority_id).first()
            _status_id = form.inputStatus.data
            status = db.session.query(models.Status).filter_by(status_id=_status_id).first()
            _project_id = form.inputProjectID.data
            project = db.session.query(models.Project).filter_by(project_id=_project_id).first()
            _task_id = request.form['task_id']

            if project.deadline and form.inputDeadline.data > project.deadline.date():
                flash("Task deadline cannot be later than project deadline.")
                return redirect('/newTask')
            
            if _task_id == "0":
                task = models.Task(
                    description=_description,
                    priority=priority,
                    status=status,
                    deadline=_deadline,
                    project=project,
                    user=user
                )
                db.session.add(task)
            else:
                task = db.session.query(models.Task).filter_by(task_id=_task_id).first()
                task.description = _description
                task.priority = priority
                task.status = status
                task.deadline = _deadline
                task.project = project

            db.session.commit()
            return redirect('/userHome')
        
        return render_template('newTask.html', form=form, user=user)
    
    return redirect('/')

@app.route('/editTask', methods=['GET', 'POST'])
def editTask():
    _user_id = session.get('user')
    form = TaskForm()
    form.inputPriority.choices = [(p.priority_id, p.text) for p in db.session.query(models.Priority).all()]
    form.inputStatus.choices = [(p.status_id, p.text) for p in db.session.query(models.Status).all()]
    form.inputProjectID.choices = [(p.project_id, p.name) for p in db.session.query(models.Project).all()]

    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        _task_id = request.form['task_id']

        if _task_id:
            task = db.session.query(models.Task).filter_by(task_id=_task_id).first()
            form.inputDescription.default = task.description
            form.inputPriority.default = task.priority_id
            form.inputStatus.default = task.status_id
            form.inputProjectID.default = task.project_id
            form.inputDeadline.default = task.deadline
            project_deadline = task.project.deadline
            form.process()

            return render_template('/newTask.html', form=form, user=user, task=task, project_deadline=project_deadline)
        
    return redirect('/')

def updateProjectStatus(project_id):
    project = db.session.query(models.Project).filter_by(project_id=project_id).first()
    tasks = db.session.query(models.Task).filter_by(project_id=project_id).all()

    if any(task.status_id == 2 for task in tasks):
        project.status_id = 2
    else:
        project.status_id = 1
    db.session.commit()

    all_tasks_completed = all(task.status_id == 4 for task in tasks)

    if all_tasks_completed and project.status_id != 4:
        project.status_id = 4
        db.session.commit()



@app.route('/deleteTask', methods=['GET', 'POST'])
def deleteTask():
    _user_id = session.get('user')
    if _user_id:
        _task_id = request.form['task_id']
        if _task_id:
            task = db.session.query(models.Task).filter_by(task_id=_task_id).first()
            db.session.delete(task)
            db.session.commit()

        return redirect('/userHome')
    
    return redirect('/')

@app.route('/signOut')
def signOut():
    session.pop('user', None)
    return redirect('/')

@app.route('/search')
def Search():
    searchStatus = request.args.get('searchStatus')
    searchProject = request.args.get('searchProject')
    if searchStatus is not None:
        _user_id = session.get('user')
        if _user_id:
            user = db.session.query(models.User).filter_by(user_id=_user_id).first()
            projects = db.session.query(models.Project).filter(models.Project.name.like('%'+searchProject+'%')).all()
            status_id = db.session.query(models.Project).filter(models.Project.status_id.like('%'+searchStatus+'%')).all()
            return render_template('userHome.html', projects=projects, tasks=status_id, user=user)
    else:
        flash("Search field cannot be empty")
    return redirect('/userHome')
    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000', debug=True)