# Notes

## 2023-06-27

### strings

Don't use mod for string formatting. Use f-strings or `.format()` if using
older versions of python

### context managers

The `with` keyword is your best friend. Use it as much as possible

### passwords

Why is the length of the password capped?

Why are you not using a salt?

### Exceptions

If you are raising exceptions from errors, use the `from` statement:

```python
try:
  function_call()
except library.Error as e:
  raise Exception('lorem ipsum...') from e
```

### sql

Use sql prepared statements

Not sure if it's relevant yet, but use transactions where applicable

### config

Use a proper config format like yaml/toml/etc

### server setup

Don't use ufw unless you're already super familiar with it. Just use iptables.
It's part of the linux kernel and you're not getting away from it. Don't learn
the narrow abstraction if the underlying technology is there (and honestly
simpler imo)

Turn this into an ansible script (or bash at the very least)

### weird stuff

database.py is weird. Either make it a module or don't. Currently you're
calling the `get_connection` function from different files, but assigning it to
the label in the same module the function is from. You also call it twice so
not sure what's up with that?

The inconsistency when using `import`. Either put it all on the same line, or
use separate statements.
