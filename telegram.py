from bs4 import BeautifulSoup
from requests import get
import logging
import time
import telebot
from telebot import types
import datetime
import mysql.connector

mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="wp_xeon")
API_TOKEN = '551792388:AAFKFNKrbApCx1x-XKoV1XONQXJuxQt_FqU'
title=''
para=''

bot = telebot.TeleBot(API_TOKEN)
disp_name=''
ID=''
categories ={"Sports":4,"Music":5,"History":6,"Science":7,"Technology":8,"Politics":9,"Geography":10,"Arts":11}
now = datetime.datetime.now()
l1=[]
l2=[]
l3=[]
l4=[]
dict1={}
dict2={}
dict3={}
list_of_articles=[]
cat=-1
postid=-1

@bot.message_handler(commands=['help', 'Start','start'])
def send_welcome(message):
	cursor = mydb.cursor()
	query=("SELECT ID FROM wp_users WHERE user_pass=%s")
	val=(message.chat.id,)
	cursor.execute(query, val)
	cursor.fetchall()
	if cursor.rowcount ==0:
		msg = bot.reply_to(message,'Hi there, Welcome to Xeon.\n\nSince this is your first time here , Please Enter a Username : \n\n/Exit')
		bot.register_next_step_handler(msg,reg_user)
	else:
		query1=("SELECT ID,display_name FROM wp_users WHERE user_pass=%s")
		val=(message.chat.id,)
		cursor.execute(query1, val)
		result_set = cursor.fetchone()
		global disp_name
		global ID
		disp_name=str(result_set[1])
		ID=str(result_set[0])
		str5='Hi ' + disp_name +'.\n\nWhat would you like to do today :\n\n1. /Contribute \n\n2. /Services \n\n3. /Admin\n\n/Exit'
		msg = bot.reply_to(message, str5)

def reg_user(message):
	value=message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	else:
		cursor = mydb.cursor()
		query = ("INSERT into wp_users(user_pass,user_nicename,display_name,user_registered,user_status) VALUES (%s,%s,%s,%s,0)")
		val=(message.chat.id,message.text,message.text,now)
		cursor.execute(query, val)
		msg = bot.reply_to(message,'User Registered.\n/Start')
		mydb.commit()
		bot.register_next_step_handler(msg,send_welcome)

@bot.message_handler(commands=['Contribute'])
def Contribute(message):
	str1='Select a Operation:\n\n1. /Add_Article \n\n2. /Modify_Article \n\n3. /Delete_Article\n\n/Exit'
	msg = bot.reply_to(message, str1)

@bot.message_handler(commands=['Exit'])
def Exit(message):
	msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
	bot.register_next_step_handler(msg,send_welcome)

@bot.message_handler(commands=['Add_Article'])
def Add_Article(message):
	value= message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	else:
		str1=''
		global categories
		count=1
		for key, value in categories.items() :
			str1+='\n\n'+str(count)+'. /'+str(key)
			count+=1
		msg = bot.reply_to(message, "Please select a category for the new post:\n"+str1+"\n\n/Exit")
		bot.register_next_step_handler(msg,add_to_category)

def add_to_category(message):
	global categories
	value= message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	else:
		value=value.replace('/','')
		global cat
		cat=categories[value]
		msg = bot.reply_to(message, 'Enter Title :\n\n/Exit')
		bot.register_next_step_handler(msg, add_title)

def add_title(message):
	value=message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	else:
		global title
		title=message.text
		msg = bot.reply_to(message, 'Enter Description (in less than 100 words):\n\n/Exit')
		bot.register_next_step_handler(msg,add_para)

