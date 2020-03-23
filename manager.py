# encoding: utf-8

from flask_script import Manager
from flask_migrate import Migrate, MigrateConmmand
from SDWZCS import app
from config import db


manager = Manager(app)

#通过migrate绑定app和db
migrate = Migrate(app, db)

#添加迁移脚本的命令到manager中
manager.add_command('db', MigrateConmmand)



if __name__ == "__main__":
    manager.run()
