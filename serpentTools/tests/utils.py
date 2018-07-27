"""
Utilities to make testing easier
"""

from unittest import TestCase
from logging import NOTSET

from serpentTools.messages import (
    DictHandler, __logger__, removeHandler, addHandler,
)


class LoggerMixin(object):
    """
    Mixin class captures log messages

    Attributes
    ----------
    handler: :class:`serpentTools.messages.DictHandler
        Logging handler that stores messages in a
        :attr:`serpentTools.messages.DictHandler.logMessages`
        dictionary according to level.
    """
    def __init__(self):
        self.__old = []
        self.handler = None

    def attach(self, level=NOTSET):
        """
        Attach the :class:`serpentTools.messages.DictHandler`

        Removes all :class:`logging.Handler` objects from the
        old logger, and puts them back when :class:`detach` is
        called

        Parameters
        ----------
        level: int
            Initial level to apply to handler
        """
        self.handler = DictHandler(level)
        self.__old = __logger__.handlers
        for handler in self.__old:
            removeHandler(handler)
        addHandler(self.handler)

    def detach(self):
        """Restore the original handers to the main logger"""
        if self.handler is None:
            raise AttributeError("Handler not set. Possibly not attached.")
        removeHandler(self.handler)
        for handler in self.__old:
            addHandler(handler)
        self.handler = None
        self.__old = []

    def msgInLogs(self, level, msg, partial=False):
        """
        Determine if the message is contained in the logs

        Parameters
        ----------
        level: str
            Level under which this message was posted.
            Must be a key in the
            :attr:`~serpentTools.messages.DictHandler.logMessages`
            on the :attr:`handler` for this class
        msg: str
            Message to be found in the logs.
        partial: bool
            If this evaluates to true, then search through each
            ``message`` in `logMessages` and return ``True`` if
            ``msg in message``. Otherwise, look for exact matches

        Returns
        -------
        bool:
            If the message was found in the logs

        Raises
        ------
        KeyError:
            If the level was not found in the logs
        AttributeError:
            If the :attr:`handler` has not been
            :meth:`attach`ed
        """
        if self.handler is None:
            raise AttributeError("Handler has not been attached. Must run "
                                 "<attach> first")
        logs = self.handler.logMessages
        if level not in logs:
            raise KeyError("Level {} not found in logs. Existing levels:\n{}"
                           .format(level, list(sorted(logs.keys()))))
        if not partial:
            return msg in logs[level]
        for message in logs[level]:
            if msg in message:
                return True
        return False


class TestCaseWithLogCapture(TestCase, LoggerMixin):
    """
    Lightly overwritten :class:`unittest.TestCase` that captures logs

    Mix in the :class:`LoggerMixin` to automatically
    :meth:`~LoggerMixin.attach` during
    :meth:`~unittest.TestCase.setUp` and :meth:`~LoggerMixin.detach`
    during :meth:`~unittest.TestCase.tearDown`

    Intended to be subclassed for actual test methods
    """

    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        LoggerMixin.__init__(self)

    def setUp(self):
        """
        Method to be called before every individual test.

        :meth:`~LoggerMixin.attach`es to capture any log messages
        that would be presented during testing. Should be called
        during any subclassing.
        """
        LoggerMixin.attach(self)

    def tearDown(self):
        """
        Method to be called immediately after calling and recording test

        :meth:`~LoggerMixin.detach`es to reset the module logger to
        its original state. Should be called during any subclassing.
        """
        LoggerMixin.detach(self)
