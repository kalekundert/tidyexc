*******
TidyExc
*******

.. image:: https://img.shields.io/pypi/v/tidyexc.svg
   :alt: Last release
   :target: https://pypi.python.org/pypi/tidyexc

.. image:: https://img.shields.io/pypi/pyversions/tidyexc.svg
   :alt: Python version
   :target: https://pypi.python.org/pypi/tidyexc

.. image:: https://img.shields.io/readthedocs/tidyexc.svg
   :alt: Documentation
   :target: https://tidyexc.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/github/workflow/status/kalekundert/tidyexc/Test%20and%20release/master
   :alt: Test status
   :target: https://github.com/kalekundert/tidyexc/actions

.. image:: https://img.shields.io/coveralls/kalekundert/tidyexc.svg
   :alt: Test coverage
   :target: https://coveralls.io/github/kalekundert/tidyexc?branch=master

.. image:: https://img.shields.io/github/last-commit/kalekundert/tidyexc?logo=github
   :alt: Last commit
   :target: https://github.com/kalekundert/tidyexc

TidyExc provides an exception base class that makes it easy to raise rich, 
helpful exceptions:

- *Rich*: Instead of simply storing an error message, TidyExc exceptions 
  separately store parameters and message templates.  This separation makes it 
  easier for exception handling code to access information describing the error 
  and to respond accordingly.

- *Helpful*: TidyExc is inspired by the error message conventions promoted by 
  the `tidyverse style guide`__.  Briefly, these conventions state that an 
  error message should consist of a brief statement of the problem, followed by 
  a bullet-point list of relevant contextual information.  The bullet-point 
  format makes it easy to include lots of detail, without the detail becoming 
  overwhelming.

__ https://style.tidyverse.org/error-messages.html

The following example shows TidyExc in action::

  >>> from tidyexc import Error
  >>> class CheeseShopError(Error):
  ...     pass
  ...
  >>> err = CheeseShopError(
  ...         product_name="Red Leicester",
  ...         num_requested=1,
  ...         num_available=0,
  ... )
  >>> err.brief = "insufficient inventory to process request"
  >>> err.info += "{num_requested} {product_name} requested"
  >>> err.blame += "{num_available} available"
  >>> raise err
  Traceback (most recent call last):
    ...
  CheeseShopError: insufficient inventory to process request
  • 1 Red Leicester requested
  ✖ 0 available

