***********
Basic Usage
***********

Installation
============
Install TidyExc using ``pip``:

.. code-block:: console

  $ pip install tidyexc

- Requires python≥3.6
- Obeys `semantic versioning`_.

Defining exceptions
===================
TidyExc exceptions inherit from ``tidyexc.Error`` and are typically empty:

.. code-block::

  >>> from tidyexc import Error
  >>> class MyError(Error):
  ...     pass

While it's possible to use the `Error` class directly, it's good practice to 
define a custom exception type for your library.  This makes it possible to 
distinguish between exceptions from different libraries.

How many exception classes to define for your library is a matter of taste.  I 
prefer to define one for each kind of user that might be expected to fix the 
problem causing the exception.  For example, this might include:

- *UsageError*: For faulty input that the end-user would need to fix.
- *ApiError*: For programming mistakes that a developer would need to fix.

Raising exceptions
==================
There are three steps to raising a TidyExc exception:

- Provide any parameters relevant to diagnosing and fixing the problem.

- Provide message templates that format and describe the above parameters.

- Raise the exception.

It's important that the parameters and the message templates are provided 
separately.  This allows downstream exception handlers to access every 
parameter relevant to the exception when attempting to formulate a response.
For example, one common way to handle an exception is to raise another 
exception with a more context-specific message (e.g. "missing configuration" 
instead of "file not found").  This is much easier if the parameters of the 
original exception (e.g. the file name) can be accessed directly, rather than 
needing to be `parsed from its error message`__.

__ https://stackoverflow.com/questions/27779375/get-better-parse-error-message-from-elementtree

Parameters are typically provided as keyword arguments to the exception 
constructor, although they can also be added to the `Error.data` attribute 
after the fact:

.. code-block:: pycon

  >>> err = MyError(a=1)
  >>> err.data.b = 2
  >>> err.data.a, err.data.b
  (1, 2)

There are four different kinds of message templates that can be provided, all 
optional:

- `brief <Error.brief>`: For a brief statement of the problem.
- `info <Error.info>`: For descriptions of the context in which the error 
  occurred.
- `blame <Error.blame>`: For descriptions of the specific cause of the error.
- `hints <Error.hints>`: For suggestions on how to fix the error.

Each of these message templates can either be a string or a callable.  If a 
string, the `str.format` method will be used to do parameter substitution.  If 
a callable, the parameters will be provided as an argument and the return value 
will be used as the ultimate message.  See the `API documentation <info>` for 
more detail on how these templates are interpreted.

The `brief` message can be specified as an argument to the constructor, but all 
the other messages must be specified after the exception object has been 
created.  Note that `brief` is specified using the assignment operator while 
`info`, `blame`, and `hints` are specified using the in-place addition 
operator.  This is because there can only be one `brief` message, but any 
number of the others:

.. code-block:: pycon

  >>> err.brief = "a problem occured"
  >>> err.info += "some relevant context: {a}"
  >>> err.blame += "something unexpected: {b}"
  >>> err.hints += "try this instead"

Once the exception object contains all of the relevant information, it can be 
raised as usual:

.. code-block:: pycon

  >>> raise err
  Traceback (most recent call last):
    ...
  MyError: a problem occured
  • some relevant context: 1
  ✖ something unexpected: 2
  • try this instead

.. _`semantic versioning`: https://semver.org/
.. _`tidyverse style guide`: https://style.tidyverse.org/error-messages.html
