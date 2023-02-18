# Yupiter
Yupiter is a high-level compiled programming language,
which compiles to 32/64 bit NASM


# Getting started
Clone this repository and create a script (``main.yp`` for example).
The file name has to end with ``.yp``.

Compile with ``python main.py main.yp``.


# Synatx
NOTE: Yupiter is NOT finished.


## Variables

Create a variable with
```
age = 11
name = "Jack"

age =  age + 3  # Increase the age, lol
```

First comes the name, then an EQ operator and lastly the value.
Operations can only be made between the same types.
Type-definitions are not neccessary.
By the way: Comments are created with hashtags.


# Compiler options

- ``-v`` / ``-view`` : Views the input file with syntax highlihting
