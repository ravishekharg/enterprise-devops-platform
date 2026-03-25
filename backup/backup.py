
import subprocess, datetime
import hashlib

date = datetime.datetime.now().strftime("%Y%m%d")

databases = ["users","orders","payments"]

for db in databases:
    subprocess.run(["mysqldump","-u","root",db,"-r",f"/backup/{db}_{date}.sql"])

def checksum(file):
    h = hashlib.md5()
    with open(file,'rb') as f:
        h.update(f.read())
    return h.hexdigest()