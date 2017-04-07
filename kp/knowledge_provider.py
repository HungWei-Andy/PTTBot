# -*- coding: utf-8 -*- 
import json
import logging
import pandas
import dateutil.parser
import sys

#python sys default decode method: ascii
#so change sys decode from ascii to utf-8 done ! No Error Fxck u
reload(sys)
sys.setdefaultencoding('utf-8')



class KnowledgeProvider:
	#request 
	request = {} 
	filtered_posts=[]
	DATABASE_PATH =''
	DATABASE =[]


	def __init__(self,database_path):
		self.DATABASE_PATH = database_path

		try:
			with open(self.DATABASE_PATH) as f:
				self.DATABASE = json.load(f)
			logging.info('Database load successfully !')
		except:
			logging.warning('The database is not exist : ' + str(self.DATABASE_PATH))


	def query(self,request):
		self.request = request
		self.filtered_posts = self.DATABASE
		# print 'Filtered posts : ' + str(len(self.filtered_posts))

		if self.request['function'] == 'request_board':
			self.request_board()
		else:
			self.request_post()


	def request_post(self):
		request = self.extract_slot()
		self.find_strategy(request)


		print 
		print '[Request]:' + str(request)
		print '[Total posts]:' + str(len(self.DATABASE))
		print '[Filtered posts]:' + str(len(self.filtered_posts)) +'\n'

		try:
			MAX_SHOW_POST = 5
			show_post_count = 0
			for post in self.filtered_posts:
				show_post_count += 1
				if show_post_count <= MAX_SHOW_POST:
					print '(' + str(show_post_count) +')' 'Title->' + str(post['title'])
		except:
			logging.warning('There is no posts for you idiot~')


	def request_board(self):
		request = self.extract_slot()
		self.find_strategy(request)


		print 
		print '[Request]:' + str(request)
		print '[Total posts]:' + str(len(self.DATABASE))
		print '[Filtered posts]:' + str(len(self.filtered_posts)) +'\n'

		try:
			print 'The board you would like is:' + str(self.filtered_posts[0]['board'])
		except:
			logging.warning('There is no board fucking for you! Got it?')			



	#Input string date , Ouput datetime.datetime 
	#Input   : 'Wed Apr  5 23:22:54 2017'
	#Output: datetime.datetime(2017, 4, 5, 23, 22, 54)
	def extract_date(self,date_string):
		return dateutil.parser.parse(date_string)

	def decode_utf8(self,string):
		return string.decode('utf-8').encode('utf-8')



	def find_strategy(self,request):
		# Strategy of finding posts
		for k,v in request.iteritems():
			if k == 'board':
				self.filtered_posts = filter(lambda posts: posts[k] == v, self.filtered_posts)			
			elif k == 'title':
				#find request keyword in database title
				self.filtered_posts = filter(lambda posts: self.decode_utf8(v) in self.decode_utf8(posts[k]), self.filtered_posts)
				a=0
			elif k == 'author':
				self.filtered_posts = filter(lambda posts: self.decode_utf8(v) in self.decode_utf8(posts[k]), self.filtered_posts)				

			elif k == 'content':
				a=0
			elif k == 'comment':
				a=0
			elif k == 'push':
				for key,val in request[k].iteritems():
					if key=='all':
						self.filtered_posts = filter(lambda posts: posts[k][key] >= val, self.filtered_posts)
					elif key=='score':
						self.filtered_posts = filter(lambda posts: posts[k][key] >= val, self.filtered_posts)
					elif key=='good':
						self.filtered_posts = filter(lambda posts: posts[k][key] >= val, self.filtered_posts)				
					elif key=='bad':
						self.filtered_posts = filter(lambda posts: posts[k][key] >= val, self.filtered_posts)
					elif key=='none':
						self.filtered_posts = filter(lambda posts: posts[k][key] >= val, self.filtered_posts)
					else:
						self.filtered_posts = filter(lambda posts: posts[k][key] >= val, self.filtered_posts)

			elif k == 'date':
				a=0
			elif k == 'ip':
				a=0
			else:
				a=0

	#remove user request which value is None, in other words, remain useful slot
	def extract_slot(self):
		request_tmp = self.request

		for key, val in list(request_tmp.iteritems() ):
			if key == 'comment'  or key =='push':
				for k,v in list(request_tmp[key].iteritems()) :
					if v is None:
						del request_tmp[key][k]
				if request_tmp[key] =={}:
					del request_tmp[key]
			else:
				if val is None:
					del request_tmp[key]

		return request_tmp




