# -*- coding: utf-8 -*-
import ftplib,os,sqlite3
import ftputil
# from Protect import  DoLock

DEBUG=False

if  DEBUG:
    EXAMPLE_PORT = 21000
    HOST="192.168.4.66"
else:
    EXAMPLE_PORT = 21
    HOST = "192.168.4.66"
    # DoLock()

USER="user"
PASS="123"

HOME_PATH="/media/sda/voice"
INFO_DB=os.path.join( os.getcwd(),"0.db")

class InfoDB(object):
    def __init__(self,db_name=""):
        self.db_name=db_name
        self.createTable()

    def createTable( self):
        if not  os.path.isfile( self.db_name) :
            with open(self.db_name,"w") as f:
                f.close()
        try:
            conn = sqlite3.connect( self.db_name )
            # print "Opened database successfully"
            conn.execute('''CREATE TABLE  IF NOT EXISTS  info
                           (
                           file_path_name  CHAR(2000) PRIMARY KEY     NOT NULL,

                           type       CHAR(100) NULL,
                           size       CHAR(100)   NULL,
                           modify     CHAR(100) NULL);''')

            conn.execute('''CREATE TABLE  IF NOT EXISTS  info_tmp
                           (
                           file_path_name  CHAR(2000) PRIMARY KEY     NOT NULL,

                           type       CHAR(100) NULL,
                           size       CHAR(100)   NULL,
                           modify     CHAR(100) NULL);''')

            conn.commit()
            conn.close()
            return  True,""
        except Exception as e:
            return  False ,e

    def save_to_db(self ,info_list=[]):
        conn = sqlite3.connect(self.db_name)

        for index, tmp in enumerate(info_list):
            for k, v in tmp.items():
                # for pos, t in enumerate(tmp):
                if isinstance(v, str):
                    # t_list.append(v.decode("utf-8"))
                    tmp[k] = v.decode("utf-8")
            info_list[index] = (tmp["file_path_name"], tmp["type"], tmp["size"], tmp["modify"])

        conn.executemany("INSERT OR REPLACE INTO info_tmp ( file_path_name,type,size,modify) VALUES (?,?,?,?)", info_list)
        conn.commit()

        sql = '''
        SELECT   a.file_path_name,a.type,a.size,a.modify
        FROM     info_tmp  a
        LEFT OUTER  join info  b
        on    a.file_path_name = b.file_path_name and  a.modify = b.modify and a.type=b.type and a.size=b.size
        where b.file_path_name is null
        '''
        cursor = conn.execute(sql)
        rst = cursor.fetchall()
        conn.executemany("INSERT OR REPLACE INTO info ( file_path_name,type,size,modify) VALUES (?,?,?,?)", rst)
        conn.commit()

        conn.execute("delete from info_tmp ")
        conn.commit()
        conn.close()
        return  rst

class MySession(ftplib.FTP):
    def __init__(self, host, userid, password, port):
        """Act like ftplib.FTP's constructor but connect to other port."""
        ftplib.FTP.__init__(self)
        self.connect(host, port)
        self.login(userid, password)

class FTPSync(object):
    def __init__(self,HOME_PATH=""):

        # try not to use MySession() as factory, - use the class itself
        self.host  = ftputil.FTPHost(HOST, USER, PASS, port=EXAMPLE_PORT, session_factory=MySession)
        print self.host.curdir
        if DEBUG:
            os.chdir('c:\data')  # 本地下载目录
        else:
            os.chdir('c:\data')  # 本地下载目录
        self.HOME_PATH=HOME_PATH
        self.host.chdir( HOME_PATH)
        self.DB = InfoDB(INFO_DB)


    def walk_new(self, next_dir):
        print 'Walking to', next_dir
        self.host.chdir(next_dir)
        try:
            os.mkdir(next_dir)
        except OSError:
            pass
        os.chdir(next_dir)
        ftp_curr_dir = self.host.getcwd()
        local_curr_dir = os.getcwd()
        files, dirs = self.get_dirs_files(ftp_curr_dir)
        print "FILES: ", files
        print "DIRS: ", dirs
        for f in files:
            print next_dir, ':', f
            self.host.download(f, f)  # remote, local, binary mode
        for d in dirs:
            os.chdir(local_curr_dir)
            self.host.chdir(ftp_curr_dir)
            self.walk_new(d)


    def get_dirs_files(self, ftp_curr_dir=""):
        u''' 得到当前目录和文件, 放入dir_res列表 '''
        # dir_res = []
        # self.conn.dir('.', dir_res.append)
        names = self.host.listdir(".")
        files=[]
        dirs=[]
        for name in names:
            if self.host.path.isfile(name):  # 如果是文件，判断文件的属性
                files.append(name)
            elif self.host.path.isdir(name):  # 如果是目录，跳转至目录
                dirs.append(name)

        info_list=[]
        for  f in  files:
            print "f=",f
            # stat_result1 = StatResult(st_mode=33188, st_ino=None, st_dev=None, st_nlink=1, st_uid=u'hdeng',
            #                           st_gid=u'staff', st_size=5819, st_atime=None, st_mtime=1471482540.0,
            #                           st_ctime=None)
            StatResult=self.host.stat( f )
            print  StatResult
            # f_time_l = self.host.stat( f ).split(",")
            # # print  f_time_l
            #
            info_dic={}
            # for  item in  f_time_l:
            #     item=item.strip()
            #     if  item.startswith("st_dev="):
            #         info_dic["type"]=item.split("=")[1].strip()
            #     elif item.startswith("st_size="):
            #         info_dic["size"] = item.split("=")[1].strip()
            #     elif item.startswith("st_mtime="):
            #         info_dic["modify"] = item.split("=")[1].strip()
            info_dic["type"] = str( StatResult[0])
            info_dic["size"] =str( StatResult[6])
            info_dic["modify"]=str( StatResult[8])
            info_dic["file_path_name"] = ftp_curr_dir + "/" + f
            print info_dic.__str__()

            info_list.append(info_dic)

        if  info_list:
            rst=self.DB.save_to_db(info_list)
            files=[  os.path.basename( r[0] ) for r in rst]
            # print  files

        return (files, dirs)

    def run(self):
        self.walk_new('.')


def main( _dir=""):
    f = FTPSync( _dir )
    f.run( )

if __name__ == '__main__':
    main( HOME_PATH )

# # make a new directory and copy a remote file into it
# host.mkdir('newdir')
# source = host.file('index.html', 'r')         # file-like object
# target = host.file('newdir/index.html', 'w')  # file-like object
# host.copyfileobj(source, target)  # similar to shutil.copyfileobj
# source.close()
# target.close()