def add_para(message):
	value=message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	else:
		global title
		global ID
		global cat
		now = datetime.datetime.now()
		para=message.text
		mycursor = mydb.cursor()
		idsql="SELECT max(ID) FROM wp_posts"
		mycursor.execute(idsql,)
		result_set = mycursor.fetchone()
		newid=int(result_set[0])
		newid+=1	
		url=title.replace(' ','_')
		sql = "INSERT INTO wp_posts (post_type,ID,post_author,post_date,post_date_gmt,post_modified,post_modified_gmt,post_content,post_title,post_name,post_status,post_excerpt,to_ping,pinged,post_content_filtered) values ('post',"+str(newid)+","+str(ID)+",%s,%s,%s,%s,%s,%s,%s,'draft','','','','')" 
		val = (now,now,now,now,para,title,url)
		mycursor.execute(sql, val)
		mydb.commit()
		sql=" INSERT INTO wp_term_relationships (object_id,term_taxonomy_id,term_order) VALUES ("+str(newid)+","+str(cat)+",0)"
		mycursor.execute(sql)
		mydb.commit()
		mycursor.close() 
		bot.send_message(chat_id=message.chat.id,text=title)
		bot.send_message(chat_id=message.chat.id,text=para)
		msg = bot.send_message(chat_id=message.chat.id,text="Post submitted for review \n/Add_Article \n/Exit")

@bot.message_handler(commands=['Modify_Article'])
def Modify_Article(message):
	value= message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	else:
		str1=''
		global categories
		count=1
		for key, value in categories.items() :
			str1+='\n\n'+str(count)+'. /'+str(key)
			count+=1
		msg = bot.reply_to(message, "Please select a post category to modify:\n"+str1+"\n\n/Exit")
		bot.register_next_step_handler(msg,ModificationCategory)
		
def ModificationCategory(message):
	global categories
	value= message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	else:
		value=value.replace('/','')
		global cat
		global ID
		global dict3
		cat=categories[value]		
		cursor = mydb.cursor()
		query="select post_name,ID FROM wp_posts where post_status='publish' and ID in (SELECT object_id from wp_term_relationships WHERE term_taxonomy_id="+str(cat)+")"
		cursor.execute(query)
		resultset=cursor.fetchall()
		if(cursor.rowcount==0):
			msg = bot.reply_to(message,"Nothing to Modify in this category\n /Check_Other_Categories")
			bot.register_next_step_handler(msg,Modify_Article)
		else:
			count=1
			str3=''
			for i in resultset:
				str3+='\n'+str(count)+'. /'+str(i[0])
				dict3[i[0]]=i[1]
				count+=1
			msg = bot.reply_to(message,str3+"\n\n/Exit")
			bot.register_next_step_handler(msg, modify_this_post)

@bot.message_handler(commands=['modify_this_post'])
def modify_this_post(message):
	value= message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	else:
		global dict3
		global postid
		global title
		cursor = mydb.cursor()
		value=message.text
		if value=='/Exit':
			msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
			bot.register_next_step_handler(msg,send_welcome)
		value=value.replace('/','')
		postid=dict3[value]	
		query=("select post_content,post_name from wp_posts where ID = "+str(postid))
		cursor.execute(query)
		resultset=cursor.fetchone()
		title=resultset[1]
		msg = bot.reply_to(message,'Copy the content, paste and modify.')
		bot.send_message(chat_id=message.chat.id,text=resultset[0])
		bot.send_message(chat_id=message.chat.id,text="\n\n/Exit")
		cursor.close()	
		bot.register_next_step_handler(msg, modification_submit)

@bot.message_handler(commands=['modification_submit'])
def modification_submit(message):
	value=message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	else:
		global title
		global postid
		global ID
		now = datetime.datetime.now()
		para=message.text
		mycursor = mydb.cursor()
		idsql="SELECT max(ID) FROM wp_posts"
		mycursor.execute(idsql,)
		result_set = mycursor.fetchone()
		newid=int(result_set[0])
		newid+=1	
		url=title.replace(' ','_')
		sql = "INSERT INTO wp_posts (post_type,ID,post_author,post_date,post_date_gmt,post_modified,post_modified_gmt,post_content,post_title,post_name,post_status,post_excerpt,to_ping,pinged,post_content_filtered,post_parent) values ('post',"+str(newid)+","+str(ID)+",%s,%s,%s,%s,%s,%s,%s,'modification','','','','',"+str(postid)+")" 
		val = (now,now,now,now,para,title,url)
		mycursor.execute(sql, val)
		mydb.commit()		
		mycursor.close() 
		bot.send_message(chat_id=message.chat.id,text=title)
		bot.send_message(chat_id=message.chat.id,text=para)
		bot.send_message(chat_id=message.chat.id,text="Post modification submitted for review\n/Modify_Article \n/Exit")
		

