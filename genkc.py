import jwt
import yaml
from uuid import uuid4
import datetime
import sys
import json
import tempfile
from os import system

# Generate a kubernetes configuration from a private key
# Arguments:
# - path to values.yaml
# - path to CA for openunison proxy ingress
# - path to private key
# - number of seconds generated token should be valid

print("loading values.yaml : " + sys.argv[1])

values_yaml = open(sys.argv[1]).read()

values_json = yaml.load(values_yaml)

print("remote tls certificate : " + sys.argv[2])

cmd = "kubectl config set-cluster remote-proxy --server=https://" + values_json["services"]["api_server_host"] + " --certificate-authority=" + sys.argv[2] + " --embed-certs=true"
system(cmd)

cmd = "kubectl config set-context remote-proxy --cluster=remote-proxy --user=" + values_json["services"]["issuer_url"]
system(cmd)





print("loading private key : " + sys.argv[3] )
private_key = open(sys.argv[3]).read()
print("creating jwt")

jwt_claims = {
    'sub': values_json["services"]["issuer_url"],
    'iss': values_json["services"]["issuer_url"],
    'aud':'kubernetes',
    'jti':str(uuid4()),
    'iat':datetime.datetime.utcnow(),
    'exp':datetime.datetime.utcnow() + datetime.timedelta(seconds=int(sys.argv[4])),
    'nbf':datetime.datetime.utcnow() - datetime.timedelta(seconds=60)
}



signed_jwt = jwt.encode(jwt_claims,key=private_key,algorithm='RS256')

cmd = "kubectl config set-credentials " + values_json["services"]["issuer_url"] + " --token=" + signed_jwt.decode("utf-8")
system(cmd)

cmd = "kubectl config use-context remote-proxy"
system(cmd)
