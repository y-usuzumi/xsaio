from datetime import datetime
from threading import Thread
import xsaio


def _l(s):
    print("[%s] %s" % (datetime.now(), s))


def control(loop):
    print("Hello", end=' ')
    i = 0

    def lyrics():
        nonlocal i
        if i == 0:
            _l("如果有一天")
        elif i == 1:
            _l("我回到从前")
        elif i == 2:
            _l("回到最原始的我")
        elif i == 3:
            _l("你是否会觉得我不错")
        i += 1

    loop.set_interval(lyrics, 1000)
    # loop.set_timeout(u_rock, 5000)
    print("world!")


if __name__ == '__main__':
    loop = xsaio.EPollEventLoop()
    t = Thread(target=control, args=(loop, ))
    t.daemon = True
    t.start()
    loop.run()
