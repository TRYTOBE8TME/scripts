import os
import subprocess
import datetime
import textwrap
import stat
import time
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

os.mkdir('/home/kalpesh/certificate_files')
os.chmod('/home/kalpesh/certificate_files', mode=stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
root_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"UK"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Oxfordshire"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"Harwell"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Rosalind Franklin Institute"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"RFI CA"),
])
root_cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    root_key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.utcnow()
).not_valid_after(
    datetime.datetime.utcnow() + datetime.timedelta(days=3650)
).add_extension(
    x509.BasicConstraints(ca=True, path_length=None), critical=True
).sign(root_key, hashes.SHA256(), default_backend())

CACERTFILE = '/home/kalpesh/certificate_files/ca_certificate.pem'

with open(CACERTFILE, "wb") as f:
        f.write(root_cert.public_bytes(serialization.Encoding.PEM))

cert_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

KEYFILE = '/home/kalpesh/certificate_files/server_key.pem'

with open(KEYFILE, "wb") as f:
    f.write(cert_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ))

new_subject = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"UK"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Oxfordshire"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"Harwell"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Rosalind Franklin Institute"),
])
cert = x509.CertificateBuilder().subject_name(
    new_subject
).issuer_name(
    root_cert.issuer
).public_key(
    cert_key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.utcnow()
).not_valid_after(
datetime.datetime.utcnow() + datetime.timedelta(days=30)
).add_extension(
    x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
    critical=False,
).sign(root_key, hashes.SHA256(), default_backend())

CERTFILE = '/home/kalpesh/certificate_files/server_certificate.pem'

with open(CERTFILE, "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

#RABBITMQ_CONF_FILE = '/home/kalpesh/certificate_files/rabbitmq.config'

tempdir = '/home/kalpesh/certificate_files'

RABBITMQ_CONF_FILE = os.path.join(tempdir, 'rabbitmq.config')

with open(RABBITMQ_CONF_FILE, "w") as f:
    # use the old style config format to ensure it also runs on older RabbitMQ versions.
    f.write(textwrap.dedent(f'''
        [
            {{rabbit, [
                {{ssl_listeners, [5671]}},
                {{ssl_options, [{{cacertfile,           "{'/home/kalpesh/certificate_files/ca_certificate.pem'}"}},
                                {{certfile,             "{'/home/kalpesh/certificate_files/server_certificate.pem'}"}},
                                {{keyfile,              "{'/home/kalpesh/certificate_files/server_key.pem'}"}},
                                {{verify,               verify_peer}},
                                {{fail_if_no_peer_cert, false}}]}}]}}
        ].
    '''))
#os.environ['RABBITMQ_CONFIG_FILE'] = os.path.splitext(RABBITMQ_CONF_FILE)[0]
#print(os.environ['RABBITMQ_CONFIG_FILE'])
#subprocess.call(['sudo', 'rabbitmqctl', 'stop'])
#time.sleep(5)
#subprocess.Popen(['sudo', '--preserve-env=RABBITMQ_CONFIG_FILE', 'rabbitmq-server'])
#time.sleep(5)
#print(os.environ['RABBITMQ_CONFIG_FILE'])