def keyword_translate(request, keyword_dict):
	req = request
	for k,v in req['push'].iteritems():
		for key,val in keyword_dict.iteritems():
			if v == key:
				req['push'][k] = val
	return req





#request = {'function':None,'board':None,'title':None,'author':None,'content':None,'comment':{'state':None,'message':None,'id':None,'date':None},'push':{'all':None,'score':None,'good':None,'bad':None,'none':None},'date':None,'ip':None}

# if __name__ == '__main__':
# 	database_path = 'database/merged_file.json'
# 	traindata_path = 'traindata/traindata_fortest.csv'

# 	# Gossiping, sex, LOL, joke, NBA

# 	#幫我找出西斯版爆的文章
# 	request_1 = {'function':'request_post','board':'sex','title':None,'author':None,'content':None,'comment':{'state':None,'message':None,'id':None,'date':None},'push':{'all':None,'score':'爆','g':None,'b':None,'n':None},'date':None,'ip':None}

# 	#幫我找出這個月JOKE版噓文大於5的文章
# 	request_2 = {'function':'request_post','board':'joke','title':None,'author':None,'content':None,'comment':{'state':None,'message':None,'id':None,'date':None},'push':{'all':None,'score':None,'g':None,'b':5,'n':None},'date':None,'ip':None}

# 	#顯示這個月作者為FallRed的文章
# 	request_3 = {'function':'request_post','board':None,'title':None,'author':'FallRed','content':None,'comment':{'state':None,'message':None,'id':None,'date':None},'push':{'all':None,'score':None,'g':None,'b':None,'n':None},'date':None,'ip':None}

# 	#我想看關鍵字有嘿咻的文章
# 	request_4 = {'function':'request_post','board':None,'title':'嘿咻','author':None,'content':None,'comment':{'state':None,'message':None,'id':None,'date':None},'push':{'all':None,'score':None,'g':None,'b':None,'n':None},'date':None,'ip':None}

# 	#j我想看這周HKE的版
# 	request_5 = {'function':'request_board','board':None,'title':'HKE','author':None,'content':None,'comment':{'state':None,'message':None,'id':None,'date':None},'push':{'all':None,'score':None,'g':None,'b':None,'n':None},'date':None,'ip':None}

# 	#請搜尋關鍵字有約炮的版
# 	request_6 = {'function':'request_board','board':None,'title':'約炮','author':None,'content':None,'comment':{'state':None,'message':None,'id':None,'date':None},'push':{'all':None,'score':'爆','g':None,'b':None,'n':None},'date':None,'ip':None}

# 	#請搜尋關鍵字有約炮的爆文
# 	#請搜尋關鍵字有約砲的爆文
# 	request_7 = {'function':'request_post','board':None,'title':'約炮','author':None,'content':None,'comment':{'state':None,'message':None,'id':None,'date':None},'push':{'all':None,'score':'爆','g':None,'b':None,'n':None},'date':None,'ip':None}

# 	keyword_dict = {'爆':100,'紫爆':100}

# 	request = keyword_translate(request_4, keyword_dict)
# 	# print request_6['push']['score']
# 	# print req['push']['score']

# 	kp = KnowledgeProvider(database_path)
# 	kp.query(request)


# 	# traindata = pandas.read_csv(traindata_path,sep=',',header=None,keep_default_na=False)
# 	# matrix = traindata.as_matrix()
# 	# print matrix
# 	# print traindata(index=range(0, 9, 3))

