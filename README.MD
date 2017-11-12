# 需求
类 Fabric 主机管理程序开发：
1. 运行程序列出主机组或者主机列表
2. 选择指定主机或主机组
3. 选择让主机或者主机组执行命令或者向其传输文件（上传/下载）
4. 充分使用多线程或多进程
5. 不同主机的用户名密码、端口可以不同

#实现思路
- 使用paramiko模块，实现ssh的链接、命令执行和文件传输；
- 使用多线程，来提供用户的体验；

#难点

#执行
bin/inbatch_main.py

#部署环境
1. 必须根据conf/setting.cnf中的虚拟机设置，安装对于的虚拟机，并配置IP和账号信息；
2. 安装paramiko模块；

#测试命令
- 执行命令
brun -g cache_cluster,dev -h Redis-70,Redis-71 -cmd 'df -h'
- 上传
bput -g cache_cluster -l 1.txt -p /tmp/abc.txt
brun -g cache_cluster -cmd 'cat /tmp/abc.txt'
- 下载
bget -g cache_cluster -l abc.txt -p /tmp/abc.txt


#运行截图
看doc下的测试截图.jpg





