from pymongo.collection import Collection
from backend.apis import convert_currency_to_cop
from backend.command import Invoker, ValidateAccount, GetAccountBalance, WithdrawInDollars, DepositMoney, WithdrawInCop
from backend.constants import (
    USD,
    OPERATORS,
    WITHDRAW_IN_DOLLARS,
    WITHDRAW_IN_COP,
    VALIDATE_ACCOUNT,
    DEPOSIT_MONEY,
    GET_ACCOUNT_BALANCE
)
from backend.utils import green, cyan, orange
from backend.validators import validate_attrs, account_exists, raise_exception


class Account(object):
    user_id: str
    pin: int
    balance: int
    collection: Collection
    deposit: int
    money: int
    is_valid: bool
    queryMongo = {}

    def __init__(self, user_id: str, pin: int, collection: Collection):
        self.user_id = user_id
        self.pin = pin
        self.collection = collection
        self.is_valid = self.validate_account()
        self.queryMongo = {
            'user_id': self.user_id,
            'pin': self.pin
        }
        self.set_balance()

    def set_balance(self):
        self.balance = round(self.get_account_balance(), 2)

    def get_account(self):
        return self.collection.find_one(self.queryMongo)

    def validate_account(self):
        return self.get_account() is not None

    def get_account_balance(self):
        return self.get_account().get('balance')

    def withdraw_in_dollars(self):
        min_usd = convert_currency_to_cop(USD)
        value = round(self.money * min_usd, 2)
        print(cyan(f'${self.money} USD == ${value} COP'))
        self.money = self.get_account_balance() - value
        self.update_db_balance()


    def withdraw_in_cop(self):
        money = self.money
        self.money = round(self.get_account_balance() - money, 2)
        self.update_db_balance()

    def deposit_money(self):
        self.money = round(self.money + self.get_account_balance(), 2)
        self.update_db_balance()

    def update_db_balance(self):
        self.collection.update_one(self.queryMongo, {
            '$set': {
                'balance': self.money
            }
        })
        self.money = 0
        self.set_balance()

    def set_property(self, prop, value):
        self.__dict__[prop] = value


def run_step(step, steps, controller, commands, account):
    action = step.get('action')
    command = commands.get(action)
    account_dict = account.__dict__
    params = step.get('params')
    step_id = step.get('id')
    print(green(f'account object ---- {account_dict}'), flush=True)
    if 'money' in params.keys():
        value = params.get('money').get('value')
        account.set_property('money', value)

    if action in commands.keys():
        print(orange(f'Running Step ---> {step_id}'), flush=True)
        controller.apply_command(command)

    for transition in step.get('transitions'):
        print(cyan(transition), flush=True)
        can_jump = False
        target_step = transition.get('target')
        for condition in transition.get('condition', []):

            operator = condition.get('operator')
            field_id = condition.get('field_id')
            expected_vale = condition.get('value')

            if operator in OPERATORS:
                field_obj = account_dict.get(field_id)
                if operator == 'eq':
                    can_jump = field_obj == expected_vale
                elif operator == 'lt':
                    can_jump = field_obj < expected_vale
                elif operator == 'gt':
                    can_jump = field_obj > expected_vale
                elif operator == 'lte':
                    can_jump = field_obj <= expected_vale
                elif operator == 'gte':
                    can_jump = field_obj >= expected_vale

                if not can_jump:
                    raise Exception(f'Invalid condition -> account {field_id} {field_obj} {operator} {expected_vale} == False')
            else:
                raise Exception(f'Invalid Operator {account_dict[field_id]}')

        if target_step:
            step = steps.get(target_step)
            run_step(step, steps, controller, commands, account)


def launch_transactions_set(trigger, steps, collection):
    params_trigger = trigger.get('params')
    user_id = params_trigger.get('user_id')
    pin = params_trigger.get('pin')

    if not account_exists(user_id, pin, collection):
        raise_exception('Account Doesnt Exists')

    account = Account(
        user_id=user_id,
        pin=pin,
        collection=collection
    )

    controller = Invoker(account)

    actions = {
        VALIDATE_ACCOUNT: ValidateAccount(),
        GET_ACCOUNT_BALANCE: GetAccountBalance(),
        WITHDRAW_IN_DOLLARS: WithdrawInDollars(),
        DEPOSIT_MONEY: DepositMoney(),
        WITHDRAW_IN_COP: WithdrawInCop()
    }

    sequences = {
        trigger.get('id'): {
            'id': trigger.get('id'),
            'transitions': trigger.get('transitions'),
            'params': params_trigger
        }
    }

    for step in steps:
        step_id = step.get('id')
        sequences[step_id] = step

    for _, sequence in sequences.items():
        if not 'action' in sequence.keys():
            continue
        for paramName, param in sequence.get('params').items():
            parent_id = param.get('from_id')
            if parent_id is not None:
                parent = sequences[parent_id].get('params')
                sequence['params'][paramName] = parent.get(paramName)

    result = None, None
    for _, sequence in sequences.items():
        if 'action' not in sequence.keys():
            for transition in sequence.get('transitions', []):
                target_step = transition.get('target')
                step = sequences.get(target_step)
                result = run_step(step, sequences, controller, actions, account)
    return result


def start_transaction(collection, data):
    trigger = data.pop('trigger', None)
    steps = data.pop('steps', [])

    validation_result = validate_attrs(trigger, steps)

    if validation_result[0] is False:
        return validation_result

    launch_transactions_set(trigger, steps, collection)