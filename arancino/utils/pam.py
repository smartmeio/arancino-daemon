# Copyright 2017 MDSLAB - University of Messina
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

__author__ = "Nicola Peditto <n.peditto@gmail.com>"

from ctypes import byref
from ctypes import c_char
from ctypes import c_char_p
from ctypes import c_int
from ctypes import c_uint
from ctypes import c_void_p
from ctypes import cast
from ctypes import CDLL
from ctypes import CFUNCTYPE
from ctypes import POINTER
from ctypes import sizeof
from ctypes import Structure
from ctypes.util import find_library

import sys

# LIBC imports
libc = CDLL(find_library("c"))
libpam = CDLL(find_library("pam"))

# CALLOC imports
calloc = libc.calloc
calloc.restype = c_void_p
calloc.argtypes = [c_uint, c_uint]

# STRUP imports
strdup = libc.strdup
strdup.argstypes = [c_char_p]
strdup.restype = POINTER(c_char)

# PAM CONSTANTS
PAM_PROMPT_ECHO_OFF = 1
PAM_PROMPT_ECHO_ON = 2
PAM_ERROR_MSG = 3
PAM_TEXT_INFO = 4
PAM_REINITIALIZE_CRED = 0x0008  # libpam requirement


class PamHandle(Structure):
    """pam_handle_t wrapper"""
    _fields_ = [("handle", c_void_p)]

    def __init__(self):
        Structure.__init__(self)
        self.handle = 0


class PamMsg(Structure):
    """pam_message structure wrapper"""
    _fields_ = [("msg_style", c_int), ("msg", c_char_p), ]

    def __repr__(self):
        return "<PamMsg %i '%s'>" % (self.msg_style, self.msg)


class PamResp(Structure):
    """pam_response structure wrapper"""
    _fields_ = [("resp", c_char_p), ("resp_retcode", c_int), ]

    def __repr__(self):
        return "<PamResp %i '%s'>" % (self.resp_retcode, self.resp)

conv_func = CFUNCTYPE(
    c_int,
    c_int,
    POINTER(POINTER(PamMsg)),
    POINTER(POINTER(PamResp)),
    c_void_p
)


class PamWrapper(Structure):
    """pam_conv structure wrapper"""
    _fields_ = [("conv", conv_func), ("appdata_ptr", c_void_p)]

pamLib_start = libpam.pam_start
pamLib_start.restype = c_int
pamLib_start.argtypes = [
    c_char_p,
    c_char_p,
    POINTER(PamWrapper),
    POINTER(PamHandle)
]

pamLib_authenticate = libpam.pam_authenticate
pamLib_authenticate.restype = c_int
pamLib_authenticate.argtypes = [PamHandle, c_int]

pamLib_setcred = libpam.pam_setcred
pamLib_setcred.restype = c_int
pamLib_setcred.argtypes = [PamHandle, c_int]

pamLib_end = libpam.pam_end
pamLib_end.restype = c_int
pamLib_end.argtypes = [PamHandle, c_int]


def pamAuthentication(
        username, password, service='login', encoding='utf-8', resetcred=True):

    auth_success = None

    if sys.version_info >= (3,):
        if isinstance(username, str):
            username = username.encode(encoding)
        if isinstance(password, str):
            password = password.encode(encoding)
        if isinstance(service, str):
            service = service.encode(encoding)
    else:
        if isinstance(username, unicode):
            username = username.encode(encoding)
        if isinstance(password, unicode):
            password = password.encode(encoding)
        if isinstance(service, unicode):
            service = service.encode(encoding)

    @conv_func
    def prompt_cov_msg(n_messages, messages, p_response, app_data):
        """
        Conversation function that responds to any
        prompt where the echo is off with the supplied password
        """

        addr = calloc(n_messages, sizeof(PamResp))
        p_response[0] = cast(addr, POINTER(PamResp))
        for i in range(n_messages):
            if messages[i].contents.msg_style == PAM_PROMPT_ECHO_OFF:
                pw_copy = strdup(password)
                p_response.contents[i].resp = cast(pw_copy, c_char_p)
                p_response.contents[i].resp_retcode = 0
        return 0

    handle = PamHandle()
    conv = PamWrapper(prompt_cov_msg, 0)
    pamRes = pamLib_start(service, username, byref(conv), byref(handle))

    if pamRes != 0:
        print("Error calling PAM module: " + str(pamRes))
        return False

    pamRes = pamLib_authenticate(handle, 0)
    if pamRes == 0:
        auth_success = True
    else:
        auth_success = False

    # Re-initialize credentials (e.g. for Kerberos users)
    if auth_success and resetcred:
        pamRes = pamLib_setcred(handle, PAM_REINITIALIZE_CRED)

    pamLib_end(handle, pamRes)

    return auth_success
