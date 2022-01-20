import os
import configparser
import redis


#Author: Enrico Catalfamo <enricocatalfamo@gmail.com>


class TLSecurity:

    RedisContext = True
    r = redis.Redis(host = 'localhost', port = 6380, db = 0)


    def __init__(self, listener, req, client, addr, CertFingerprint):
        self.listener = listener
        self.req = req
        self.client = client
        self.addr = addr
        self.CertFingerprint = CertFingerprint



    def details(self):
        print(self.listener)
        print(self.req)
        print(self.client)
        print(self.addr)
        print(self.CertFingerprint)


    def Authorization(self):

        if self.RedisContext == True:
            rresponse = self.r.hgetall("AuthClient")
            for v in rresponse.values():
                if str(v) == self.CertFingerprint:
                    return 1
            return 0

        else:
            config = configparser.ConfigParser()
            config.read(os.path.join(os.environ.get('ARANCINOCONF'), "arancino.cfg"))
            AuthorizedClients = config.items("TLSecurity")
            for k,v in AuthorizedClients:
                if v == self.CertFingerprint:
                    return 1
            return 0