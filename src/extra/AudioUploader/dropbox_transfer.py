# -*- coding: utf-8 -*-
import threading
import time
import os
import exceptions
import wx
import dropbox
import config
from mysc import event
from utils import *
from dropbox.rest import ErrorResponse
from StringIO import StringIO

class UnauthorisedError(exceptions.Exception):
 def __init__(self, *args, **kwargs):
  super(UnauthorisedError, self).__init__(*args, **kwargs)

class newChunkedUploader(dropbox.client.ChunkedUploader):
 def __init__(self, client, file_obj, length, callback):
  super(newChunkedUploader, self).__init__(client, file_obj, length)
  self.progress_callback = callback

 def upload_chunked(self, chunk_size = 4 * 1024 * 1024):
  while self.offset < self.target_length:
   next_chunk_size = min(chunk_size, self.target_length - self.offset)
   if self.last_block == None:
    self.last_block = self.file_obj.read(next_chunk_size)

   try:
    (self.offset, self.upload_id) = self.client.upload_chunk(
                    StringIO(self.last_block), next_chunk_size, self.offset, self.upload_id)
    self.last_block = None
    if callable(self.progress_callback): self.progress_callback(self.offset)
   except ErrorResponse as e:
    reply = e.body
    if "offset" in reply and reply['offset'] != 0:
     if reply['offset'] > self.offset:
      self.last_block = None
      self.offset = reply['offset']

class dropboxLogin(object):
 def __init__(self):
  self.logged = False
  self.app_key = "c8ikm0gexqvovol"
  self.app_secret = "gvvi6fzfecooast"

 def get_url(self):
  self.flow = dropbox.client.DropboxOAuth2FlowNoRedirect(self.app_key, self.app_secret)
  return self.flow.start()

 def authorise(self, code):
  access_token, user_id = self.flow.finish(code)
  config.main["services"]["dropbox_token"] = access_token
  self.logged = True

class dropboxUploader(object):
 def __init__(self, filename, completed_callback, wxDialog, short_url=False):
  if config.main["services"]["dropbox_token"] != "":
   self.client = dropbox.client.DropboxClient(config.main["services"]["dropbox_token"])
  else:
   raise UnauthorisedError("You need authorise TWBlue")
  self.filename = filename
  self.short_url = short_url
  self.wxDialog = wxDialog
  self.file = open(self.filename, "rb")
  self.file_size = os.path.getsize(self.filename)
  self.uploader = newChunkedUploader(client=self.client, file_obj=self.file, length=self.file_size, callback=self.process)
  self.start_time = None
  self.completed_callback = completed_callback
  self.background_thread = None
  self.current = 0
  self.transfer_rate = 0

 def elapsed_time(self):
  if not self.start_time:
   return 0
  return time.time() - self.start_time

 def perform_transfer(self):
  self.start_time = time.time()
  while self.uploader.offset < self.file_size:
   self.uploader.upload_chunked(self.file_size/100)
  self.transfer_completed()

 def process(self, offset):
  progress = {}
  self.current = offset
  progress["total"] = self.file_size
  progress["current"] = self.current
  progress["percent"] = int((float(progress["current"]) / progress["total"]) * 100)
  self.transfer_rate = progress["current"] / self.elapsed_time()
  progress["speed"] = '%s/s' % convert_bytes(self.transfer_rate)
  if self.transfer_rate:
   progress["eta"] = (progress["total"] - progress["current"]) / self.transfer_rate
  else:
   progress["eta"] = 0
  info = event.event(event.EVT_OBJECT, 1)
  info.SetItem(progress)
  wx.PostEvent(self.wxDialog, info)

 def perform_threaded(self):
  self.background_thread = threading.Thread(target=self.perform_transfer)
  self.background_thread.daemon = True
  self.background_thread.start()

 def transfer_completed(self):
  self.uploader.finish(os.path.basename(self.filename))
  if callable(self.completed_callback):
   self.completed_callback()

 def get_url(self):
  original = "%s" % (self.client.share(os.path.basename(self.filename), False)["url"])
  return original.replace("dl=0", "dl=1")