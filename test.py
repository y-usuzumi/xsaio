from datetime import datetime
from threading import Thread
import xsaio
from xsaio.tcp_client import TCPClient


def _p(s):
    print("[%s] %s" % (datetime.now(), s))


def control(loop):
    print("Hello", end=' ')
    i = 0

    def lyrics():
        nonlocal i
        if i == 0:
            _p("如果有一天")
        elif i == 1:
            _p("我回到从前")
        elif i == 2:
            _p("回到最原始的我")
        elif i == 3:
            _p("你是否会觉得我不错")
        i += 1

    loop.set_interval(lyrics, 1000)
    print("world!")
    c = TCPClient()
    c.connect("127.0.0.1", 80)


if __name__ == '__main__':
    xsaio.config(debug=True)
    loop = xsaio.EPollEventLoop()
    t = Thread(target=control, args=(loop,))
    t.daemon = True
    t.start()
    loop.run()
