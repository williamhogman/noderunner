from nose.tools import eq_, ok_

from noderunner import crypto

_msg = "F0" * 32
_msg2 = "0F" * 32

_s = "secret"
_s2 = "secret2"

def test_valid_sign():
    sign1 = crypto.sign_challenge(_s, _msg)
    sign2 = crypto.sign_challenge(_s, _msg)    
    eq_(sign1, sign2)

def test_invalid_signature():
    sign1 = crypto.sign_challenge(_s, _msg)
    sign2 = crypto.sign_challenge(_s, _msg2)

    ok_(sign1 != sign2)

def test_different_secrets():
    sign1 = crypto.sign_challenge(_s, _msg)
    sign2 = crypto.sign_challenge(_s2, _msg)

    ok_(sign1 != sign2)
