from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_restx import Api, Resource, fields


def create_app():
    app = Flask(__name__)
    api = Api(app)
    products_api = api.namespace('Products', description='Products API')

    # Set the JWT secret key for encryption
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'
    jwt = JWTManager(app)

    # Virtual product data
    products = [
        {'id': 1, 'name': 'Product 1'},
        {'id': 2, 'name': 'Product 2'},
        {'id': 3, 'name': 'Product 3'},
    ]

    @products_api.route('/products', methods=['GET'])
    class GetProducts(Resource):
        def get(self):
            return jsonify(products), 200

    @products_api.route('/products/<int:product_id>', methods=['GET'])
    class GetProduct(Resource):
        def get(self, product_id):
            product = next(
                (p for p in products if p['id'] == product_id), None)
            if product is None:
                return jsonify({'message': 'Product not found'}), 404

            return jsonify(product), 200

    @products_api.route('/products', methods=['POST'])
    class CreateProduct(Resource):
        @jwt_required()
        def post(self):
            current_user = get_jwt_identity()

            if current_user != 'admin':
                return jsonify({'message': 'Unauthorized'}), 401

            data = request.json
            product_id = len(products) + 1
            product = {'id': product_id, 'name': data['name']}
            products.append(product)

            return jsonify(product), 201

    @app.route('/products/<int:product_id>', methods=['PUT'])
    class UpdateProduct(Resource):
        @jwt_required()
        def put(self, product_id):
            current_user = get_jwt_identity()

            if current_user != 'admin':
                return jsonify({'message': 'Unauthorized'}), 401

            product = next(
                (p for p in products if p['id'] == product_id), None)
            if product is None:
                return jsonify({'message': 'Product not found'}), 404

            data = request.json
            product['name'] = data['name']

            return jsonify(product), 200

    @app.route('/products/<int:product_id>', methods=['DELETE'])
    class DeleteProduct(Resource):
        @jwt_required()
        def delete(self, product_id):
            current_user = get_jwt_identity()

            if current_user != 'admin':
                return jsonify({'message': 'Unauthorized'}), 401

            product = next(
                (p for p in products if p['id'] == product_id), None)
            if product is None:
                return jsonify({'message': 'Product not found'}), 404

            products.remove(product)

            return jsonify({'message': 'Product deleted'}), 200

    return app


app = create_app()

if __name__ == '__main__':
    app.run(port=5001, debug=True)
