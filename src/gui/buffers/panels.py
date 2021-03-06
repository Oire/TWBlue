# -*- coding: utf-8 -*-
############################################################
#    Copyright (c) 2014 Manuel Eduardo Cortéz Vallejo <manuel@manuelcortez.net>
#       
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################
import wx
from multiplatform_widgets import widgets

class accountPanel(wx.Panel):
 def __init__(self, parent, name_buffer):
  super(accountPanel, self).__init__(parent=parent)
  self.type = "account"
  self.name_buffer = name_buffer
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.list = widgets.list(self, _(u"Announce"))
  sizer.Add(self.list.list, 0, wx.ALL, 5)
  self.SetSizer(sizer)

 def get_more_items(self):
  output.speak(_(u"This action is not supported for this buffer"))
 
class emptyPanel(accountPanel):
 def __init__(self, parent):
  super(emptyPanel, self).__init__(parent=parent, name_buffer="")
  self.type = "empty"

