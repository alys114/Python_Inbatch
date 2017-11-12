# Author: Vincent.chan
# Blog: http://blog.alys114.com

import os
import re
import paramiko
import threading
# import common
from .common import *

class ssh_host():
	def __init__(self,host,ip,port,user,password):
		self.host = host
		self.ip = ip
		self.port = port
		self.user = user
		self.password = password

class batchProxy:
	'''
	批量管理的代理类
	'''
	def displayTree(self):
		'''
		加载分组和主机的树
		:return:
		'''
		group_names = ReadConfig('groupInfo', 'name')
		for g in group_names.split(','):
			print('-', g)
			host_names = ReadConfig(g, 'host_list')
			for h in host_names.split(','):
				print(' |--', h)

	def help(self,detail=False):
		'''
		显示帮助文档
		:param detail:
		:return:
		'''
		menu = []
		menu.append('操作指南'.center(50, '-'))
		menu.append("-执行命令的语法：brun -g g1,g2 -h h1,h2 -cmd 'df -h'")
		menu.append("-上传文件的语法：bput -g g1,g2 -h h1,h2 -l localfile -p remotefile")
		menu.append("-下载文件的语法：bget -g g1,g2 -h h1,h2 -l localfile -p remotefile")
		if detail:
			menu.append('参数说明'.center(50, '-'))
			menu.append("	-g 组名，例如cache_cluster")
			menu.append("	-h 主机名，例如Redis-70")
			menu.append("	-l 本地文件")
			menu.append("	-p 远程文件")

		menuDisplay(os.linesep.join(menu))

	def brun(self,*args):
		# 处理远程命令
		cmd_str = args[0]
		m = re.search("'.*'",cmd_str)
		remote_cmd = ''
		if m is not None:
			remote_cmd = m.group()
			index = int(cmd_str.index(remote_cmd))
			cmd_str = cmd_str[0:index]
		parm_list = cmd_str.split()
		# 获取远程机器的连接信息
		remote_conn_info = self.get_remote_info(parm_list)
		remote_cmd = remote_cmd.replace("'", "")

		## 多线程处理
		thread_list = []
		for r in remote_conn_info:
			# self.run_cmd_pwd(remote_cmd.replace("'",""),r)
			t = threading.Thread(target=self.run_cmd_pwd,args=(remote_cmd,r,))
			thread_list.append(t)
			# t.daemon = True
			t.start()

		for t in thread_list:
			t.join()

	def get_remote_info(self,*args):
		parm_list = args[0]
		# 1.获取主机列表
		host_list = []
		tmp_index = -1
		if parm_list.__contains__('-g'):
			tmp_index = int(parm_list.index('-g'))
			if tmp_index > -1:
				g_name = parm_list[tmp_index+1]
				# print(g_name)
				for g in g_name.split(','):
					for n in ReadConfig(g,'host_list').strip().split(','):
						host_list.append(n)
		if parm_list.__contains__('-h'):
			tmp_index = int(parm_list.index('-h'))
			if tmp_index > -1:
				host_name = parm_list[tmp_index + 1]
				for h in host_name.split(','):
					if host_list.__contains__(h):pass
					else:
						host_list.append(h)

		# 2.获取主机连接信息
		host_info = []
		for host in host_list:
			p_ip = ReadConfig(host,'ip')
			p_port = int(ReadConfig(host, 'port'))
			p_user = ReadConfig(host, 'user')
			p_password = ReadConfig(host, 'password')
			h = ssh_host(host,p_ip,p_port,p_user,p_password)
			host_info.append(h)
		return host_info

	def bget(self,*args):
		self.sftp(args[0], 'get')

	def sftp(self,*args):
		'''
		封装对文件上传和下载的处理
		:param args:
		:return:
		'''
		cmd_str = args[0]
		action_name = args[1]
		parm_list = cmd_str.split()
		# 获取远程机器的连接信息
		remote_conn_info = self.get_remote_info(parm_list)
		# 获取文件信息
		local_file = ''
		remote_file = ''
		tmp_index = parm_list.index('-l')
		if tmp_index > -1:
			local_file = parm_list[tmp_index + 1]
		tmp_index = parm_list.index('-p')
		if tmp_index > -1:
			remote_file = parm_list[tmp_index + 1]


		## 多线程处理
		thread_list = []
		for r in remote_conn_info:
			# self.tran_file_pwd(r,local_file,remote_file,action_name)

			t = threading.Thread(target=self.tran_file_pwd, args=(r,local_file,remote_file,action_name))
			thread_list.append(t)
			# t.daemon = True
			t.start()

		for t in thread_list:
			t.join()


	def bput(self,*args):
		self.sftp(args[0],'put')

	def interactive(self):
		'''
		命令响应程序
		:return:
		'''
		while True:
			cmd_input = input('>>').strip()
		# cmd_input = "brun -g cache_cluster,dev -h Redis-70,Redis-71 -cmd 'df -h'"
		# cmd_input = "bput -g cache_cluster  -l 1.txt -p /tmp/1.txt"
		# cmd_input = "bget -g cache_cluster -l 1.txt -p /tmp/1.txt"
			if cmd_input is not None:
				# 反射
				cmd = cmd_input.strip().split()[0]
				if hasattr(self,cmd):
					func = getattr(self,cmd)
					func(cmd_input)

	def run_cmd_pwd(self,cmd,remote_info):
		'''
		远程登录执行命令（只能执行一次性命令，不能执行类似top、vim命令）
		类似于ssh
		:return:
		'''
		# 创建SSH对象
		ssh = paramiko.SSHClient()
		# 允许链接不在know_hosts文件中的主机
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		# 链接服务器
		ssh.connect(remote_info.ip, remote_info.port, username=remote_info.user, password=remote_info.password)

		# 执行命令
		stdin, stdout, stderr = ssh.exec_command(cmd)

		# 获取命令结果
		if stdout is not None:
			result = stdout.read()
		else:
			result = stderr.read()

		print(('[%s]执行结果'%remote_info.host).center(30,'-'))
		print(result.decode())

		# 关闭
		ssh.close()

	def tran_file_pwd(self,remote_info,local_file,remote_file,action='put'):
		'''
		传输文件，类似scp
		:return:
		'''
		# 创建实例
		transport = paramiko.Transport((remote_info.ip,remote_info.port))
		# 链接
		transport.connect(username=remote_info.user, password=remote_info.password)
		sftp = paramiko.SFTPClient.from_transport(transport)
		if action=='put':
			# 将本地文件上传
			sftp.put(local_file, remote_file)
			print('文件[%s]上传[%s]成功'%(local_file,remote_info.host))
		if action=='get':
			if local_file is None:
				local_file = os.path.basename(remote_file)
			local_file = os.path.dirname(os.path.abspath(__file__)) + os.sep + remote_info.host + '_' + local_file


			# 将服务器文件下载
			sftp.get(remote_file,local_file)
			print('文件[%s]下载到[%s]成功' % (remote_file,local_file))
		# 关闭链接
		transport.close()


def main():
	ssh = batchProxy()
	# 加载分组和主机的树
	ssh.displayTree()
	# 加载命令菜单
	ssh.help()
	# 命令处理
	ssh.interactive()




if __name__ == '__main__':
	main()