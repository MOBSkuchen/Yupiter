# Yupiter - Easily write MASM

## What is this?

Yupiter is a high level Programming Language that compiles to MASM32
***
## Installation (*Incomplete*)
First, you have to have MASM32 installed, it can be installed from

[HERE](https://www.masm32.com/)
   or    [HERE (Direct download)](http://masm32.masmcode.com/masm32/masm32v11r.zip)

*Further steps are not available yet.*

***
## Basic Syntax
### Imports
Import work using the import keyword and the name of the library.
````
import stdlib
````

The outputted assembly will be \masm32\modules\ **LIB**.inc

Additionally, you can import MASM32 libraries by adding a question mark.
By also adding an exclamation mark, you can import a .lib file.
````
import ?kernel32   # .inc file import (\masm32\include\kernel32.inc)
import ?!kernel32  # .lib file import (\masm32\includelib\kernel32.lib)
````

### Variables
A variable is defined using **name = value**,
they do not require types.
````
str = "Hello World"
int = 100
````
Variables are assigned a unique name upon definition (v_**NUM**).

When they are redefined, another variable with a different name
is registered and the value of the previous variable is set to **NULL**
### Basic Functions

A function is defined using the def keyword,
which is then followed by the name and arguments.
A function is closed with a semicolon.

Functions **require** a return statement

````
def function(a, b)
   return a + b
;
````

Like variables, functions are also assigned another name (F_**NUM**).

The returned value is evaluated and then moved in the *eax* register.
If another variable is assigned to the value of a function,
*eax* will be moved in the register of the variable.

*eax* is not cleared after that.

### If statements

An if statement is implemented like this:

````
if int > 10
    print("Greater than")
;
````

**else** and **else if** are used like this:

````
elif int == 10
    print("Eqaul")
;
else
    print("Less than")
;
````

Every statement is closed using a semicolon

## Problems

Yupiter is still very early in development and a lot of things still have to be implemented.

Some of these things are:
- If statements
- While loops
- For loops
- File imports
- Improved garbage collection

I also plan on adding NASM as a compiler target.