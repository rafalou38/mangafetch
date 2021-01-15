import os
import appdirs
import json


class MagicSave(object):
	def __init__(self, dev=False):
		self.CONFIG_DIR = os.path.join(appdirs.user_data_dir(), "MangaFetch")
		self.CONFIG_MAIN_FILE = os.path.join(self.CONFIG_DIR, "save.json")
		self.indent = 4 if dev else 0

		print(self.CONFIG_MAIN_FILE)

		self.data = {}
		if not os.path.exists(self.CONFIG_DIR):
			os.makedirs(self.CONFIG_DIR)
		if not os.path.exists(self.CONFIG_MAIN_FILE):
			with open(self.CONFIG_MAIN_FILE, "w"):
				pass
	def save(self):
		with open(self.CONFIG_MAIN_FILE, "w") as file:
			json.dump(self.data, file, indent=self.indent)

	def get(self, filter=None):
		with open(self.CONFIG_MAIN_FILE, "r") as file:
			c = file.read()
			if c:
				self.data = json.loads(c)
			else:
				self.data = {}
			if filter:
				return self.data[filter] if filter in self.data.keys() else None
			else:
				return self.data
	def set(self, data={}):
		self.data = {**self.data, **data}
		self.save()

if __name__ == "__main__":
	import pretty_errors

	pretty_errors.configure(
		name                = "my_config",
		separator_character = '₪',
		filename_display    = pretty_errors.FILENAME_EXTENDED,
		line_number_first   = True,
		display_link        = True,
		lines_before        = 2,
		lines_after         = 2 ,
		line_color          = '═'+ pretty_errors.RED +'❯ ' + pretty_errors.default_config.line_color,
		code_color          = '   ' + pretty_errors.default_config.code_color,
		truncate_code       = True,
		display_arrow       = True,
	)
	pretty_errors.blacklist(
		"D:\\r\\Miniconda"
	)
	save = MagicSave(dev=True)
	save.data =  {}
	save.save()
	print(save.get())
	save.set({"favorite" : [4, 2]})
	print(save.get())
	save.set({"favorite" : [4, 5, 7]})
	save.save()
	print(save.get("favorite"))