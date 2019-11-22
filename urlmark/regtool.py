# -*- coding: utf-8 -*-
import winreg


class Reg(object):
	software = (
		(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall'),
		(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall'),
		(winreg.HKEY_CURRENT_USER, 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall')
	)

	@classmethod
	def search(cls, hkey, path, name):
		values = []
		key = winreg.OpenKey(hkey, path)
		subKeyCnt, attrCnt, unixTime = winreg.QueryInfoKey(key)
		for i in range(subKeyCnt):
			try:
				info = winreg.EnumKey(key, i)
				if info.find(name) >= 0:
					values.append(winreg.OpenKey(key, info))
			except OSError:
				continue

		return values

	@classmethod
	def fetch_browers(cls):
		browers = {
			'360se': '',
			'Chrome': '',
			'Firefox': '',
		}
		for hkey, path in cls.software:
			for brower in browers:
				handles = cls.search(hkey, path, brower)
				if handles:
					value = winreg.QueryValueEx(handles[0], 'InstallLocation')
					browers[brower] = value[0]

		return {i:browers[i] for i in browers if browers[i] != ''}


if __name__ == '__main__':
	rf =Reg()
	print(rf.fetch_browers())