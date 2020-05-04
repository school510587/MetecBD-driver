#brailleDisplayDrivers/MetecBD.py
#A part of NonVisual Desktop Access (NVDA)
#Copyright (C) 2006-2011 NVDA Contributors <http://www.nvda-project.org/>
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

""" This file drives the BD-Devices from Metec Ingenieur AG, Stuttgart """
# intended for NVDA-version 2011-1

import controlTypes
import braille
import queueHandler
from logHandler import log
from ctypes import *
import time
import threading
import wx
import config
import speech
import NVDAObjects
import api
import textInfos
import inputCore

# layout of input from MetecBD (total 8 bytes)

# Byte 0 routing keys
# for a BD-20 or BD_40 without status cells they are numbered from 0 to 19 or 39
# for a Bd-20 or BD-40 with status cells they are numered as follows:
# 0, 1 = status keys
# 2 .. 21 or 41 = routing keys
# for the key-handling this codes are changed in the read-routine to
# 0xa0, 0xa1 for the status keys and
# to 0 .. 19 or 0 .. 39 for the routing keys
sk0 = 0xa0 # statuss key 0
sk1 = 0xa1 # statuss key 1
# you can only press 1 routing key at a time
# if you press 2 routing keys together, only one of them is reported

# Byte 1 number of braille-cells
# 0x14 = 20 for BD_20 without status cells
# 0x16 = 22 for BD_20 with status cells
# 0x28 = 40 for BD_40 without status cells
# 0x2a = 42 for BD_40 with status cells

# Byte 2 function keys shifted 8 bits to left
fk6 = 0x0100 # bit 0 right down
fk5 = 0x0200 # bit 1 right center
fk3 = 0x0400 # bit 2 left down
fk4 = 0x0800 # bit 3 right up
fk2 = 0x1000 # bit 4 left center
fk1 = 0x4000 # bit 6 left up
# attention: the 3-key-BD-40 returns allways 0xab + value of the pressed keys
# therefore we must mask the input  with 0xab (see OneLineDisplay._keyMask)

# Byte 3 cursor keys, shifted 16 bits to left
ckl = 0x040000 # bit 2 Cursorkey left
cku = 0x080000 # bit 3 Cursorkey up
ckr = 0x100000 # bit 4 Cursorkey right
ckd = 0x400000 # bit 6 Cursorkey down

# byte 4 - 7 contain garbage

#Load MetecBD.dll
try:
	MetecBD = cdll[r"brailleDisplayDrivers\MetecBD.dll"]
except:
	MetecBD = None


def _do_key(key):
	log.debug("Metec key %s"%hex(key))
	try:
		inputCore.manager.executeGesture(InputGesture(key))
		return True
	except inputCore.NoInputGestureAction:
		log.debug("Metec key %s not found"%hex(key))
		speech.speakMessage(_("keys not found"))
		return False

class OneLineDisplay:

	def __init__(self, BrdDeviceNr, lock):
		self._BrdDeviceNr = BrdDeviceNr
		self._lock = lock
		self._keyTimer = wx.PyTimer(self._readKeys)
		self ._routingKey = 255
		self._fctKey = 0 # function keys
		self._keyMask = -1 # default bits of fctKey-data for 3-key bd-40
		self._numCells = 0
		self._statusCells = 0
		self._keyTimer.Start(50)

	def terminate(self):
		try:
			self._keyTimer.Stop()
			self._keyTimer = None
		except:
			pass

	def _get_numCells(self):
		buf = create_string_buffer(8)
		with self._lock:
			MetecBD.BrdReadData(self._BrdDeviceNr,8,buf)
		self._numCells = ord(buf[1])
		# here you can set your own amount of status cells
		if self._numCells == 22 or self._numCells == 42:
		    self._numCells -= 2
		    self._statusCells = 2
		else:
		    self._statusCells = 0
		return self._numCells

	def display(self, cells):
		cells="".join([chr(x) for x in cells])
		out = create_string_buffer(self._statusCells + self._numCells)
		l = len(cells)
		if l > self._numCells:
		    l = self._numCells
		for i in range(l):
		    c1 = ord(cells[i])
		    c2 = 0
		    if c1  &   1: c2 |= 128
		    if c1  &   2: c2 |=  64
		    if c1  &   4: c2 |=  32
		    if c1  &   8: c2 |=  16
		    if c1  &  16: c2 |=   8
		    if c1  &  32: c2 |=   4
		    if c1  &  64: c2 |=   2
		    if c1  & 128: c2 |=   1
		    out[i+self._statusCells] = chr(c2)
		with self._lock:
			MetecBD.BrdWriteData(self._BrdDeviceNr,
			    self._statusCells+self._numCells,out)

	def _readKeys(self):
		# read keys
		buf = create_string_buffer(8)
		with self._lock:
			MetecBD.BrdReadData(self._BrdDeviceNr,8,buf)
		# routing keys
		routingKey = ord(buf[0])
		if routingKey != 0xff: # at least 1 rk is pressed
		    if routingKey < self._statusCells: # this iss a status key
			routingKey += sk0
		    elif self._statusCells:
			routingKey -= self._statusCells
		    self._routingKey = routingKey
		# function keyss
		fctKey = ord(buf[2]) + (ord(buf[3]) << 8)
		if self._keyMask == -1:
		    self._keyMask = fctKey
		    log.info("MetecBD length %d keyMask %s"%
			(ord(buf[1]),hex(self._keyMask)))
		fctKey &= ~self._keyMask
		self._fctKey |= fctKey
		if (self._fctKey or self._routingKey != 0xff) and\
		    fctKey == 0 and routingKey == 0xff:
			_do_key((self._fctKey << 8) | self._routingKey)
			self._fctKey = 0
			self._routingKey = 0xff

