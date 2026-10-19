#!/usr/bin/env python
import argparse
import os
from pathlib import Path
from typing import overload

# consts
_TRUTHY_VALS = frozenset({'y', 'yes', '1', 'true', 't', 'on'})
# anything else will be considered false...

# helpers
def _normalize(value: str) -> str:
	return value.strip().lower()

def _fmtpct(value: str) -> str:
	return value.replace("%", "%%")

class Env:
	# setters
	@staticmethod
	def put_value(key: str, value: str) -> None:
		os.environ[key] = value

	# getters
	@staticmethod
	def has_value(key: str) -> bool:
		return key in os.environ

	# if is missing, set a default. or don't.
	# set but empty counts as unset, like shell ${FOO:-default}
	@overload
	@staticmethod
	def get_value(key: str) -> str | None: ...

	@overload
	@staticmethod
	def get_value(key: str, default: str) -> str: ...

	@staticmethod
	def get_value(key: str, default: str | None = None) -> str | None:
		return os.environ.get(key) or default

	# useful for cli tool invocations
	@staticmethod
	def get_bool(key: str, default: bool = False) -> bool:
		# set but empty counts as unset, like shell ${FOO:-default}
		if not (value := _normalize(os.environ.get(key, ''))):
			return default

		return value in _TRUTHY_VALS

	# ~ expands, a relative path is taken from base (when given)
	@staticmethod
	def get_path(key: str, base: Path | None = None) -> Path | None:
		if not (value := os.environ.get(key)):
			return None

		path = Path(value).expanduser()
		return base / path if base else path

	# copy of the current envir, extras override. for child processes
	@staticmethod
	def get_envir(extra: dict[str, str] | None = None) -> dict[str, str]:
		return os.environ | (extra or {})

	# lets say the child process now modified the envir...
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
# print(Env.get_bool("DUMMYKV"))

# precedence is: cli flags, envir, default.

_env_parser = argparse.ArgumentParser()

# flag backed by an envir key. the help gets the env key and resolved default appended
# a bool default makes it an on switch (store_true)
def _env_arg(flag: str, key: str, default: str | bool, help: str, **kwargs) -> None:
	if isinstance(default, bool):
		value = Env.get_bool(key, default)
		kwargs.setdefault("action", "store_true")
	else:
		value = Env.get_value(key, default)

	# argparse %-formats help, so a literal % must be doubled
	shown = _fmtpct(str(value))
	_env_parser.add_argument(flag, default=value, help=f"{help} (env: {key}, default: {shown})", **kwargs)


_env_arg("--verbose", "VERBOSE", False, "Verbose output")
_env_arg("--port", "PORT", "8080", "Port to listen on", type=int)
_env_arg("--force", "FORCE", "100%", "Force to apply")

if __name__ == "__main__":
	args = _env_parser.parse_args()
