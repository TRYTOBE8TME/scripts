import subprocess
from io import StringIO
import os
import json
import sys
from pathlib import Path

def git(*args):
    return subprocess.check_call(['git'] + list(args))

def maven(*args):
    return subprocess.check_call(['mvn'] + list(args))

def kcadm(*args,**kwargs):
    return subprocess.run(['./kcadm.sh'] + list(args),**kwargs)

def curl(*args):
    return subprocess.Popen(['curl'] + list(args),stdout=subprocess.PIPE)
'''
git("clone","https://github.com/keycloak/keycloak.git")
os.chdir("keycloak")
#print(os.getcwd())
maven("install","-DskipTestsuite")
maven("install","-Pdistribution")
maven("-Pdistribution","-pl","distribution/server-dist","-am","-Dmaven.test.skip","clean","install")
maven("-f","testsuite/utils/pom.xml","exec:java","-Pkeycloak-server")
'''

#cmd="export PATH=/home/kapandya/keycloak:distribution/server-dist/target/keycloak-12.0.0-SNAPSHOT/bin"
#os.system(cmd)
#process=subprocess.run('/home/kapandya/keycloak/distribution/server-dist/target/keycloak-12.0.0-SNAPSHOT/bin/kcadm.sh',shell=True)
os.chdir("/home/kalpesh/keycloak-14.0.0/bin")
kcadm("config", "credentials", "--server", "http://localhost:8080/auth", "--realm", "master", "--user", "admin", "--password", "admin" ,"--client", "admin-cli")
kcadm("create", "realms", "-s", "realm=demorealm", "-s", "enabled=true", "-s", "accessTokenLifespan=2800", "-o")
kcadm("create", "clients", "-r", "demorealm", "-s", "clientId=my_client", "-s", 'redirectUris=["http://localhost:8080/myapp/*"]')

#comm=kcadm('get','clients','-r','demorealm','-F','id,clientId',stdout=subprocess.PIPE)
#comm=subprocess.run(['/home/kapandya/keycloak-11.0.0/bin/kcadm.sh','get','clients','-r','demorealm','-F','id,clientId'],stdout=subprocess.PIPE)
comm=subprocess.Popen(['/home/kalpesh/keycloak-14.0.0/bin/kcadm.sh','get','clients','-r','demorealm','-F','id,clientId'],stdout=subprocess.PIPE)
#out=subprocess.run(['jq','-r','.[] | select (.clientId == "my_client") | .id'],input=comm.stdout,stdout=subprocess.PIPE)
#xx1=out.stdout.rstrip()
#xx2=repr(xx1)[2:-1]
#print(xx2)
#f.close()
#comm.stdout.close()
#out=subprocess.check_output(['jq','-r','.[] | select (.clientId == "my_client") | .id'],stdin=comm.stdout,encoding="utf-8")
out=subprocess.run(['jq','-r','.[] | select (.clientId == "my_client") | .id'],stdin=comm.stdout,stdout=subprocess.PIPE)
#print(out.communicate()[0])
#print(repr(out.stdout))
#x1=out.communicate()[0].rstrip()
xx1=out.stdout.rstrip()
#print(x1)
#print(xx1)
#xx1=repr(x1)[2:-1]
xx2=repr(xx1)[2:-1]
#print(xx)
print(xx2)
#print(repr(out.stdout)[2:-1])
#print(out.strip())
#print(out["stdout"])
#print(out.stdout)
#print(out.stdout.decode("utf-8"))
#print(out.stdout[0:36])

w="clients/{}".format(xx2)
#print(w.strip())

kcadm("update", w, "-r", "demorealm", "-s", "enabled=true", "-s", "serviceAccountsEnabled=true")
x=w+"/client-secret"
print(x)
#ans1=subprocess.run(['/home/kalpesh/keycloak/distribution/server-dist/target/keycloak-12.0.0-SNAPSHOT/bin/kcadm.sh','get',x,'-r','demorealm','-F','value'],stdout=subprocess.PIPE,universal_newlines=True)
# Request Tokens for credentials
realm_name='demorealm'
ans1=subprocess.run(['/home/kalpesh/keycloak-14.0.0/bin/kcadm.sh', 'get', x, '-r', realm_name, '-F', 'value'],stdout=subprocess.PIPE)
print(ans1.stdout[15:51])

client_name = "my_client"
ans0= '{client}:{secret}'.format(client=client_name,secret=ans1.stdout[15:51])

y="client_secret={}".format(ans1.stdout[15:51])
print(y)

ans2=subprocess.Popen(['curl',"-k", "-v", "-X", "POST", "-H", "Content-Type:application/x-www-form-urlencoded", "-d", "scope=openid", "-d", "grant_type=client_credentials", "-d", "client_id=my_client", "-d", y , "http://localhost:8080/auth/realms/demorealm/protocol/openid-connect/token"],stdout=subprocess.PIPE)
#ans3=subprocess.run(['jq', '.'],stdin=ans2.stdout,stdout=subprocess.PIPE)
#print(ans3)
web_token=subprocess.run(['jq', '-r','.access_token'],stdin=ans2.stdout,stdout=subprocess.PIPE)
answer="{}".format(web_token.stdout.decode("utf-8"))
print(answer)

acc_token= 'token={}'.format(web_token.stdout.decode("utf-8"))

#id_token=subprocess.run(['jq', '-r', '.id_token'],stdin=ans3.stdout,stdout=subprocess.PIPE)
#answer1="{}".format(id_token.stdout.decode("utf-8"))
#print(id_token)

ans4=subprocess.Popen(['curl',"-k", "-v", "-X", "GET", "-H", "Content-Type: application/x-www-form-urlencoded", "http://localhost:8080/auth/realms/demorealm/protocol/openid-connect/certs"],stdout=subprocess.PIPE)
ans5=subprocess.run(['jq', '-r', '.keys[].x5c[]'],stdin=ans4.stdout,stdout=subprocess.PIPE)
aa='{}'.format(ans5.stdout.decode("utf-8"))
#print(aa)

start="-----BEGIN CERTIFICATE-----\n"
end="-----END CERTIFICATE-----"
with open(r'/home/kalpesh/keycloak-14.0.0/bin/certi.crt', 'w+') as f:
    f.write(start)
    f.write(aa)
    f.write(end)
    f.close()

ans6=subprocess.run(['openssl', 'x509', '-in', '/home/kalpesh/keycloak-14.0.0/bin/certi.crt', '-fingerprint', '-noout'],stdout=subprocess.PIPE)
ans7='{}'.format(ans6.stdout.decode("utf-8")[17:76])
print(ans7)
c=""
for i in ans7:
    if(i!=':'):
        c+=i
print(c)
ans8=subprocess.Popen(["curl", "-k", "-v", "-X", "POST", "-u", ans0, "-d", acc_token, "http://localhost:8080/auth/realms/demorealm/protocol/openid-connect/token/introspect"],stdout=subprocess.PIPE)
aud_output = subprocess.run(['jq', '-r', '.aud'],stdin=ans8.stdout,stdout=subprocess.PIPE)
final_aud_answer = "{}".format(aud_output.stdout.decode("utf-8"))
print(final_aud_answer)

