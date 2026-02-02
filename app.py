from flask import Flask
from config import Config
from routes import bp


app = Flask(__name__)
app.config.from_object(Config)


app.register_blueprint(bp)


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
