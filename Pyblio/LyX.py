# This file is part of pybliographer
# 
# Copyright (C) 1998-2004 Frederic GOBRY
# Email : gobry@pybliographer.org
# 	   
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2 
# of the License, or (at your option) any later version.
#   
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# 
# 

import os, string, select, signal

from Pyblio import Config

class LyXClient:
    def __init__ (self):
        self.pin = None
        self.pout = None
        
        base = Config.get ('base/lyxpipe').data

        pin = os.path.expanduser (base + '.in')
        try:
            ans = os.stat (pin)
        except os.error:
            raise IOError, (-1, _("no input pipe `%s'") % pin)
        
        pout = os.path.expanduser (base + '.out')
        try:
            ans = os.stat (pout)
        except os.error:
            raise IOError, (-1, _("no output pipe `%s'") % pout)

        def noaction (* arg): return
        
        signal.signal (signal.SIGALRM, noaction)
        signal.alarm (2)
        self.pout = open (pout, 'r')
        self.pin  = open (pin,  'w')
        signal.alarm (0)
        
        # Say hello !
        self.pin.write ('LYXSRV:pyblio:hello\n')
        self.pin.flush ()
        return
    
    def __call__ (self, command, * arg):
        self.pin.write ('LYXCMD:%s:%s:%s\n' % ('pyblio', command, string.join (arg, ' ')))
        self.pin.flush ()
        
        #print self.pout.read ()
        
        #ans = string.strip (ans)
        #if ans [0:4] != 'INFO':
        #    raise IOError, ("LyX server error: " + ans,)
        return
    
    def __del__ (self):
        if not self.pin or not self.pout: return
        self.pin.write ('LYXSRV:pyblio:bye\n')
        self.pin.flush ()
        #print self.pout.read ()
        return
