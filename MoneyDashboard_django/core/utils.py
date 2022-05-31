from .models import *
from django.db.models import Q


def calc_amount_wallet(a_type, action, pk):

    w_amount = Wallet.objects.get(pk=pk)

    match(a_type):
        case 'create':
            if action.action_type == "increase":
                w_amount.start_amount += float(action.money)
            else:
                w_amount.start_amount -= float(action.money)
        case 'delete':
            if action.action_type == "increase":
                w_amount.start_amount -= float(action.money)
            else:
                w_amount.start_amount += float(action.money)

    w_amount.save()


def calc_amount_wallet_update(action, pk, old_action):

    w_amount = Wallet.objects.get(pk=pk)

    if old_action.action_type == 'increase':
        w_amount.start_amount -= float(old_action.money)

        if action.action_type == 'increase': 
            w_amount.start_amount += float(action.money)
        else:
            w_amount.start_amount -= float(action.money)

    else:
        w_amount.start_amount += float(old_action.money)

        if action.action_type == 'increase': 
            w_amount.start_amount += float(action.money)
        else:
            w_amount.start_amount -= float(action.money)

    w_amount.save()


def calc_amount(actions):

    total_amount = 0

    for action in actions:

        if action.action_type == "increase":
            total_amount = total_amount + action.money
        else:
            total_amount -= action.money

    return total_amount


def search_actions(wallet_pk, q_from, q_to, q_category, q_type):

    if q_category:
        actions_c = Action.objects.filter(
            category=q_category,
            wallet=wallet_pk
        ).order_by('-date', '-created_at')
    else:
        actions_c = Action.objects.filter(
            wallet=wallet_pk
        ).order_by('-date', '-created_at')

    if q_type:
        actions_all = actions_c.filter(action_type=q_type)
    else:
        actions_all = actions_c

    if q_from:

        if q_to:    
            actions = actions_all.filter(
                Q(date__gte=q_from,date__lte=q_to))
        else:
            actions = actions_all.filter(
                Q(date__gte=q_from))

    else:

        if q_to:
            actions = actions_all.filter(
                    Q(date__lte=q_to))
        else:
            actions = actions_all

    return actions


def get_next_link(request):

    if request.GET.get('next'):
        return request.GET.get('next')
    else:
        return '/'


def transfer_money(wallet_from, wallet_to, money):

    wallet_from.start_amount -= money
    wallet_from.save()
    wallet_to.start_amount += money
    wallet_to.save()

def objective_transfer_money(objective, wallet, money):

    wallet.start_amount -= money
    wallet.save()
    objective.now_amount += money
    objective.save()


def total_graph(actions, categories):

    total_amount_graph = []

    for category in categories:
        filtered = actions.filter(category=category.id)
        total_amount = 0
        increase = 0
        spending = 0

        for action in filtered:

            if action.action_type == "increase":
                total_amount += action.money
                increase += action.money
            else:
                total_amount -= action.money
                spending += action.money

        item = {
            'title': category.title,
            'total': total_amount,
            'increase': increase,
            'spending': spending,
            'category_id': category.pk,
            'category_color': category.color
        }

        total_amount_graph.append(item)

    return total_amount_graph
    