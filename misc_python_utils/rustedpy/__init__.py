from beartype import BeartypeConf, BeartypeStrategy
from beartype.claw import beartype_this_package

beartype_this_package(conf=BeartypeConf(strategy=BeartypeStrategy.O0))
