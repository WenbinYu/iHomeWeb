# -*- coding:utf-8 -*-



from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager
from ihome import get_app,db
from ihome import models
from flask_migrate import Migrate,MigrateCommand




app = get_app('development')

manager = Manager(app)

Migrate(app,db)

manager.add_command('db',MigrateCommand)



if __name__ == '__main__':

    print app.url_map

    app.run()
    # manager.run()