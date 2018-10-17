all: pmake precover pshow

pmake: makepin.py
	cp makepin.py pmake
	chmod a+x pmake

precover: recoverpin.py
	cp recoverpin.py precover
	chmod a+x precover

pshow: showpass.sh
	cp showpass.sh pshow
	chmod a+x pshow