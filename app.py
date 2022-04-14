from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from resources.hotel import Hoteis, Hotel
from resources.usuario import User, UserLogin, UserLogout, UserRefresh, UserRegister
from models.blacklist import TokenBlocklist, REFRESH_TOKEN, ACCESS_EXPIRES
from sql_alchemy import banco


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = "super-secret"
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = REFRESH_TOKEN
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES


api = Api(app)
jwt = JWTManager(app)


@app.before_first_request
def cria_banco():
    banco.create_all()


# Callback function to check if a JWT exists in the database blocklist
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = banco.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    return token is not None


api.add_resource(Hoteis, '/hoteis')
api.add_resource(Hotel, '/hoteis/<string:hotel_id>')
api.add_resource(User, '/usuarios/<int:user_id>')
api.add_resource(UserRegister, '/cadastro')
api.add_resource(UserLogin, '/login')
api.add_resource(UserRefresh, '/refresh')
api.add_resource(UserLogout, '/logout')


if __name__ == '__main__':
    banco.init_app(app)
    app.run(debug=True)

# http://127.0.0.1:5000/hoteis
