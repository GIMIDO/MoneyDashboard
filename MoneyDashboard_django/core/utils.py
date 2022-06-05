from .models import *
from django.db.models import Q
import decimal


def calc_amount_wallet(a_type, action, pk):
    """The function of calculating the funds in the wallet after the action "create" or "delete" """
    
    w_amount = Wallet.objects.get(pk=pk)

    match(a_type):
        case 'create':
            if action.action_type == "increase":
                w_amount.start_amount = decimal.Decimal(w_amount.start_amount) + decimal.Decimal(action.money)
            else:
                w_amount.start_amount = decimal.Decimal(w_amount.start_amount) - decimal.Decimal(action.money)
        case 'delete':
            if action.action_type == "increase":
                w_amount.start_amount = decimal.Decimal(w_amount.start_amount) - decimal.Decimal(action.money)
            else:
                w_amount.start_amount = decimal.Decimal(w_amount.start_amount) + decimal.Decimal(action.money)

    w_amount.save()


def calc_amount_wallet_update(action, pk, old_action):
    """The function of calculating the funds in the wallet after the action "update" """

    w_amount = Wallet.objects.get(pk=pk)

    if old_action.action_type == 'increase':
        w_amount.start_amount = decimal.Decimal(w_amount.start_amount) - decimal.Decimal(old_action.money)
        if action.action_type == 'increase': 
            w_amount.start_amount = decimal.Decimal(w_amount.start_amount) + decimal.Decimal(action.money)
        else:
            w_amount.start_amount = decimal.Decimal(w_amount.start_amount) - decimal.Decimal(action.money)

    else:
        w_amount.start_amount = decimal.Decimal(w_amount.start_amount) + decimal.Decimal(old_action.money)
        if action.action_type == 'increase': 
            w_amount.start_amount = decimal.Decimal(w_amount.start_amount) + decimal.Decimal(action.money)
        else:
            w_amount.start_amount = decimal.Decimal(w_amount.start_amount) - decimal.Decimal(action.money)

    w_amount.save()


def calc_amount(actions):
    """Calculate the total amount of found actions on the search page"""

    total_amount = 0

    for action in actions:
        if action.action_type == "increase":
            total_amount = decimal.Decimal(total_amount) + decimal.Decimal(action.money)
        else:
            total_amount = decimal.Decimal(total_amount) - decimal.Decimal(action.money)

    return total_amount


def search_actions(wallet_pk, q_from, q_to, q_category, q_type):
    """The function of search action"""

    if q_category:
        actions_c = Action.objects.filter(category=q_category,wallet=wallet_pk).order_by('-date', '-created_at')
    else:
        actions_c = Action.objects.filter(wallet=wallet_pk).order_by('-date', '-created_at')

    if q_type:
        actions_all = actions_c.filter(action_type=q_type)
    else:
        actions_all = actions_c

    if q_from:
        if q_to:    
            actions = actions_all.filter(Q(date__gte=q_from,date__lte=q_to))
        else:
            actions = actions_all.filter(Q(date__gte=q_from))
    else:
        if q_to:
            actions = actions_all.filter(Q(date__lte=q_to))
        else:
            actions = actions_all
    return actions


def get_next_link(request):
    """The function of get link to go "next" link"""

    if request.GET.get('next'):
        return request.GET.get('next')
    else:
        return '/'


def transfer_money(wallet_from, wallet_to, money, user):
    """The function of transferring funds between wallets"""

    wallet_from.start_amount = decimal.Decimal(wallet_from.start_amount) - decimal.Decimal(money)
    wallet_from.save()
    wallet_to.start_amount = decimal.Decimal(wallet_to.start_amount) + decimal.Decimal(money)
    wallet_to.save()
    
    log_write('0', "create", "transfer", str('from ' + wallet_from.title + ' to ' + wallet_to.title + ' ' + str(money)), user)


def objective_transfer_money(objective, wallet, money, user):
    """The function of transferring funds from the wallet to the objective"""

    wallet.start_amount = decimal.Decimal(wallet.start_amount) - decimal.Decimal(money)
    wallet.save()
    objective.now_amount = decimal.Decimal(objective.now_amount) + decimal.Decimal(money)
    objective.save()
    
    log_write('0', "create", "transfer", str('from ' + wallet.title + ' to ' + objective.title + ' ' + str(money)), user)


def total_graph(actions, categories):
    """Data calculation function for displaying them in the "Graphics" block"""

    total_amount_graph = []

    for category in categories:
        filtered = actions.filter(category=category.id)
        total_amount = 0
        increase = 0
        spending = 0
        for action in filtered:
            if action.action_type == "increase":
                total_amount = decimal.Decimal(total_amount) + decimal.Decimal(action.money)
                increase = decimal.Decimal(increase) + decimal.Decimal(action.money)
            else:
                total_amount = decimal.Decimal(total_amount) - decimal.Decimal(action.money)
                spending = decimal.Decimal(spending) + decimal.Decimal(action.money)
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
    

def log_write(wallet_pk, a_type, model, text, user):
    """Logging function"""

    if wallet_pk == '0':
        log_message = LogTable.objects.create(
            user = user,
            a_type = a_type,
            message = '{}d {} "{}"'.format(a_type, model, text)
        )
        log_message.save()

    else:
        log_message = LogTable.objects.create(
            user = Wallet.objects.get(pk=wallet_pk).user,
            a_type = a_type,
            message = '{}d {} "{}"'.format(a_type, model, text)
        )
        log_message.save()