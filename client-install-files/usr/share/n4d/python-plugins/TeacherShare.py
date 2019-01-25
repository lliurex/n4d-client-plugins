# -*- coding: utf-8 -*-<F12>

import os.path
import base64
import os
import pwd
import multiprocessing
import socket 
import ssl
import shutil

from xmlrpclib import *

class TeacherShare:

	def send_to_teacher_net(self,from_user,to_user,file_path):

		file_path=file_path.encode("utf8")
		#Get ip from user
		s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		s.connect(("server",9779))
		student_ip=s.getsockname()[0]

		server = ServerProxy ("https://server:9779")
		
		try:
			paths=server.get_paths("","TeacherShareManager")
			
		except Exception as e:
			print e
			return False
					
		if to_user in paths:
			path,name,ip,port=paths[to_user]
			path=path.encode("utf8")
			name=name.encode("utf8")
			try:
				src=file_path
				queue=multiprocessing.Queue()
				p=multiprocessing.Process(target=self.copy_file_as_user,args=(src,student_ip,ip,from_user,to_user,False,queue))
				p.start()
				p.join()
	
				if not queue.get():
					return False
				else:
					return True
				
			except Exception as e:
				print e
				return False
	#def send_to_teacher_net
	
	def copy_file_as_user(self,src,from_ip,to_ip,from_user,to_user,delete,queue):
		try:	
			server=ServerProxy("https://"+to_ip+":9779")
			ret=server.grab_file("","TeacherShare",from_user,from_ip,src)
			if ret:
				if delete:
					os.remove(src)
				queue.put(True)
			else:
				queue.put(False)
		except Exception as e:
			print e
			queue.put(False)
	#def copy_file_as_user


	def grab_file(self,from_user,from_ip,src):
		if self.credentials:
			teacher_uid=pwd.getpwnam(self.credentials[0])[2]
			teacher_gid=pwd.getpwnam(self.credentials[0])[3]
			server=ServerProxy("https://localhost:9779")
			if self.credentials:
				try:
					fileName=os.path.basename(src)
					dest=self.shared_path+"/["+from_user+"]_"+fileName
					ret=server.get_file(self.credentials,"ScpManager",from_user,self.credentials[0],self.credentials[1],from_ip,src,dest)
					os.chown(dest,teacher_uid,teacher_gid)
					return True
				except Exception as e:
					print e
					return False
		else:
			print("No credentials found")
			return False

	def register_share_info(self,user,pwd,path):
			self.credentials=(user,pwd)
			self.shared_path=path
	#def register_credentials

#class TeacherFileManager

