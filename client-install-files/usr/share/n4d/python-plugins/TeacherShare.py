# -*- coding: utf-8 -*-<F12>

import os.path
import os
import pwd
import multiprocessing
import socket 
import ssl
import xmlrpc.client

import n4d.responses


class TeacherShare:

	QUEUE_ERROR=-5
	SEND_TO_TEACHER_ERROR=-10
	GRAB_FILE_ERROR=-15
	CREDENTIALS_ERROR=-20
	
	def __init__(self):
		
		self.credentials=None
		
	#def init

	def send_to_teacher_net(self,from_user,to_user,file_path):

		file_path=file_path.encode("utf8")
		
		#Get ip from user
		s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		s.connect(("server",9779))
		student_ip=s.getsockname()[0]
		
		c=ssl._create_unverified_context()
		server = xmlrpc.client.ServerProxy ("https://server:9779",context=c)
		
		try:
			ret=server.get_paths("","TeacherShareManager")
			if ret["status"]==0:
				paths=ret["return"]
			else:
				print(ret["msg"])
				return n4d.responses.build_failed_call_response(ret["msg"])
		except Exception as e:
			return n4d.responses.build_failed_call_response(str(e))
					
		if to_user in paths:
			path,name,ip,port=paths[to_user]
			#path=path.encode("utf8")
			#name=name.encode("utf8")
			try:
				src=file_path.decode("utf-8")
				queue=multiprocessing.Queue()
				p=multiprocessing.Process(target=self.copy_file_as_user,args=(src,student_ip,ip,from_user,to_user,False,queue))
				p.start()
				p.join()
				if not queue.get():
					return n4d.responses.build_failed_call_response()
				else:
					return n4d.responses.build_successful_call_response(TeacherShare.QUEUE_ERROR)
				
			except Exception as e:
				print(e)
				return n4d.responses.build_failed_call_response(TeacherShare.SEND_TO_TEACHER_ERROR,str(e))
				
	#def send_to_teacher_net
	
	def copy_file_as_user(self,src,from_ip,to_ip,from_user,to_user,delete,queue):
		
		try:	
			#server=ServerProxy("https://"+to_ip+":9779")
			context=ssl._create_unverified_context()
			server=xmlrpc.client.ServerProxy("https://"+to_ip+":9779",context=context)
			ret=server.grab_file("","TeacherShare",from_user,from_ip,src)
			if ret["status"]==0 and ret["return"]:
				if delete:
					os.remove(src)
				queue.put(True)
			else:
				queue.put(False)
		except Exception as e:
			print(e)
			queue.put(False)
			
	#def copy_file_as_user


	def grab_file(self,from_user,from_ip,src):
		
		if self.credentials:
			teacher_uid=pwd.getpwnam(self.credentials[0])[2]
			teacher_gid=pwd.getpwnam(self.credentials[0])[3]
			#server=ServerProxy("https://localhost:9779")
			context=ssl._create_unverified_context()
			server=xmlrpc.client.ServerProxy("https://localhost:9779",context=context)
			if self.credentials:
				try:
					fileName=os.path.basename(src)
					dest=self.shared_path+"/["+from_user+"]_"+fileName
					ret=server.get_file(self.credentials,"ScpManager",from_user,self.credentials[0],self.credentials[1],from_ip,src,dest)
					if ret["status"]==0:
						os.chown(dest,teacher_uid,teacher_gid)
						return n4d.responses.build_successful_call_response()
					else:
						print(ret["msg"])
						e=Exception(ret["msg"])
						raise e
				except Exception as e:
					print(e)
					return n4d.responses.build_failed_call_response(TeacherShare.GRAB_FILE_ERROR,str(e))
		else:
			print("No credentials found")
			return n4d.responses.build_failed_call_response(TeacherShare.CREDENTIALS_ERROR,str(e))
			
	#def grab_file

	def register_share_info(self,user,pwd,path):
		
			self.credentials=(user,pwd)
			self.shared_path=path
			return n4d.responses.build_successful_call_response()
			
	#def register_credentials

#class TeacherFileManager

