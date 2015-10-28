from flask.ext.script import Manager
from flask_migrate import MigrateCommand
from Super_Wicked_File_Sharing_Service import create_app
from Super_Wicked_File_Sharing_Service.extensions import celery

"""
This script is used for running the application locally as
well as migrating and managing the database.
It also is used to provide the celery instance that is
daemonized
"""
app = create_app()

manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
