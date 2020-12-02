#!/usr/bin/env python3

import textwrap
from dotmap import DotMap
from shutil import get_terminal_size
from contextlib import contextmanager
from collections import ChainMap
from .utils import list_iadd, property_iadd, eval_template

_info_stack = []

class Error(Exception):
    """
    A base class for making exceptions that:

    - Provide direct access to any parameters that are relevant to the error.
    - Use bullet-points to clearly and comprehensively describe the error.

    Example:

    .. code-block:: pycon

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
        tidyexc.exc.CheeseShopError: insufficient inventory to process request
        • 1 Red Leicester requested
        ✖ 0 available
    """

    @classmethod
    @contextmanager
    def add_info(cls, message, **kwargs):
        """
        Add the given `info` to any exceptions derived from this class that are 
        instantiated inside a with-block.

        It is common for different exceptions raised by a single task to share 
        some context.  For example, many errors are possible when parsing a 
        file, but for most of them the file name and line number will be 
        relevant.  This function provides an easy way to include this context.

        Any exceptions that inherit from this class and are instantiated inside 
        a with-block using this context manager will have the given message 
        template as one of their `info` bullet points, and the given *kwargs* 
        merged with their `data`.  The data is merged such that later values 
        will override earlier values.  
        
        It is possible to nest any number of these context managers.  The 
        `info` bullet points will appear in the order the context managers were 
        invoked.  It is considered good practice for the message template to 
        only refer to parameters that are provided to the same context manager, 
        but all message templates do have access to all parameters, regardless 
        of when they were specified.

        Example:

        .. code-block:: pycon

            >>> from tidyexc import Error
            >>> with Error.add_info('a: {a}', a=1):
            ...     raise Error()
            ...
            Traceback (most recent call last):
              ...
            tidyexc.exc.Error:
            • a: 1
        """
        try:
            cls.push_info(message, **kwargs)
            yield
        finally:
            cls.pop_info()

    @classmethod
    def push_info(cls, message, **kwargs):
        """
        Add the given `info` to any exceptions derived from this class that are 
        subsequently instantiated.

        See `add_info()` for more information.  This function is similar, 
        except that it is not a context manager.  That means that you must 
        manually call `pop_info()` or `clear_info()` after calling this 
        function.

        Example:

        .. code-block:: pycon

            >>> from tidyexc import Error
            >>> Error.push_info('a: {a}', a=1)
            >>> try:
            ...     raise Error()
            ... finally:
            ...     Error.pop_info()
            ...
            Traceback (most recent call last):
              ...
            tidyexc.exc.Error:
            • a: 1
        """

        _info_stack.append((cls, message, kwargs))

    @classmethod
    def pop_info(cls):
        """
        Stop adding the `info` that was most-recently "pushed" to exceptions 
        derived from this class.

        This is the opposite of `push_info()`.
        """
        for i, (cls_i, _, _) in reversed(list(enumerate(_info_stack))):
            if cls_i is cls:
                del _info_stack[i]
                return
        raise IndexError(f"no info to pop for {cls}")

    @classmethod
    def clear_info(cls):
        """
        Stop adding any `info` that was "pushed" to exceptions derived from 
        this class.
        """
        global _info_stack
        _info_stack = [x for x in _info_stack if x[0] is not cls]


    def __init__(self, brief="", **kwargs):
        """
        Create a new exception.

        You can specify a `brief` message template and any number of parameters 
        (via keyword arguments) when constructing an `Error` instance.  This 
        may be enough for simple exceptions, but most of the time you would 
        subsequently add `info` and `blame` message templates (which cannot be 
        directly specified in the constructor).
        
        Any class-wide parameters and/or message templates specified using 
        `add_info()` or `push_info()` are read and applied during the 
        constructor.  This means that these class-wide functions have no effect 
        on exceptions that have already been instantiated.

        Example:

        .. code-block:: pycon

            >>> raise Error("a: {a}", a=1)
            Traceback (most recent call last):
              ...
            tidyexc.exc.Error: a: 1

        """
        info_stack = [
                (msg, kwargs)
                for cls, msg, kwargs in _info_stack
                if isinstance(self, cls)
        ]
        info_messages, info_kwargs = \
                zip(*info_stack) if info_stack else ([], [])

        self._brief = brief
        self._info = list_iadd(info_messages)
        self._blame = list_iadd()
        self._hints = list_iadd()
        self._data = DotMap(ChainMap(kwargs, *reversed(info_kwargs)))

    @property
    def brief(self):
        """
        A message template briefly describing the error.

        The `tidyverse style guide`__ recommends using the verb "must" when the 
        cause of the problem is pretty clear, and the verb "can't" when it's 
        not.  It's common for this template to be a fixed string (i.e. no 
        parameter substitution), and for the `info` and `blame` templates to 
        reference the parameters of the exception.

        __ https://style.tidyverse.org/error-messages.html

        See `info` for a description of message templates in general.  Unlike 
        `info`, `blame`, and `hints`, there can only be a single `brief` 
        message template.  For this reason, use the assignment operator the set 
        this template (as opposed to the in-place addition operator).

        Example:

        .. code-block:: pycon

            >>> err = Error(a=1)
            >>> err.brief = "a: {a}"
            >>> raise err
            Traceback (most recent call last):
              ...
            tidyexc.exc.Error: a: 1

        """
        return self._brief

    @brief.setter
    def brief(self, value):
        self._brief = value
    
    @property
    def brief_str(self):
        """
        The `brief` message, with all parameter substitution performed.
        """
        return eval_template(self.brief, self.data)

    @property_iadd
    def info(self):
        """
        Message templates describing the context in which the error occurred.

        For example, imagine an error that was triggered because an unmatched 
        brace was encountered when parsing a file.  A good `info` message for 
        this exception might specify the file name and line number where the 
        error occurred.

        A message template can either be a string or a callable:

        - *str*: When the error message is generated, the `str.format` method 
          will be called on the string as follows: ``s.format(**self.data)``.  
          This means that any parameters associated with the exception can be 
          substituted into the message.

        - *callable*: When the error message is generated, the callable will be 
          invoked with `data` as the only argument.  It should return a string, 
          which will be taken as the message.  A common use-case for callable 
          template is to specify f-strings via lambda functions.  This is a 
          succinct way to format parameters using arbitrary expressions (see 
          example below).
          
        The `info`, `blame`, and `hints` attributes are all lists of message 
        templates.  Special syntax is added such that use can use the ``+=`` 
        operator to add message templates to any of these lists.  You can also 
        use any of the usual list methods to modify the list in-place, although 
        you cannot overwrite the attribute altogether.
        
        Example:

        .. code-block:: pycon

            >>> err = Error(a=1, b=[2,3])
            >>> err.info += "a: {a}"
            >>> err.info += lambda e: f"b: {','.join(map(str, e.b))}"
            >>> raise err
            Traceback (most recent call last):
              ...
            tidyexc.exc.Error:
            • a: 1
            • b: 2,3

        """
        return self._info

    @property
    def info_strs(self):
        """
        The `info` messages, with all parameter substitution performed.
        """
        return [eval_template(x, self.data) for x in self.info]

    @property_iadd
    def blame(self):
        """
        Message templates describing the specific cause of the error.

        For example, imagine an error that was triggered because an unmatched 
        brace was encountered when parsing a file.  A good `blame` message for 
        this exception would clearly state that an unmatched brace was the 
        cause of the problem.

        See `info` for a description of message templates in general.

        Example:

        .. code-block:: pycon

            >>> from tidyexc import Error
            >>> err = Error(a=1)
            >>> err.blame += "a: {a}"
            >>> raise err
            Traceback (most recent call last):
              ...
            tidyexc.exc.Error:
            ✖ a: 1

        """
        return self._blame

    @property
    def blame_strs(self):
        """
        The `blame` messages, with all parameter substitution performed.
        """
        return [eval_template(x, self.data) for x in self.blame]

    @property_iadd
    def hints(self):
        """
        Message templates suggesting how to fix the error.

        For example, imagine an error that was triggered because some user 
        input didn't match any of the expected keywords.  A good hint for this 
        exception might suggest the expected keyword that was most similar to 
        what the user inputted.

        See `info` for a description of message templates in general.

        Example:

        .. code-block:: pycon

            >>> from tidyexc import Error
            >>> err = Error(a=1)
            >>> err.hints += "a: {a}"
            >>> raise err
            Traceback (most recent call last):
              ...
            tidyexc.exc.Error:
            • a: 1

        """
        return self._hints

    @property
    def hint_strs(self):
        """
        The `hints` messages, with all parameter substitution performed.
        """
        return [eval_template(x, self.data) for x in self.hints]

    @property
    def data(self):
        """
        Parameters relevant to the error.

        This attribute is a DotMap_ instance.  Briefly, this means that 
        parameters can be accessed either as attributes or as dictionary 
        elements:

        .. code-block:: pycon

            >>> e = Error(a=1)
            >>> e.data.a
            1
            >>> e.data['a']
            1

        .. _DotMap: https://github.com/drgrib/dotmap
        """
        return self._data

    def __str__(self):
        """
        Return the formatted error message.

        All parameter substitutions are performed at this point, so any changes 
        made to either the message templates or the data themselves will be 
        reflected in the resulting error message.

        The error message is wrapped based on the width of the terminal.
        """
        message = ""
        parts = [
                ('',  [self.brief_str]),
                ('• ', self.info_strs),
                ('✖ ', self.blame_strs),
                ('• ', self.hint_strs),
        ]
        w = get_terminal_size().columns

        # Be conservative about line-breaking to avoid breaking paths.
        wrap_options = dict(
                break_on_hyphens=False,
                break_long_words=False,
        )

        for bullet, strs in parts:
            b = len(bullet)

            for s in strs:
                s = textwrap.fill(s, width=w-b, **wrap_options)
                s = textwrap.indent(s, b*' ')
                s = bullet + s[b:]
                message += s + '\n'

        return message
