from datetime import datetime
from datetime import timedelta
from datetime import timezone

from flask_restful import Resource, reqparse
from models.usuario import UserModel
from flask import jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from models.blacklist import TokenBlocklist
from sql_alchemy import banco


atributos = reqparse.RequestParser()
atributos.add_argument('login', type=str, required=True, help="The field 'login' cannot be left blank.")
atributos.add_argument('senha', type=str, required=True, help="The field 'senha' cannot be left blank.")


class User(Resource):
    # /usuarios/{user_id}
    @staticmethod
    def get(user_id):
        if user_id == 0:
            return {'users': [user.json() for user in UserModel.query.all()]}
        else:
            user = UserModel.find_user(user_id)
            if user:
                return user.json()

        return {'message': 'User not found.'}, 404

    @jwt_required()
    def delete(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            user.delete_user()
            return {'message': 'User deleted.'}
        return {'message': 'User not found.'}, 404


class UserRegister(Resource):
    # /cadastro
    @staticmethod
    def post():
        dados = atributos.parse_args()

        if UserModel.find_by_login(dados['login']):
            return {"message": "The login '{}' already exists.".format(dados['login'])}

        user = UserModel(**dados)
        user.save_user()
        return {'message': 'User created successfully!'}, 201  # Created


class UserLogin(Resource):

    def strings_equal(s1, s2):
        if len(s1) != len(s2):
            return False
        for i in range(len(s1)):
            if s1[i] != s2[i]:
                return False
        return True

    @classmethod
    def post(cls):
        dados = atributos.parse_args()

        user = UserModel.find_by_login(dados['login'])

        if user and cls.strings_equal(user.senha, dados['senha']):  # funcao safe_str_cmp() do python
            token_de_acesso = create_access_token(identity=user.user_id)
            refresh_token = create_refresh_token(identity=user.user_id)
            return {'access_token': token_de_acesso, 'refresh_token': refresh_token}, 200
        return {'message': 'The username or password is incorrect.'}, 401  # Unauthorized


class UserLogout(Resource):

    @jwt_required()
    def delete(self):
        jti = get_jwt()["jti"]
        now = datetime.now(timezone.utc)
        banco.session.add(TokenBlocklist(jti=jti, created_at=now))
        banco.session.commit()
        return {'message': 'Logged out successfully!'}


class UserRefresh(Resource):

    @jwt_required()
    def post(self):
        identity = get_jwt_identity()
        print('user', identity)
        access_token = create_access_token(identity=identity, fresh=False)
        return {'access_token': access_token}, 200
