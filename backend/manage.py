from flask_script import Manager
from flask_migrate import MigrateCommand
from backend.app import app, db

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    """
    This script is used to manage the Flask application and perform database migrations.

    Usage:
        python manage.py [command]

    Commands:
        db      Perform database migrations using Flask-Migrate.

    Example:
        python manage.py db init
        python manage.py db migrate
        python manage.py db upgrade
    """
    manager.run()
