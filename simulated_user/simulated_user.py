            
# -*- coding: utf-8 -*-
import random
import os
import urllib

push_number = []

for r in range(99):
    push_number.append('%i' % r)
    
push_number.append('爆')
#print push_number
cur_dir = os.path.dirname(os.path.abspath(__file__))
text_file = open(os.path.join(cur_dir, 'DB_key_word.txt'), "r")


#keyword =['斯溫','李星','提摩']
keyword = text_file.read().split(',')
text_file.close()
board =['Gossiping','LoL','NBA','joke','sex']

#push_number=['0','1','2','3','4','5','爆']


def Send_to_Server(user_output):
    if user_output is not None:
        print '[User]:'+user_output
        print '###Please wait our PTT-BOT >< ###'
        res = urllib.urlopen('http://localhost:8000/query?user_input=' + user_output)
        response= res.read()
        
        print '[PTTBot]:'+response
        return response
    else:
        print 'This dialogue is finished :)'
        exit(0)







class user_semantic:

        def __init__(self):

                self.turn=0
                self.check=0
                self.done=0
                self.dialogue_reward=0

                self.pre_action=0
                self.success_rate=0
                





                self.informed=[]
                for i in range(4):
                        self.informed.append(0)
                


                switch_board=random.choice(['0', '1']) 
                if switch_board=='0':
                        self.find = '版'
                        
                elif switch_board=='1':
                        self.find = '文章'
                else:    
                      self.find='作者'




                if    self.find == '版':
                        self.key_word = random.choice(keyword)[1:-1]
                        self.board = None
                        self.push = None


                        # record times
                        self.key_word_times=0

                        # for rewarding 
                        self.check_function=0
                        self.check_title=0
                                          

                elif self.find=='文章':

                     
                   
                        
                        key_temp = random.choice(keyword)[1:-1]
                        self.key_word=key_temp
                        #self.key_word = random.choice([None,key_temp,key_temp,key_temp])
                        board_temp = random.choice(board)
                        self.board=board_temp
                        #self.board = random.choice([None,board_temp,board_temp,board_temp,board_temp,board_temp])
                        push_temp = random.choice(push_number)
                        push_temp=random.choice([push_temp,'10','20','10','20'])
                        self.push = random.choice([push_temp])

                        # for rewarding 
                        self.check_function=0
                        self.check_title=0
                        self.check_board=0
                        self.check_score=0

                        # record times
                        self.key_word_times=0
                        self.borad_times=0
                        self.push_times=0

        
                elif self.find=='作者':
                        key_temp = random.choice(keyword)[1:-1]
                        self.key_word = random.choice([None,key_temp,key_temp,key_temp])
                        board_temp = random.choice(board)
                        self.board = random.choice([None,board_temp,board_temp,board_temp,board_temp])
                        push_temp = random.choice(push_number)
                        self.push = random.choice([None,push_temp,push_temp])

        def Reward_request_board(self,action):
            reward =0
            if action==0:
                reward-=.5
            elif action==1:
                reward-=.2
            elif action==2:
                reward-=.1
                reward-=.005*self.key_word_times
            elif action==3:
                reward-=.2
            elif action==4:
                reward+=1
            elif action==5:
                reward-=.2
            elif action==6:
                reward-=2
            elif reward==7:
                reward-=.2
            elif reward==8:
                reward-=.5
            else:
                reward-=.5
            return reward

        def Reward_request_posts(self,action):
            reward =0
            if action==0:
                reward-=.5
            elif action==1:
                reward-=.005*self.borad_times
            elif action==2:
                reward-=.005*self.key_word_times
            elif action==3:
                reward-=.005*self.push_times
            elif action==4:
                reward-=.2
            elif action==5:
                reward+=1
            elif action==6:
                reward+=1
            elif reward==7:
                reward-=.2
            elif reward==8:
                reward-=.5
            else:
                reward-=.5
            return reward

        def Give_reward(self,state,action):
            #self.turn++
            self.turn+=1
            if self.turn>=8:
                self.done=1


            reward=0
            if action ==self.pre_action:
                reward-=.5

            self.pre_action=action

            if self.find=='版':  
                self.success_rate=0
                if 'function' in state and state['function']=='request_board':
                    self.success_rate+=.5
                if 'title' in state and state['title']==self.key_word:
                    self.success_rate+=.5




                self.check=self.check_function*self.check_title
                if self.check==0:
                    if self.informed[0]==1 and self.check_function==0:
                        self.check_function=1
                        if state['function']=="request_board":
                            reward+=1
                        else:
                            reward-=1
                    if self.informed[1]==1 and self.check_title==0:
                        self.check_title=1
                        if ('title' in state and state['title']==self.key_word) or action==4:
                            reward+=1
                        else:
                            reward-=1
                else:  
                    reward=self.Reward_request_board(action)
                    if action==4:
                        self.done=1


                self.dialogue_reward+=reward
                return reward

            if self.find=='文章':
                self.success_rate=0

                if 'function' in state and state['function']=='request_post':
                    self.success_rate+=.25
                if 'title' in state and state['title']==self.key_word:
                    self.success_rate+=.25
                if 'board' in state and state['board']==self.board:
                    self.success_rate+=.25
                if 'push' in state and state['push']['score']==self.push:
                    self.success_rate+=.25




                self.check=self.check_function*self.check_title*self.check_board*self.check_score
                if self.check==0:
                    if self.informed[0]==1 and self.check_function==0:
                        self.check_function=1

                        if (state['function']=='request_post') or action==1 or action==2 or action==3:
                            reward+=1
                        else:
                            reward-=1

                    if self.informed[1]==1 and self.check_title==0:
                        self.check_title=1
                        if ('title' in state and state['title']==self.key_word) or action==1 or action==3 :
                            reward+=1
                        else:
                            reward-=1

                    if self.informed[2]==1 and self.check_board==0:
                        self.check_board=1
                        if ('board' in state and state['board']==self.board) or action==3:
                            reward+=1
                        else:
                            reward-=1
                    if self.informed[3]==1 and self.check_score==0:
                        self.check_score=1
                        if ('push' in state and state['push']['score']==self.push) or action==5 or action==6:
                            reward+=1
                        else:
                            reward-=1
                else: # already compared all of the slots  
                    reward=self.Reward_request_posts(action)
                    if action==5 or action==6:
                        self.done=1
                        
                self.dialogue_reward+=reward
                return reward




        """
            if self.find=='文章':
                if self.informed[0]==1 and self.check_function==0: 
                    self.check_function=1
                    reward=self.Reward_request_posts(action)
                    if state['function']=="request_posts":
                        reward+=2
                    else:
                        reward-=2
                elif self.check_function==1 and self.check_title==0:
             
                    reward=self.Reward_request_posts(action)

                    if self.informed[1]==1:
                        self.check_title=1
                        if state['title']==self.key_word: 
                            reward+=1
                        elif state['title']!=self.key_word:
                            reward-=1
                        else:
                            reward-=.5

                    else:
                            reward-=.1
                elif self.check_function==1 and self.check_board==0:
                  
                    reward=self.Reward_request_posts(action)
                    if self.informed[2]==1:
                        self.check_board=1
                        if state['board']==self.board :
                            reward+=1
                        elif self.board!=None:
                            reward-=1
                        else:
                            reward-=.5
                    else:
                        reward-=.1

                elif self.check_function==1 and self.check_score==0:
                    reward=self.Reward_request_posts(action)
                    if self.informed[3]==1:
                        self.check_score=1
                        if state['push']['score']==self.push:
                            reward+=1
                        elif self.board!=None:
                            reward-=1
                        else:
                            reward-=.5
                    else:
                        reward-=.1
                else:
                     reward=self.Reward_request_posts(action)

           

        """

                 

        """
            if self.find=='版':



                if self.informed[0]==1 and self.informed[1]==0 and self.check_function==0: 
                    self.check_function=1
                    if state['function']=="request_board":
                        reward+=2
                        if action==0:
                            reward-=.5
                        elif action==1:
                            reward-=.2
                        elif action==2:
                            reward+=.5
                        elif action==3:
                            reward-=.2
                        elif action==4:
                            reward+=.2
                        elif action==5:
                            reward-=.2
                        elif action==6:
                            reward-=.2
                        elif reward==7:
                            reward-=.2
                        elif reward==8:
                            reward-=.3
                        else:
                            reward-=.5
                    else:
                        reward-=2
                        if action==0:
                            reward+=.5
                        elif action==1:
                            reward-=.2
                        elif action==2:
                            reward-=.2
                        elif action==3:
                            reward-=.2
                        elif action==4:
                            reward+=.4
                        elif action==5:
                            reward-=.2
                        elif action==6:
                            reward-=.2
                        elif reward==7:
                            reward-=.2
                        elif reward==8:
                            reward-=.3
                        else:
                              reward-=.5
                elif self.informed[0]==1 and self.informed[1]==1 and self.check_function==1 and self.check_title==0:
                    self.check_title=1
                    if action==0:
                        reward-=.5
                    elif action==1:
                        reward-=.2
                    elif action==2:
                        reward-=.2
                    elif action==3:
                        reward-=.2
                    elif action==4:
                        reward+=.1
                    elif action==5:
                        reward-=.2
                    elif action==6:
                        reward-=.2
                    elif reward==7:
                        reward-=.2
                    elif reward==8:
                        reward-=.3
                    else:
                        reward-=.5
                    if state['title']==self.key_word:
                        reward+=1
                    
                    else:
                        reward-=1
                elif self.informed[0]==1 and self.informed[1]==1 and self.check_function==1 and self.check_title==1:
                    if action==0:
                        reward-=.5
                        self.informed[0]=0
                    elif action==1:
                        reward-=.2
                    elif action==2:
                        reward-=.2
                        self.informed[1]=0
                    elif action==3:
                        reward-=.2
                    elif action==4:
                        reward+=.4
                    elif action==5:
                        reward-=.2
                    elif action==6:
                        reward-=.2
                    elif reward==7:
                        reward-=.2
                    elif reward==8:
                        reward-=.3
                    else:
                        reward-=.5
                else:
                    if action==0:
                        reward-=.5
                        self.informed[0]=0
                    elif action==1:
                        reward-=.2
                    elif action==2:
                        reward-=.2
                        self.informed[1]=0
                    elif action==3:
                        reward-=.2
                    elif action==4:
                        reward+=.4
                    elif action==5:
                        reward-=.2
                    elif action==6:
                        reward-=.2
                    elif reward==7:
                        reward-=.2
                    elif reward==8:
                        reward-=.3
                    else:
                        reward-=.5
            return reward


        """














                    
        def Inform_BOT(self,action):
            Info_keyword_pattern='我'+random.choice(['想',''])+'要'+random.choice(['的',''])+random.choice(['關鍵字','keyword'])+random.choice(['是','為'])
            Info_Noneed=random.choice(['不需要','不用了','不惹','先這樣','這樣就夠了'])
            Info_board_pattern= random.choice(['我要','請幫我找','我要的是','幫我找','我需要的是','想找','找'])
            Info_push_pattern=  random.choice(['推','讚數','讚','評價'])+random.choice(['要大於','至少要','要','起碼'])
            

            # inform 0:function, 1:title 2:board 3:score
            if self.find=='版':

                if action==2 or action==0 or action==1:
                     self.informed[1]=1
                     self.key_word_times+=1
                     return Info_keyword_pattern+self.key_word


                if self.informed[1]==0:
                    self.informed[1]=1
                    self.key_word_times+=1
                    return Info_keyword_pattern+self.key_word
                else:
                    if action==2 or action==0:
                        self.key_word_times+=1
                        return Info_keyword_pattern+self.key_word
                    else:
                        return Info_Noneed
        


            elif self.find=='文章':

                if action==1:
                    self.informed[2]=1
                    self.borad_times+=1
                    return Info_board_pattern+self.board
                elif action==2:
                    self.informed[1]=1
                    self.key_word_times+=1
                    return Info_keyword_pattern+self.key_word
                elif action==3:
                    self.informed[3]=1
                    self.push_times+=1
                    return Info_push_pattern+self.push


                
                if self.informed[2]==0 :
                    self.informed[2]=1
                    self.borad_times+=1
                    return Info_board_pattern+self.board

                elif self.informed[1]==0 :

                    self.informed[1]=1
                    self.key_word_times+=1
                    return Info_keyword_pattern+self.key_word
                elif self.informed[3]==0 :

                    self.informed[3]=1
                    self.push_times+=1
                    return Info_push_pattern+self.push

                else: # have told the BOT everything
                    if action==1:
                        self.borad_times+=1
                        return Info_board_pattern+self.board
                    elif action==2:
                        self.key_word_times+=1
                        return Info_board_pattern+self.board
                    elif action==3:
                        self.push_times+=1
                        return  Info_push_pattern+self.push
                    else:
                        return Info_Noneed



               
                        

            """

                elif self.find=='作者':
                    if self.informed[0]==0:
                        self.informed[0]=1
                        if self.board!=None:
                            return Info_board_pattern+self.board+'版'
                    elif self.informed[1]==0:
                        self.informed[1]=1
                        if self.key_word!=None:
                            return Info_keyword_pattern+self.key_word
                    elif self.informed[2]==0:
                        self.informed[2]=1
                        if self.push!=None:
                            return Info_push_pattern+self.push
                    
                    else:
                        return Info_Noneed

             """
                    
            
                
          
                



        def tell_BOT(self):
            ask_board_pattern=['我要找版','給我版','我想要找版','想知道是什麼版','請幫我找版','可以幫我找版嗎','想找一個版']
            ask_board_keywoard_pattern=['我要找關於','我要找關鍵字為','想知道有','請你幫我找關鍵字有']
            ask_author_pattern=['請幫我找作者好嗎','幫我找ID好嗎','幫我找作者', '幫我找ID']
            
            
           

            if self.find=='版':
                self.informed[0]=1
                switch=random.choice(['0', '1','0','0','0']) 

                if switch=='0':
                    return random.choice(ask_board_pattern)
                else:
                    self.informed[1]=1
                    self.key_word_times+=1
                    return random.choice(ask_board_keywoard_pattern)+self.key_word+'的版'


            elif self.find=='作者':
                
                return random.choice(ask_author_pattern)
                
                
                
            else: # intent: request article 
                self.informed[0]=1  
                switch_post=[]
                idx=0
                total=0
                reponse=random.choice(['我要','我想要','我需要'])
             
                # random decide if we should fill the blank
                for x in range(3):
                    switch_post.append(random.choice(['0', '1','0','0','0','0','0','0','0','0']) )
                
                
                
                for it in switch_post:
                        
                        idx=idx+1
                        if it=='1':
                            
                            if idx==1:
                        
                                self.informed[2]=1
                                self.borad_times+=1
                                total=1
                                reponse+='在'+self.board+random.choice(['中','版','版中'])
                                    #self.informed[0]='1'
                                    
                            if idx==2:
                       
                                self.informed[1]=1
                                self.key_word_times+=1
                                total=1
                                reponse+='找關鍵字為'+self.key_word
                                    #self.informed[1]='1'

                            if idx==3:
                          
                                self.informed[3]=1
                                self.push_times+=1
                                total=1
                                reponse+='推文數大於'+self.push
                                    #self.informed[2]='1'
            
            
                if total==0:
                    return reponse+'找文章'
                else:
                    return reponse+'的文章'
        
                        
                """        
                elif query=='請問你要搜索的關鍵字為何'or query=='請告訴我你想找關於什麼樣的版':
                    return self.key_word

                elif query=='推文數大於多少你才想看':
                    return self.push

                elif query=='你想找關於什麼版的文章':
                    if self.find=='版':
                        return '不我要找版'
                    else:
                        return self.board
                """











