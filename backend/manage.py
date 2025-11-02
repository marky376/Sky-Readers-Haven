import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from backend.app import create_app, db

# Get config name from environment, default to production
config_name = os.getenv('FLASK_CONFIG', 'production')
app = create_app(config_name)
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
