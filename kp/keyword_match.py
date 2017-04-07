
# -*- coding: utf-8 -*-
import json
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == '__main__':
	path = '/Users/Brian/workspace/chatbot/data/database/keyword.json'
	keyword = {'爆':100,'紫爆':100}

	with open(path,'w') as outfile:
		json.dump(keyword,outfile)

