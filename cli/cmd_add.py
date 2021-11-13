import click
import random

from datetime import datetime

from flask import current_app
from flask.cli import with_appcontext
from faker import Faker

from snakeeyes.extensions import db
from snakeeyes.blueprints.user.models import User
from snakeeyes.blueprints.billing.models.invoice import Invoice
from snakeeyes.blueprints.bet.models.bet import Bet
from snakeeyes.blueprints.bet.models.dice import roll

fake = Faker()


def _log_status(count, model_label):
    """
    Log the output of how many records were created.

    :param count: Amount created
    :type count: int
    :param model_label: Name of the model
    :type model_label: str
    :return: None
    """
    click.echo('Created {0} {1}'.format(count, model_label))

    return None


@with_appcontext
def _bulk_insert(model, data, label):
    """
    Bulk insert data to a specific model and log it. This is much more
    efficient than adding 1 row at a time in a loop.

    :param model: Model being affected
    :type model: SQLAlchemy
    :param data: Data to be saved
    :type data: list
    :param label: Label for the output
    :type label: str
    :param skip_delete: Optionally delete previous records
    :type skip_delete: bool
    :return: None
    """
    model.query.delete()

    db.session.commit()
    db.engine.execute(model.__table__.insert(), data)

    _log_status(model.query.count(), label)

    return None


@click.group()
def add():
    """ Add items to the database. """
    pass


@add.command()
@with_appcontext
def users():
    """
    Generate fake users.
    """
    app_config = current_app.config

    random_emails = []
    data = []

    click.echo('Working...')

    # Ensure we get about 100 unique random emails.
    for i in range(0, 99):
        random_emails.append(fake.email())

    random_emails.append(app_config['SEED_ADMIN_EMAIL'])
    random_emails = list(set(random_emails))

    while True:
        if len(random_emails) == 0:
            break

        fake_datetime = fake.date_time_between(
            start_date='-1y', end_date='now').strftime('%s')

        created_on = datetime.utcfromtimestamp(
            float(fake_datetime)).strftime('%Y-%m-%dT%H:%M:%S Z')

        random_percent = random.random()

        if random_percent >= 0.05:
            role = 'member'
        else:
            role = 'admin'

        email = random_emails.pop()

        random_percent = random.random()

        if random_percent >= 0.5:
            random_trail = str(int(round((random.random() * 1000))))
            username = fake.first_name() + random_trail
            last_bet_on = created_on
        else:
            username = None
            last_bet_on = None

        fake_datetime = fake.date_time_between(
            start_date='-1y', end_date='now').strftime('%s')

        current_sign_in_on = datetime.utcfromtimestamp(
            float(fake_datetime)).strftime('%Y-%m-%dT%H:%M:%S Z')

        params = {
            'created_on': created_on,
            'updated_on': created_on,
            'role': role,
            'email': email,
            'username': username,
            'password': User.encrypt_password('password'),
            'sign_in_count': random.random() * 100,
            'coins': 100,
            'last_bet_on': last_bet_on,
            'current_sign_in_on': current_sign_in_on,
            'current_sign_in_ip': fake.ipv4(),
            'last_sign_in_on': current_sign_in_on,
            'last_sign_in_ip': fake.ipv4()
        }

        # Ensure the seeded admin is always an admin with the seeded password.
        if email == app_config['SEED_ADMIN_EMAIL']:
            params['role'] = 'admin'
            params['username'] = app_config['SEED_ADMIN_USERNAME']

            password = User.encrypt_password(app_config['SEED_ADMIN_PASSWORD'])
            params['password'] = password

        data.append(params)

    return _bulk_insert(User, data, 'users')


@add.command()
@with_appcontext
def invoices():
    """
    Generate random invoices.
    """
    data = []

    users = User.query.all()

    for user in users:
        for i in range(0, random.randint(1, 12)):
            # Create a fake unix timestamp in the future.
            created_on = fake.date_time_between(
                start_date='-1y', end_date='now').strftime('%s')
            period_start_on = fake.date_time_between(
                start_date='now', end_date='+1y').strftime('%s')
            period_end_on = fake.date_time_between(
                start_date='now', end_date='+14d').strftime('%s')
            exp_date = fake.date_time_between(
                start_date='now', end_date='+2y').strftime('%s')

            created_on = datetime.utcfromtimestamp(
                float(created_on)).strftime('%Y-%m-%dT%H:%M:%S Z')
            period_start_on = datetime.utcfromtimestamp(
                float(period_start_on)).strftime('%Y-%m-%d')
            period_end_on = datetime.utcfromtimestamp(
                float(period_end_on)).strftime('%Y-%m-%d')
            exp_date = datetime.utcfromtimestamp(
                float(exp_date)).strftime('%Y-%m-%d')

            plans = ['BRONZE', 'GOLD', 'PLATINUM']
            cards = ['Visa', 'Mastercard', 'AMEX',
                     'J.C.B', "Diner's Club"]

            params = {
                'created_on': created_on,
                'updated_on': created_on,
                'user_id': user.id,
                'receipt_number': fake.md5(),
                'description': '{0} MONTHLY'.format(random.choice(plans)),
                'period_start_on': period_start_on,
                'period_end_on': period_end_on,
                'currency': 'usd',
                'tax': random.random() * 100,
                'tax_percent': random.random() * 10,
                'total': random.random() * 1000,
                'brand': random.choice(cards),
                'last4': str(random.randint(1000, 9000)),
                'exp_date': exp_date
            }

            data.append(params)

    return _bulk_insert(Invoice, data, 'invoices')


@add.command()
@with_appcontext
def bets():
    """
    Generate random bets.
    """
    data = []

    users = User.query.all()

    for user in users:
        for i in range(0, random.randint(10, 20)):
            fake_datetime = fake.date_time_between(
                start_date='-1y', end_date='now').strftime('%s')

            created_on = datetime.utcfromtimestamp(
                float(fake_datetime)).strftime('%Y-%m-%dT%H:%M:%S Z')

            wagered = random.randint(1, 100)
            die_1 = roll()
            die_2 = roll()
            outcome = die_1 + die_2

            random_percent = random.random()

            if random_percent >= 0.75:
                guess = outcome
            else:
                guess = random.randint(2, 12)

            payout = float(current_app.config['DICE_ROLL_PAYOUT'][str(guess)])
            is_winner = Bet.is_winner(guess, outcome)
            payout = Bet.determine_payout(payout, is_winner)
            net = Bet.calculate_net(wagered, payout, is_winner)

            params = {
                'created_on': created_on,
                'updated_on': created_on,
                'user_id': user.id,
                'guess': guess,
                'die_1': die_1,
                'die_2': die_1,
                'roll': outcome,
                'wagered': wagered,
                'payout': payout,
                'net': net
            }

            data.append(params)

    return _bulk_insert(Bet, data, 'bets')


@add.command()
@click.pass_context
@with_appcontext
def all(ctx):
    """
    Generate all data.

    :param ctx:
    :return: None
    """
    ctx.invoke(users)
    ctx.invoke(invoices)
    ctx.invoke(bets)

    return None