@bot.message_handler(commands=['Delete_Article'])
def Delete_Article(message):
	global ID
	global dict1
	value=message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	else:
		cursor = mydb.cursor()
		query = ("SELECT post_name,ID FROM wp_posts WHERE post_author= %s")
		val=(ID,)
		cursor.execute(query, val)
		resultset=cursor.fetchall()
		if(cursor.rowcount==0):
			msg = bot.reply_to(message,"Nothing to Delete /Start")
			bot.register_next_step_handler(msg, send_welcome)
		else:
			count=1
			str3=''
			for i in resultset:
				str3+='\n'+str(count)+'. /'+str(i[0])
				dict1[i[0]]=i[1]
				count+=1
			msg = bot.reply_to(message,str3+"\n\n/Exit")
			bot.register_next_step_handler(msg, del_art)
		
@bot.message_handler(commands=['del_art'])
def del_art(message):
	value=message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	else:
		global dict1
		cursor = mydb.cursor()
		value=message.text
		if value=='/exit':
			msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
			bot.register_next_step_handler(msg,send_welcome)
		value=value.replace('/','')
		postid=dict1[value]
		query = ("DELETE FROM wp_posts WHERE ID = %s")
		val=(postid,)
		cursor.execute(query, val)
		mydb.commit()
		query = ("DELETE FROM wp_term_relationships WHERE object_id = %s")
		val=(postid,)
		cursor.execute(query, val)
		mydb.commit()
		msg = bot.reply_to(message,'Article Deleted.\n/Delete_Article\n/Exit')
		dict1.clear()
		cursor.close()	
		bot.register_next_step_handler(msg, send_welcome)

@bot.message_handler(commands=['Admin'])
def Admin(message):
	value=message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	else:
		msg = bot.reply_to(message,'Enter Secret Code : \n/Exit')
		bot.register_next_step_handler(msg,CheckAdmin)

@bot.message_handler(commands=['CheckAdmin'])
def CheckAdmin(message):
	if(message.text=='/Exit'):
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	elif(message.text=='password'):
		str5='Hi Admin' + '\n1. /Approve_Posts \n2. /Approve_Post_Modification\n3. /Delete_Posts\n\n/Exit'
		msg = bot.reply_to(message,str5)
	else:
		msg = bot.reply_to(message,'Incorrect Code , re-enter code or exit \n\n/Exit')
		bot.register_next_step_handler(msg,CheckAdmin)

@bot.message_handler(commands=['Approve_Posts'])
def Approve_Posts(message):
	value=message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	else:
		str1=''
		global categories
		count=1
		for key, value in categories.items() :
			str1+='\n\n'+str(count)+'. /'+str(key)
			count+=1
		msg = bot.reply_to(message, str1+"\n\n/Exit")
		bot.register_next_step_handler(msg,ApproveCategory)

def ApproveCategory(message):
	global categories
	value= message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	else:
		value=value.replace('/','')
		global cat
		global ID
		global dict2
		cat=categories[value]		
		cursor = mydb.cursor()
		query="select post_name,ID FROM wp_posts where post_status='draft' and ID in (SELECT object_id from wp_term_relationships WHERE term_taxonomy_id="+str(cat)+")"
		cursor.execute(query)
		resultset=cursor.fetchall()
		if(cursor.rowcount==0):
			msg = bot.reply_to(message,"Nothing to Approve in this category\n /Check_Other_Categories\n/Exit")
			bot.register_next_step_handler(msg,Approve_Posts)
		else:
			count=1
			str3=''
			for i in resultset:
				str3+='\n'+str(count)+'. /'+str(i[0])
				dict2[i[0]]=i[1]
				count+=1
			msg = bot.reply_to(message,str3+"\n\n/Exit")
			bot.register_next_step_handler(msg, show_approval_article)

