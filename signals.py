# -*- coding: utf-8 -*-

from blinker import Namespace
my_signals = Namespace()

__all__ = ['error_signal','search_signal']

search_signal = my_signals.signal('search')
error_signal = my_signals.signal('error')
