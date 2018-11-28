"""

	Title:	run.py
    Pkg:    alpinklubben
	Date:	02.11.2018
	Author:	Eskil Uhlving Larsen

"""

from alpinklubben import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)  # run app in debugging mode