@bot.message_handler(commands=['show_approval_article'])
def show_approval_article(message):
	value= message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	else:
		global dict2
		global postid
		cursor = mydb.cursor()
		value=message.text
		if value=='/Exit':
			msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
			bot.register_next_step_handler(msg,send_welcome)
		value=value.replace('/','')
		postid=dict2[value]	
		query = ("select post_name,post_content from wp_posts where ID="+str(postid))	
		cursor.execute(query)
		resultset=cursor.fetchone()
		bot.send_message(chat_id=message.chat.id,text=resultset[0])
		bot.send_message(chat_id=message.chat.id,text=resultset[1])
		msg = bot.send_message(chat_id=message.chat.id,text="/Approve_this_post \n/Disapprove_this_post\n\n/Exit")
		cursor.close()	
		dict1.clear()
		bot.register_next_step_handler(msg,admin_decision)

@bot.message_handler(commands=['admin_decision'])
def admin_decision(message):	
	global postid
	value=message.text
	cursor = mydb.cursor()
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	elif(value=='/Approve_this_post'):
		query = ("update wp_posts set post_status='publish' WHERE ID="+str(postid))		
		cursor.execute(query)
		mydb.commit()
		msg = bot.reply_to(message,'Article published \n/Approve_Posts\n\n/Exit')
		dict1.clear()
		cursor.close()	
	elif(value=='/Disapprove_this_post'):
		query = ("DELETE FROM wp_posts WHERE ID = "+str(postid))		
		cursor.execute(query)
		mydb.commit()
		query = ("DELETE FROM wp_term_relationships WHERE object_id ="+str(postid))		
		cursor.execute(query)
		mydb.commit()
		msg = bot.reply_to(message,'Article Deleted /Approve_Posts')
		cursor.close()	
	
@bot.message_handler(commands=['Approve_Post_Modification'])
def Approve_Post_Modification(message):	
	value=message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	else:
		str1=''
		global categories
		count=1
		for key, value in categories.items() :
			str1+='\n\n'+str(count)+'. /'+str(key)
			count+=1
		msg = bot.reply_to(message, str1+"\n\n/Exit")
		bot.register_next_step_handler(msg,ApproveModificationCategory)

def ApproveModificationCategory(message):
	global categories
	value= message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	else:
		value=value.replace('/','')
		global cat
		global ID
		global dict2
		cat=categories[value]		
		cursor = mydb.cursor()
		query="select post_name,ID FROM wp_posts where post_status='modification' and post_parent in (SELECT object_id from wp_term_relationships WHERE term_taxonomy_id="+str(cat)+")"
		cursor.execute(query)
		resultset=cursor.fetchall()
		if(cursor.rowcount==0):
			msg = bot.reply_to(message,"Nothing to Approve in this category\n /Check_Other_Categories")
			bot.register_next_step_handler(msg,Approve_Post_Modification)
		else:
			count=1
			str3=''
			for i in resultset:
				str3+='\n'+str(count)+'. /'+str(i[0])
				dict2[i[0]]=i[1]
				count+=1
			msg = bot.reply_to(message,str3+"\n\n/Exit")
			bot.register_next_step_handler(msg, show_modify_approval_article)

@bot.message_handler(commands=['show_modify_approval_article'])
def show_modify_approval_article(message):
	global dict2
	global postid
	cursor = mydb.cursor()
	value=message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	value=value.replace('/','')
	postid=dict2[value]	
	query = ("select post_name,post_content,post_parent from wp_posts where ID="+str(postid))	
	cursor.execute(query)
	resultset=cursor.fetchone()
	query = ("select post_content from wp_posts where ID="+str(resultset[2]))	
	cursor.execute(query)
	resultset2=cursor.fetchone()
	bot.send_message(chat_id=message.chat.id,text=resultset[0])
	bot.send_message(chat_id=message.chat.id,text="Old Content :")
	bot.send_message(chat_id=message.chat.id,text=resultset2[0])
	bot.send_message(chat_id=message.chat.id,text="New Content :")
	bot.send_message(chat_id=message.chat.id,text=resultset[1])
	msg = bot.send_message(chat_id=message.chat.id,text="/Approve_this_modification \n/Disapprove_this_modification\n\n/Exit")
	cursor.close()	
	dict1.clear()
	bot.register_next_step_handler(msg,admin_modification_decision)

