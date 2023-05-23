import os
import shutil
import subprocess
from tempfile import TemporaryDirectory
import time
from typing import Dict, List, Optional, Tuple
import psutil
import logging
import platform

def is_mac():
  return platform.system() == 'Darwin'

def is_win():
  return platform.system() == 'Windows'

class Browser:
  binary_name: str
  use_user_data_dir: bool = True
  temp_user_data_dir: Optional[TemporaryDirectory] = None

  args: List[str] = []

  process: Optional[subprocess.Popen] = None

  @classmethod
  def name(cls) -> str:
    return cls.__name__

  def profile_dir(self) -> str:
    raise RuntimeError('Not implemented')

  def binary(self) -> str:
    if is_mac():
      return self.binary_mac()
    if is_win():
      return self.binary_win()
    raise RuntimeError('Unsupported platform')

  def binary_mac(self) -> str:
    return f'/Applications/{self.binary_name}.app/Contents/MacOS/{self.binary_name}'

  def binary_win(self) -> str:
    raise RuntimeError('Not implemented')

  def _get_start_cmd(self, use_source_profile = False) -> List[str]:
    args = [self.binary()]
    if self.use_user_data_dir:
      if use_source_profile:
        args.append(f'--user-data-dir={self._get_source_profile()}')
      else:
        args.append(f'--user-data-dir={self._get_target_profile()}')

    args.extend(self.args)
    return args

  def get_all_processes(self) -> List[psutil.Process]:
    assert self.process is not None
    main_process = psutil.Process(self.process.pid)
    processes = [main_process]
    children = main_process.children(recursive=True)
    for child in children:
      processes.append(child)
    return processes


  def _get_source_profile(self) -> str:
    dir = os.path.join(os.curdir, 'browser_profiles', platform.system(), self.name())
    return os.path.abspath(dir)

  def _get_target_profile(self) -> str:
    if self.use_user_data_dir:
      if self.temp_user_data_dir is None:
        self.temp_user_data_dir = TemporaryDirectory(prefix = self.name() + '-user-data-')
      return self.temp_user_data_dir.name
    assert self.profile_dir()
    return self.profile_dir()

  def prepare_profile(self, unsafe = False):
      target_profile = self._get_target_profile()
      if os.path.exists(target_profile):
        if not self.use_user_data_dir and unsafe == False:
          accept = input(f'Have you backup your profile {target_profile}? Type YES to delete it and continue.')
          if accept != 'YES':
            raise RuntimeError(f'Aborted by user')
        shutil.rmtree(target_profile)
      if not os.path.exists(self._get_source_profile()):
        raise RuntimeError(f'Can\'t find source profile')
      shutil.copytree(self._get_source_profile(), self._get_target_profile())


  def start(self, use_source_profile=False):
    assert self.process is None
    logging.debug(self._get_start_cmd(use_source_profile))
    self.process = subprocess.Popen(self._get_start_cmd(use_source_profile), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

  def terminate(self):
    assert self.process is not None
    self.process.terminate()
    time.sleep(1)
    self.process.kill()

  def open_url(self, url: str):
    assert self.process is not None
    rv = subprocess.call(self._get_start_cmd() + [url], stdout=subprocess.PIPE)
    if self.name() != 'Opera':
      assert rv == 0

class Brave(Browser):
  binary_name = 'Brave Browser'
  def binary_win(self) -> str:
    return os.path.expandvars(Rf'%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe')

class Chrome(Browser):
  binary_name = 'Google Chrome'
  def binary_win(self) -> str:
    return os.path.expandvars(Rf'%ProgramFiles%\Google\Chrome\Application\chrome.exe')

class ChromeUBO(Chrome):
  pass

class Opera(Browser):
  binary_name = 'Opera'
  args = ['--ran-launcher']
  def binary_win(self) -> str:
    return os.path.expandvars(R'%USERPROFILE%\AppData\Local\Programs\Opera\99.0.4788.13_0\opera.exe')

class Edge(Browser):
  binary_name = 'Microsoft Edge'

  def binary_win(self) -> str:
    return os.path.expandvars(R'%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe')

class Safari(Browser):
  binary_name = 'Safari'
  use_user_data_dir = False

  def profile_dir(self) -> str:
    if is_mac():
      return '~/Library/Safari'
    raise RuntimeError('Not implemented')


class Firefox(Browser):
  binary_name = 'Firefox'
  vendor = 'Mozilla'
  use_user_data_dir = False

  def profile_dir(self) -> str:
    if is_mac():
      return '~/Library/Application Support/Firefox/'
    if is_win():
      return os.path.expandvars(R'%USERPROFILE%\AppData\Roaming\Mozilla\Firefox')
    raise RuntimeError('Not implemented')

  def binary_win(self) -> str:
    return os.path.expandvars(R'%ProgramW6432%\Mozilla Firefox\firefox.exe')

BROWSER_LIST = [Brave, Chrome, ChromeUBO, Opera, Edge, Safari, Firefox]

def get_browsers_classes_by_name(name: str):
  if name == 'all':
    return BROWSER_LIST
  for b in BROWSER_LIST:
    if b.name() == name:
      return [b]
  raise RuntimeError(f'No browser with name {name} found')
