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

os.chdir("/home/kalpesh/keycloak-14.0.0/bin")
kcadm("config", "credentials", "--server", "http://localhost:8080/auth", "--realm", "master", "--user", "admin", "--password", "admin" ,"--client", "admin-cli")
kcadm("create", "realms", "-s", "realm=demorealm9", "-s", "enabled=true", "-s", "accessTokenLifespan=2800", "-o")
kcadm("create", "clients", "-r", "demorealm9", "-s", "clientId=my_client", "-s", 'redirectUris=["http://localhost:8080/myapp/*"]')

comm=subprocess.Popen(['/home/kalpesh/keycloak-14.0.0/bin/kcadm.sh','get','clients','-r','demorealm9','-F','id,clientId'],stdout=subprocess.PIPE)
out=subprocess.run(['jq','-r','.[] | select (.clientId == "my_client") | .id'],stdin=comm.stdout,stdout=subprocess.PIPE)
xx1=out.stdout.rstrip()
xx2=repr(xx1)[2:-1]
print(xx2)

w="clients/{}".format(xx2)

kcadm("update", w, "-r", "demorealm9", "-s", "enabled=true", "-s", "serviceAccountsEnabled=true")
x=w+"/client-secret"
print(x)
realm_name='demorealm9'
ans1=subprocess.run(['/home/kalpesh/keycloak-14.0.0/bin/kcadm.sh', 'get', x, '-r', realm_name, '-F', 'value'],stdout=subprocess.PIPE)
print(ans1.stdout.decode("utf-8")[15:51])

client_name = "my_client"
ans0= '{client}:{secret}'.format(client=client_name,secret=ans1.stdout.decode("utf-8")[15:51])
print(ans0)

y="client_secret={}".format(ans1.stdout.decode("utf-8")[15:51])
print(y)

ans2=subprocess.Popen(['curl',"-k", "-v", "-X", "POST", "-H", "Content-Type:application/x-www-form-urlencoded", "-d", "scope=openid", "-d", "grant_type=client_credentials", "-d", "client_id=my_client", "-d", y , "http://localhost:8080/auth/realms/demorealm9/protocol/openid-connect/token"],stdout=subprocess.PIPE)
web_token=subprocess.run(['jq', '-r','.access_token'],stdin=ans2.stdout,stdout=subprocess.PIPE)
answer="{}".format(web_token.stdout.decode("utf-8"))
print(answer)

acc_token= 'token={}'.format(answer)

ans4=subprocess.Popen(['curl',"-k", "-v", "-X", "GET", "-H", "Content-Type: application/x-www-form-urlencoded", "http://localhost:8080/auth/realms/demorealm9/protocol/openid-connect/certs"],stdout=subprocess.PIPE)
ans5=subprocess.run(['jq', '-r', '.keys[].x5c[]'],stdin=ans4.stdout,stdout=subprocess.PIPE)
aa='{}'.format(ans5.stdout.decode("utf-8"))

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
#ans8=subprocess.Popen(["curl", "-k", "-v", "-X", "POST", "-u", ans0, "-d", acc_token, "http://localhost:8080/auth/realms/demorealm9/protocol/openid-connect/token/introspect"],stdout=subprocess.PIPE)
#print(ans8.stdout)
#aud_output = subprocess.run(['jq', '-r', '.aud'],stdin=ans8.stdout,stdout=subprocess.PIPE)
#print(aud_output)
#final_aud_answer = "{}".format(aud_output.stdout.decode("utf-8"))
#print(final_aud_answer)