@bot.message_handler(commands=['admin_modification_decision'])
def admin_modification_decision(message):	
	global postid
	value=message.text
	cursor = mydb.cursor()
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)	
	elif(value=='/Approve_this_modification'):
		query = ("select post_content,post_parent from wp_posts where ID="+str(postid))	
		cursor.execute(query)
		resultset=cursor.fetchone()
		query = ("update wp_posts set post_content=%s WHERE ID="+str(resultset[1]))
		val=(resultset[0],)
		cursor.execute(query,val)
		mydb.commit()
		query = ("DELETE FROM wp_posts WHERE ID = "+str(postid))		
		cursor.execute(query)
		mydb.commit()
		msg = bot.reply_to(message,'Article modification published \n/Approve_Post_Modification\n\n/Exit')
		dict1.clear()
		cursor.close()	

	elif(value=='/Disapprove_this_modification'):
		query = ("DELETE FROM wp_posts WHERE ID = "+str(postid))		
		cursor.execute(query)
		mydb.commit()		
		msg = bot.reply_to(message,'Article Deleted \n/Approve_Post_Modification\n\n/Exit')
		cursor.close()	
	
@bot.message_handler(commands=['Delete_Posts'])
def Delete_Posts(message):
	value= message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	else:
		str1=''
		global categories
		count=1
		for key, value in categories.items() :
			str1+='\n\n'+str(count)+'. /'+str(key)
			count+=1
		msg = bot.reply_to(message, str1+"\n\n/Exit")
		bot.register_next_step_handler(msg,DeletionCategory)
		
def DeletionCategory(message):
	global categories
	value= message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	else:
		value=value.replace('/','')
		global cat
		global ID
		global dict3
		cat=categories[value]		
		cursor = mydb.cursor()
		query="select post_name,ID FROM wp_posts where post_status='publish' and ID in (SELECT object_id from wp_term_relationships WHERE term_taxonomy_id="+str(cat)+")"
		cursor.execute(query)
		resultset=cursor.fetchall()
		if(cursor.rowcount==0):
			msg = bot.reply_to(message,"Nothing to Delete in this category\n /Check_Other_Categories")
			bot.register_next_step_handler(msg,Delete_Posts)
		else:
			count=1
			str3=''
			for i in resultset:
				str3+='\n'+str(count)+'. /'+str(i[0])
				dict3[i[0]]=i[1]
				count+=1
			msg = bot.reply_to(message,str3+"\n\n/Exit")
			bot.register_next_step_handler(msg, delete_this_post)

@bot.message_handler(commands=['delete_this_post'])
def delete_this_post(message):
	global dict3
	global postid
	cursor = mydb.cursor()
	value=message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	value=value.replace('/','')
	postid=dict3[value]	
	query = ("DELETE FROM wp_posts WHERE ID = "+str(postid))		
	cursor.execute(query)
	mydb.commit()
	query = ("DELETE FROM wp_term_relationships WHERE object_id ="+str(postid))		
	cursor.execute(query)
	mydb.commit()
	msg = bot.reply_to(message,'Post Deleted \n/Delete_Posts\n/Exit')
	cursor.close()	

@bot.message_handler(commands=['Services'])
def Services(message):
	str1='\n1. /Movies (Recommendation) \n\n2. /TV_shows (Recommendation)\n\n/Exit'
	msg = bot.reply_to(message, str1)

@bot.message_handler(commands=['TV_shows'])
def TV_shows(message):
	url='https://www.imdb.com/feature/genre/'
	response = get(url)
	soup= BeautifulSoup(response.text,'html.parser')
	x=soup.find_all(attrs={'class':'table-cell primary'})
	for i in x:
	    l3.append(i.a.text) 
	    i=i.find('a')
	    if i.has_attr('href'):
	        l4.append(i.attrs['href'])
	str1=''
	count=1
	for i in l3:
		i=i.replace(' ','_')
		i=i.replace('&','and')
		i=i.replace('-',',')
		str1=str1+str(count)+". /"+i+"\n"
		count+=1
		if count==25:
			break
	msg = bot.reply_to(message, str1)
	bot.register_next_step_handler(msg, TV_rec)

