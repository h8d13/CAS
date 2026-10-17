#!/usr/bin/env python
import os

# consts
_TRUTHY_VALS=["y", "yes", "1", "true", "t", "on"]
# anything else will be considered false...

# helpers
def _normalize(value: str) -> str:
	return value.strip().lower()

class Env:
	# setters
	@staticmethod
	def put_value(key: str, value: str) -> None:
		os.environ[key] = value
		# print(f"k = {key} v = {value}")

	@staticmethod
	def del_value(key: str) -> None:
		os.environ.pop(key)

	# getters
	@staticmethod
	def has_value(key: str) -> bool:
		return key in os.environ

	# if is missing, set a default. or don't.
	@staticmethod
	def get_value(key: str, default: str | None = None) -> str | None:
		value = os.environ.get(key, default)
		# print(f"k = {key}, d = {default}, v = {value}")
		return value

	# useful for cli tool invocations
	@staticmethod
	def get_bool(key: str, default: bool = False) -> bool:
		value = os.environ.get(key)

		if value is None:
			return default

		return _normalize(value) in _TRUTHY_VALS

	# misc
	# this is not thread safe. inherits from the python process
	# should be used only as such, for the current process envir
	@staticmethod
	def rel_envir():
		return os.reload_environ()

# Env.put_value("DUMMYKV", "0") # (1) False
# print(Env.has_value("DUMMYKV")) # (2) True
# print(Env.get_value("DUMMYKV")) # (3) returns 0, None
# print(Env.get_bool("DUMMYKV")) # (4) False 0, flip (1) to any _TRUTHY and would show True
# Env.del_value("DUMMYKV") # (5) Reset
# print(Env.get_value("DUMMYKV", "1")) # (6) returns 1, because we set a default.
# Env.put_value("DUMMYKV", "1") # (7) True
# Env.rel_envir()
# print(Env.get_bool("DUMMYKV"))