"""

print '[User]:Hello! I am the user to help the PTT-BOT!'
continue_or_not=1
#url="http://localhost:8000/query?user_input=" + text

while continue_or_not:

    a=user_semantic()
    confirm_from_BOT='請問我能為你做什麼呢??'
    if (a.find=='版'):
    
        user_output=a.query_from_BOT(confirm_from_BOT)
        confirm_from_BOT=Send_to_Server(user_output)
        
        while sum(a.informed)!=3:
            user_output=a.Inform_BOT()
            confirm_from_BOT=Send_to_Server(user_output)

    elif a.find=='文章':
        user_output=a.query_from_BOT(confirm_from_BOT)
        confirm_from_BOT=Send_to_Server(user_output)
        while sum(a.informed)!=3:
            user_output=a.Inform_BOT()
            confirm_from_BOT=Send_to_Server(user_output)
    
            
    else:
        user_output=a.query_from_BOT(confirm_from_BOT)
        confirm_from_BOT=Send_to_Server(user_output)
        while sum(a.informed)!=3:
            user_output=a.Inform_BOT()
            confirm_from_BOT=Send_to_Server(user_output)
    


    reponse_from_bot=raw_input('Do you Want To Continue? (y/n)')
    if (reponse_from_bot== 'y' or    reponse_from_bot=='Y'):
        continue_or_not=1
    else:
        print 'Bye Bye PTT-BOT!'
        continue_or_not=0

"""



#print a.query_from_BOT('你想什麼版的文章呢??')