def TV_rec(message):
	value= message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	else:
		value=value.replace('_',' ')
		value=value.replace('and','&')
		value=value.replace('/','')
		value=value.replace(',','-')
		for i in range(0,24):
			if l3[i]==value:
				val1=l4[i+24]
		response = get('https://www.imdb.com'+val1)
		soup= BeautifulSoup(response.text,'html.parser')
		x=soup.find_all(attrs={'class':'lister-item-header'})
		y=soup.find_all(attrs={'class':'inline-block ratings-imdb-rating'})
		name=[]
		score=[]
		for i in y:
		    score.append(i.strong.text)
		for i in x:
		    name.append(i.a.text)
		name = [x.strip('\n   ') for x in name]
		str1=''
		count=1
		for i in range(0,25):
			names=name[i].replace(' ','_')
			names=names.replace(':','')
			names=names.replace('(','')
			names=names.replace(')','')
			names=names.replace('-','')
			names=names.replace('.','')
			names=names.replace(')','')
			names=names.replace(',',' ')
			names=names.replace('\'','')
			str1=str1+str(count)+". /"+names+" "+score[i]+"\n"
			count+=1
		msg = bot.reply_to(message, str1)
		bot.register_next_step_handler(msg,you_link)
	
@bot.message_handler(commands=['Movies'])
def Movies(message):
	url = 'https://www.rottentomatoes.com/top/'
	response = get(url)
	soup= BeautifulSoup(response.text,'html.parser')
	tab = soup.find('ul', attrs={'class': 'genrelist'})
	pref='https://www.rottentomatoes.com'
	for i in tab.find_all('div'):
	    l1.append(i.text)
	for link in tab.find_all('a'):
	    if link.has_attr('href'):
	        l2.append(pref+link.attrs['href'])
	str1=''
	count=1
	for i in l1:
		i=i.replace(' ','_')
		i=i.replace('&','and')
		str1=str1+str(count)+". /"+i+"\n"
		count+=1
	msg = bot.reply_to(message, str1)
	bot.register_next_step_handler(msg, movie_rec)

def movie_rec(message):
	value= message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(send_welcome)
	else:
		value=value.replace('_',' ')
		value=value.replace('and','&')
		value=value.replace('/','')
		for i in range(0,len(l1)):
			if l1[i]==value:
				val1=l2[i]
		response = get(val1)
		soup= BeautifulSoup(response.text,'html.parser')
		name=[]
		score=[]
		x=soup.find_all(attrs={'class':'unstyled articleLink'})

		for tr in soup.find_all('tr')[1:]:
		    tds=tr.find_all('td')
		    for i in tds:
		        x=i.find(attrs={'class':'unstyled articleLink'})        
		        try:
		            name.append(x.text)
		        except:
		            print("",end='')
		    for i in tds:
		        x=i.find(attrs={'class':'tMeterScore'})
		        try:
		            score.append(x.text)
		        except:
		            print("",end='')
		name = [x.strip('\n   ') for x in name]
		str1=''
		count=1
		for i in range(0,len(name)):
			names=name[i].replace(' ','_')
			names=names.replace(':','')
			names=names.replace('(','')
			names=names.replace(')','')
			names=names.replace('-','')
			names=names.replace('.','')
			names=names.replace(')','')
			names=names.replace(',',' ')
			names=names.replace('\'','')
			str1=str1+str(count)+". /"+names+" "+score[i]+"\n"
			count+=1
		msg = bot.reply_to(message, str1)
		bot.register_next_step_handler(msg,you_link)

def you_link(message):
	value= message.text
	if value=='/Exit':
		msg = bot.reply_to(message,'Well then, Good Bye.\n/Start')
		bot.register_next_step_handler(msg,send_welcome)
	else:
		value=value.replace('_',' ')
		value=value.replace('/',' ')
		url='https://www.youtube.com/results?search_query='+value+" Trailer"
		response=get(url)
		soup=BeautifulSoup(response.text,'html.parser')
		vids = soup.find('a',attrs={'class':'yt-uix-tile-link'})
		tmp = 'https://www.youtube.com' + vids['href']
		msg = bot.reply_to(message,tmp)
		bot.register_next_step_handler(msg,you_link)

bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.polling()