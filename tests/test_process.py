from nose.tools import eq_
from mock import patch, Mock, sentinel

from noderunner.process import open_process


@patch("subprocess.Popen", return_value=sentinel.proc)
def test_open_process(p):
    ret = open_process(sentinel.fd,
                       sentinel.secret,
                       nodepath=sentinel.node_path)

    eq_(ret, sentinel.proc)

    p.assert_called_once()
