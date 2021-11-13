from flask import current_app

from snakeeyes.blueprints.user.models import User


initial_user = {
    'role': 'admin',
    'username': current_app.config['SEED_ADMIN_USERNAME'],
    'email': current_app.config['SEED_ADMIN_EMAIL'],
    'password': current_app.config['SEED_ADMIN_PASSWORD']
}

if User.find_by_identity(current_app.config['SEED_ADMIN_EMAIL']) is None:
    User(**initial_user).save()
