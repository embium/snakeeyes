import datetime
from collections import OrderedDict

import pytz
from flask import current_app
from sqlalchemy import or_, text
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin

from itsdangerous import URLSafeTimedSerializer

from lib.security import sign_token, verify_token
from lib.util_sqlalchemy import ResourceMixin, AwareDateTime
from snakeeyes.blueprints.billing.models.credit_card import CreditCard
from snakeeyes.blueprints.billing.models.subscription import Subscription
from snakeeyes.blueprints.billing.models.invoice import Invoice
from snakeeyes.blueprints.bet.models.bet import Bet
from snakeeyes.extensions import db


class User(UserMixin, ResourceMixin, db.Model):
    ROLE = OrderedDict([
        ('member', 'Member'),
        ('admin', 'Admin')
    ])

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # Relationships.
    credit_card = db.relationship(CreditCard, uselist=False,
                                  backref='credit_card',
                                  passive_deletes=True)
    subscription = db.relationship(Subscription, uselist=False,
                                   backref='subscription',
                                   passive_deletes=True)
    invoices = db.relationship(Invoice, backref='invoices',
                               passive_deletes=True)
    bets = db.relationship(Bet, backref='bets', passive_deletes=True)

    # Authentication.
    role = db.Column(db.Enum(*ROLE, name='role_types', native_enum=False),
                     index=True, nullable=False, server_default='member')
    active = db.Column('is_active', db.Boolean(), nullable=False,
                       server_default='1')
    username = db.Column(db.String(24), unique=True, index=True)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False,
                      server_default='')
    password = db.Column(db.String(128), nullable=False, server_default='')

    # Billing.
    name = db.Column(db.String(128), index=True)
    payment_id = db.Column(db.String(128), index=True)
    cancelled_subscription_on = db.Column(AwareDateTime())
    previous_plan = db.Column(db.String(128))

    # Bet.
    coins = db.Column(db.BigInteger())
    last_bet_on = db.Column(AwareDateTime())

    # Activity tracking.
    sign_in_count = db.Column(db.Integer, nullable=False, default=0)
    current_sign_in_on = db.Column(AwareDateTime())
    current_sign_in_ip = db.Column(db.String(45))
    last_sign_in_on = db.Column(AwareDateTime())
    last_sign_in_ip = db.Column(db.String(45))

    # Additional settings.
    locale = db.Column(db.String(5), nullable=False, server_default='en')

    def __init__(self, **kwargs):
        # Call Flask-SQLAlchemy's constructor.
        super(User, self).__init__(**kwargs)

        self.password = User.encrypt_password(kwargs.get('password', ''))
        self.coins = 100

    @classmethod
    def find_by_identity(cls, identity):
        """
        Find a user by their e-mail or username.

        :param identity: Email or username
        :type identity: str
        :return: User instance
        """
        return User.query.filter(
          (User.email == identity) | (User.username == identity)).first()

    @classmethod
    def find_by_token(cls, token, ex=3600):
        """
        Obtain a user by looking up their email contained in a token.

        :param token: Signed token.
        :type token: str
        :param expiration: Seconds until it expires, defaults to 1 hour
        :type expiration: int
        :return: User instance or None
        """
        email = verify_token(token, ex)

        if email is None:
            return None

        return User.find_by_identity(email)

    @classmethod
    def encrypt_password(cls, plaintext_password):
        """
        Hash a plaintext string using PBKDF2. This is good enough according
        to the NIST (National Institute of Standards and Technology).

        In other words while bcrypt might be superior in practice, if you use
        PBKDF2 properly (which we are), then your passwords are safe.

        :param plaintext_password: Password in plain text
        :type plaintext_password: str
        :return: str
        """
        if plaintext_password:
            return generate_password_hash(plaintext_password)

        return None

    @classmethod
    def initialize_password_reset(cls, identity):
        """
        Generate a token to reset the password for a specific user.

        :param identity: User e-mail address or username
        :type identity: str
        :return: User instance
        """
        u = User.find_by_identity(identity)
        reset_token = sign_token(u.email)

        # This prevents circular imports.
        from snakeeyes.blueprints.user.tasks import (
            deliver_password_reset_email)
        deliver_password_reset_email.delay(u.id, reset_token)

        return u

    @classmethod
    def search(cls, query):
        """
        Search a resource by 1 or more fields.

        :param query: Search query
        :type query: str
        :return: SQLAlchemy filter
        """
        if query == '':
            return text('')

        search_query = '%{0}%'.format(query)
        search_chain = (User.email.ilike(search_query),
                        User.username.ilike(search_query))

        return or_(*search_chain)

    @classmethod
    def is_last_admin(cls, user, new_role, new_active):
        """
        Determine whether or not this user is the last admin account.

        :param user: User being tested
        :type user: User
        :param new_role: New role being set
        :type new_role: str
        :param new_active: New active status being set
        :type new_active: bool
        :return: bool
        """
        is_demoting_admin = user.role == 'admin' and new_role != 'admin'
        is_changing_active = user.active is True and new_active is None
        admin_count = User.query.filter(User.role == 'admin').count()

        if is_demoting_admin and admin_count == 1:
            return True

        if is_changing_active and user.role == 'admin' and admin_count == 1:
            return True

        return False

    @classmethod
    def bulk_delete(cls, ids):
        """
        Override the general bulk_delete method because we need to delete them
        one at a time while also deleting them on Stripe.

        :param ids: List of ids to be deleted
        :type ids: list
        :return: int
        """
        delete_count = 0

        for id in ids:
            user = User.query.get(id)

            if user is None:
                continue

            if user.payment_id is None:
                user.delete()
            else:
                subscription = Subscription()
                cancelled = subscription.cancel(user=user)

                # If successful, delete it locally.
                if cancelled:
                    user.delete()

            delete_count += 1

        return delete_count

    def is_active(self):
        """
        Return whether or not the user account is active, this satisfies
        Flask-Login by overwriting the default value.

        :return: bool
        """
        return self.active

    def authenticated(self, with_password=True, password=''):
        """
        Ensure a user is authenticated, and optionally check their password.

        :param with_password: Optionally check their password
        :type with_password: bool
        :param password: Optionally verify this as their password
        :type password: str
        :return: bool
        """
        if with_password:
            return check_password_hash(self.password, password)

        return True

    def serialize_token(self, expiration=3600):
        """
        Sign and create a token that can be used for things such as resetting
        a password or other tasks that involve a one off token.

        :param expiration: Seconds until it expires, defaults to 1 hour
        :type expiration: int
        :return: JSON
        """
        private_key = current_app.config['SECRET_KEY']

        serializer = URLSafeTimedSerializer(private_key, expiration)
        return serializer.dumps({'user_email': self.email}).decode('utf-8')

    def update_activity_tracking(self, ip_address):
        """
        Update various fields on the user that's related to meta data on their
        account, such as the sign in count and ip address, etc..

        :param ip_address: IP address
        :type ip_address: str
        :return: SQLAlchemy commit results
        """
        self.sign_in_count += 1

        self.last_sign_in_on = self.current_sign_in_on
        self.last_sign_in_ip = self.current_sign_in_ip

        self.current_sign_in_on = datetime.datetime.now(pytz.utc)
        self.current_sign_in_ip = ip_address

        return self.save()

    def add_coins(self, plan):
        """
        Add an amount of coins to an existing user.

        :param plan: Subscription plan
        :type plan: str
        :return: SQLAlchemy commit results
        """
        self.coins += plan['metadata']['coins']

        return self.save()