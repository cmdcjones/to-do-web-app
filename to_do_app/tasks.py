from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from to_do_app.auth import login_required
from to_do_app.db import get_db

bp = Blueprint('tasks', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    tasks = db.execute(
        """SELECT id, title, description, created, priority
        FROM task
        ORDER BY
        priority DESC"""
    ).fetchall()
    return render_template('tasks/index.html', tasks=tasks)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        priority = request.form['priority']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                """INSERT INTO task (title, description, priority)
                VALUES (?, ?, ?)""",
                (title, description, priority)
            )
            db.commit()
            return redirect(url_for('tasks.index'))

    return render_template('tasks/create.html')

def get_task(id,):
    task = get_db().execute(
        """SELECT id, title, description, created, priority
        FROM task
        WHERE id = ?""",
        (id,)
    ).fetchone()

    if task is None:
        abort(404, f"Task id {id} doesn't exist.")

    return task

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    task = get_task(id)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                """UPDATE post SET title = ?, description = ?
                WHERE id = ?""",
                (title, description, id)
            )
            db.commit()
            return redirect(url_for('tasks.index'))

    return render_template('tasks/update.html', task=task)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_task(id)
    db = get_db()
    db.execute('DELETE FROM task WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('tasks.index'))