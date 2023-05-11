from sign_package import app
from sign_package import db

db.create_all()


if __name__ == '__main__':
	app.run(debug=True)
