from app.app import app, init_app
from app.constantes import DEBUG

if __name__ == "__main__":
    init_app()
    app.run(debug=DEBUG)
