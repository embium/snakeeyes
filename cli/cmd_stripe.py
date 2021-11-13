import click

from flask import current_app
from flask.cli import with_appcontext

from snakeeyes.blueprints.billing.gateways.stripecom import Plan as PaymentPlan


@click.group()
def stripe():
    """ Perform various tasks with Stripe's API. """
    pass


@stripe.command()
@with_appcontext
def sync_plans():
    """
    Sync (upsert) STRIPE_PLANS to Stripe.

    :return: None
    """
    if current_app.config['STRIPE_PLANS'] is None:
        return None

    for _, value in current_app.config['STRIPE_PLANS'].items():
        plan = PaymentPlan.retrieve(value.get('id'))

        if plan:
            PaymentPlan.update(id=value.get('id'),
                               name=value.get('name'),
                               metadata=value.get('metadata'),
                               statement_descriptor=value.get(
                                   'statement_descriptor'))
        else:
            PaymentPlan.create(**value)

    return None


@stripe.command()
@click.argument('plan_ids', nargs=-1)
@with_appcontext
def delete_plans(plan_ids):
    """
    Delete 1 or more plans from Stripe.

    :return: None
    """
    for plan_id in plan_ids:
        PaymentPlan.delete(plan_id)

    return None


@stripe.command()
@with_appcontext
def list_plans():
    """
    List all existing plans on Stripe.

    :return: Stripe plans
    """
    return click.echo(PaymentPlan.list())
