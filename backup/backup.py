
import subprocess, datetime

date = datetime.datetime.now().strftime("%Y%m%d")

databases = ["users","orders","payments"]

for db in databases:
    subprocess.run(["mysqldump","-u","root",db,"-r",f"/backup/{db}_{date}.sql"])
