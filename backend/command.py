import time
from abc import ABC, abstractmethod

from backend.utils import green, cyan, red


class Command(ABC):

	@abstractmethod
	def execute(self, receptor):
		pass

class Invoker(object):

	receiver = None

	def __init__(self, receiver):
		self.receiver = receiver

	def apply_command(self, command):
		time.sleep(3)
		command.execute(self.receiver)


class ValidateAccount(Command):
	def execute(self, account):
		print(green('running validate_account command'), flush=True)
		if account.validate_account():
			print(green('running validate_account command'), flush=True)
		else:
			print(red('Invalid Account'), flush=True)
		print(cyan('Account Valid'), flush=True)
		print('**********', flush=True)


class GetAccountBalance(Command):
	def execute(self, account):
		print(green(f'running get_account_balance command '), flush=True)
		account.get_account_balance()
		print('**********', flush=True)


class WithdrawInDollars(Command):
	def execute(self, account):
		print(green(f'running withdraw_in_dollars command ${account.money}'), flush=True)
		account.withdraw_in_dollars()
		print('**********', flush=True)


class DepositMoney(Command):
	def execute(self, account):
		print(green('running deposit_money command'), flush=True)
		account.deposit_money()
		print('**********', flush=True)


class WithdrawInCop(Command):
	def execute(self, account):
		print(green('running withdraw_in_cop command'), flush=True)
		account.withdraw_in_cop()
		print('**********', flush=True)

