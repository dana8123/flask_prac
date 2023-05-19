from flask import Flask, jsonify, request, Response, Blueprint
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_restx import Api, Resource, fields


def create_app():
    app = Flask(__name__)

    api = Api(app, title="user app", doc="/",
              description="Welcome to the Swagger UI documentation site!")

    api.authorizations = {
        'jwt': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    }

    blueprint = Blueprint('swagger', __name__, url_prefix='/')

    UserApi = api.namespace('Users', description='Users API')

    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # JWT 암호화에 사용되는 시크릿 키 설정
    jwt = JWTManager(app)

    # 가상의 유저 데이터
    users = {'password': 'password1',
             'email': 'user1@example.com', 'username': 'kim'}

    @UserApi.route("/users")
    class Users(Resource):
        def get(self):
            return jsonify(users)

    @UserApi.route('/login')
    @UserApi.doc(params={'username': 'User name', 'password': 'User password'})
    class UserLogin(Resource):
        def post(self):
            params = request.args
            username = params.get('username')
            password = params.get('password')

            if username != users.get("username"):
                return jsonify({"statusCode": 400, "message": '존재하지 않는 유저입니다.'})

            if password != users.get('password'):
                return jsonify({"statusCode": 400, "message": '패스워드가 틀렸습니다.'})

            access_token = create_access_token(identity=username)
            return jsonify({"statusCode": 200, 'access_token': 'Bearer ' + access_token})

    @UserApi.route('/me')
    class UserInfo(Resource):
        @UserApi.doc(security=[{'jwt': []}])
        @jwt_required()
        def get(self):
            current_user = get_jwt_identity()
            print("current user ======== > ", current_user)
            print(users['username'], users['password'])
            return jsonify({"users": current_user, "statusCode": 200})

    api.add_namespace(UserApi)
    app.register_blueprint(blueprint)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