class BrailleDisplayDriver(braille.BrailleDisplayDriver):
	"""BrailleDisplayDriver for METEC-USP-Devices
	"""
	name = "MetecBD"
	description = "MetecBD"

	@classmethod
	def check(cls):
		if MetecBD:
		    return True
		else:
		    return False

	def __init__(self):
		super(BrailleDisplayDriver,self).__init__()
		self._BrdDeviceNr = c_int(-1)
		self._BrdDeviceTyp = c_int(0)
		self._BrdDeviceCls = None
		self._lock = threading.Lock()
		if MetecBD is None:
			raise RuntimeError("MetecBD.dll not found")
		self._BrdDeviceNr = \
		    c_int(MetecBD.BrdInitDevice(c_int(0),byref( \
		    self._BrdDeviceTyp)))
		if self._BrdDeviceNr.value < 0:
			raise RuntimeError("No MetecBD found")
		log.info("MetecBD found, typ=%d" \
		    % self._BrdDeviceTyp.value)
		if self._BrdDeviceTyp.value == 1:
		    self._BrdDeviceCls=OneLineDisplay( \
			self._BrdDeviceNr, self._lock)
		else:
			self.terminate()
			raise RuntimeError(
			    "not supported type of MetecBD")

	def terminate(self):
		super(BrailleDisplayDriver, self).terminate()
		if self._BrdDeviceNr.value < 0:
		    return
		if self._BrdDeviceCls:
			self._BrdDeviceCls.terminate()
			self._BrdDeviceCls = None
		with self._lock:
			MetecBD.BrdCloseDevice(self._BrdDeviceNr)
		self._BrdDeviceNr = c_int(-1)
		self._BrdDeviceNr = c_int(-1)
		self._BrdDeviceTyp = c_int(0)

	def _get_numCells(self):
		if self._BrdDeviceCls is None:
			return 0
		self.numCells = self._BrdDeviceCls._get_numCells()
		return self.numCells

	def display(self, cells):
		if not self._BrdDeviceCls is None:
			self._BrdDeviceCls.display(cells)

#-------key-mapping-------------------------------------------------------------
	gestureMap = inputCore.GlobalGestureMap({
		"globalCommands.GlobalCommands": {
			"braille_toggleTether": ("br(MetecBD):fk2+r00",),
			"braille_previousLine": ("br(MetecBD):fk1",
			    "br(MetecBD):fk4",),
			"braille_scrollBack": ("br(MetecBD):fk2",),
			"braille_nextLine": ("br(MetecBD):fk3",
			    "br(MetecBD):fk6",),
			"braille_scrollForward": ("br(MetecBD):fk5",),
			# routing keys
			"braille_routeTo": ("br(MetecBD):routing",),
			# cursor keys
			"kb:leftArrow": ("br(MetecBD):ckl",),
			"kb:upArrow": ("br(MetecBD):cku",),
			"kb:rightArrow": ("br(MetecBD):ckr",),
			"kb:downArrow": ("br(MetecBD):ckd",),
			"kb:home": ("br(MetecBD):fk1+fk3",),
			"kb:control+home": ("br(MetecBD):fk1+fk2+fk3",),
			"kb:end": ("br(MetecBD):fk4+fk6",),
			"kb:control+end": ("br(MetecBD):fk4+fk5+fk6",),
			# review commands
			"review_previousWord": ("br(MetecBD):fk2+ckl", ),
			"review_previousLine": ("br(MetecBD):fk2+cku", ),
			"review_nextWord": ("br(MetecBD):fk2+ckr",),
			"review_nextLine": ("br(MetecBD):fk2+ckd",),
			# special functions
			"say_battery_status": ("br(MetecBD):fk2+r38",),
			"showGui": ("br(MetecBD):fk2+r39",),
		}
	})
#-------key-mapping-------------------------------------------------------------

class InputGesture(braille.BrailleDisplayGesture):

    source = BrailleDisplayDriver.name

    def __init__(self, keys):
	super(InputGesture, self).__init__()
	names = set()
	if keys < sk0:
	    names.add("routing")
	    self.routingIndex = keys
	else:
	    if keys & ckd: names.add("ckd")
	    if keys & ckl: names.add("ckl")
	    if keys & ckr: names.add("ckr")
	    if keys & cku: names.add("cku")
	    if keys & fk1: names.add("fk1")
	    if keys & fk2: names.add("fk2")
	    if keys & fk3: names.add("fk3")
	    if keys & fk4: names.add("fk4")
	    if keys & fk5: names.add("fk5")
	    if keys & fk6: names.add("fk6")
	    if (keys & 0xff) < sk0: names.add("r%02d"%(keys & 0xff))
	    if (keys & 0xff) == sk0: names.add("sk0")
	    if (keys & 0xff) == sk1: names.add("sk1")
	self.id = "+".join(names)

