from flask import Flask, jsonify

# Error Handling

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def define_error_handlers(app):

    @app.errorhandler(400)
    def handle_bad_request(error):
        return jsonify({
            "success": False, 
            "error": 400, 
            "message": f"bad request: {error.description}"
        }), 400
        
    @app.errorhandler(401)
    def handle_unauthorized(error):
        return jsonify({
            "success": False, 
            "error": 401, 
            "message": "unauthorized"
        }), 401
        
    @app.errorhandler(403)
    def handle_forbidden(error):
        return jsonify({
            "success": False, 
            "error": 403, 
            "message": "forbidden"
        }), 403
            
    @app.errorhandler(404)
    def handle_resource_not_found(self):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found.'
        }), 404
        
    @app.errorhandler(405)
    def handle_method_not_allowed(self):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method not allowed.'
        }), 405
        
        
    @app.errorhandler(422)
    def handle_unprocessable_content(self):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable Content.'
        }), 422        

    @app.errorhandler(500)
    def handle_server_error(error):
        return jsonify({
            "success": False, 
            "error": 500, 
            "message": "Server error."
        }), 500