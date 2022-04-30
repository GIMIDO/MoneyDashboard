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
    print(action)
    print(old_action)
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


def search_actions(wallet_pk, q_from, q_to, q_category, q_user):
    if q_category:
        actions_all = Action.objects.filter(category=q_category, wallet=wallet_pk)
    else:
        actions_all = Action.objects.filter(wallet=wallet_pk)

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
