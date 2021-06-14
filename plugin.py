import sublime, sublime_plugin
import os
from os.path import join as pjoin
from glob import glob

PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))
PLUGIN_DIR_REL = os.path.relpath(PLUGIN_DIR)

UI_THEME            = 'rsms-adaptive.sublime-theme'
BRIGHT_COLOR_SCHEME = pjoin(PLUGIN_DIR_REL, 'rsms-bright.sublime-color-scheme')
DARK_COLOR_SCHEME   = pjoin(PLUGIN_DIR_REL, 'rsms-dark.sublime-color-scheme')


def load_settings():
  return sublime.load_settings('Preferences.sublime-settings')

def set_settings(**kwargs):
  settings = load_settings()
  for k, v in kwargs.items():
    settings.set(k, v)
  sublime.save_settings('Preferences.sublime-settings')
  sublime.status_message('rsms-theme: set settings ' + repr(kwargs.keys()))

# note: sublime maps the name of each top level class to a command
# through the naming convention: RsmsToggleTheme => "rsms_toggle_theme"

class RsmsToggleThemeCommand(sublime_plugin.WindowCommand):
  def run(self, **kwargs):
    current_scheme = load_settings().get('color_scheme')
    if current_scheme.find("dark") == -1:
      set_settings(color_scheme=DARK_COLOR_SCHEME, theme=UI_THEME)
    else:
      set_settings(color_scheme=BRIGHT_COLOR_SCHEME, theme=UI_THEME)


class RsmsSelectThemeCommand(sublime_plugin.WindowCommand):
  def run(self, **kwargs):
    style = kwargs.get('style')
    if style == 'dark':
      set_settings(color_scheme=DARK_COLOR_SCHEME, theme=UI_THEME)
    elif style == 'bright':
      set_settings(color_scheme=BRIGHT_COLOR_SCHEME, theme=UI_THEME)
    else:
      self.selectScheme()

  def getColorSchemeName(self, filename):
    with open(filename, 'r') as f:
      name = sublime.decode_value(f.read()).get('name')
      if name is None:
        return os.path.basename(filename)
      return [name, filename]

  def selectScheme(self):
    color_schemes = glob(pjoin(PLUGIN_DIR_REL, "*.sublime-color-scheme"))
    if len(color_schemes) == 0:
      print("rsms: no color schemes found in", PLUGIN_DIR)
      sublime.status_message("rsms: no color schemes found in %s" % PLUGIN_DIR)
      return

    color_schemes.sort()
    current_scheme_index = self.indexOfCurrentScheme(color_schemes)

    def onDone(index):
      # called with -1 if the user cancelled the operation (i.e. pressed ESC)
      if index > -1:
        set_settings(color_scheme=color_schemes[index])
      else:
        set_settings(color_scheme=color_schemes[current_scheme_index])

    def onHighlight(index):
      onDone(index)

    items = [self.getColorSchemeName(fn) for fn in color_schemes]
    #items = [[os.path.basename(_), _] for _ in color_schemes]

    self.window.show_quick_panel(
      items, onDone, 0, current_scheme_index, onHighlight)

  def indexOfCurrentScheme(self, color_schemes):
    current_scheme = load_settings().get('color_scheme')
    try:
      return [c for c in color_schemes].index(current_scheme)
    except:
      return 0

