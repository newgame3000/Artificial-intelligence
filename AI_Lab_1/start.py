import sys
sys.path.append("./internal")

from internal.tickerGenerator import Generator

gen = Generator()
gen.start()
