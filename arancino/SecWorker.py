from gunicorn.workers.sync import SyncWorker
from OpenSSL import crypto
from arancino.Authorization.TLSecurity import TLSecurity

#Author: Enrico Catalfamo <enricocatalfamo@gmail.com>

class CustomWorker(SyncWorker):
    def handle_request(self, listener, req, client, addr):

        bincert = client.getpeercert(binary_form = True)
        certfp = crypto.load_certificate(crypto.FILETYPE_ASN1, bincert).digest("sha256")
        certfp = str(certfp)
        SecureConn = TLSecurity(listener, req, client, addr, certfp)

        if 'upload' in SecureConn.req.path:
            Auth = SecureConn.Authorization()
            if Auth == 0:
                del(SecureConn)
                raise Exception('Client Not Authorized.\n')
       
        super(CustomWorker, self).handle_request(listener, req, client, addr)
        del(SecureConn)