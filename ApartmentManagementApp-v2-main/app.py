from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import logging
from sqlalchemy import exc
from sqlalchemy.orm import joinedload
from Classes.config import configure_app, db
from Classes.Apartment import Apartment
from Classes.MaintenanceRequest import MaintenanceRequest
from Classes.User import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App initialization
app = Flask(__name__)
configure_app(app)
CORS(app, supports_credentials=True, origins="http://localhost:4200", 
     methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])

# Database logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Constants
VALID_STATUSES = ['Pending', 'In Progress', 'Resolved', 'Cancelled', 'Rejected']
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_scheduled_date(date_str):
    """Flexibly parse dates from different formats with timezone support"""
    if not date_str or str(date_str).lower() in ['null', 'none', '']:
        return None
    
    try:
        # Try ISO format first (from Angular Date objects)
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.replace(tzinfo=None)  # Convert to naive datetime for MySQL
        # Try with time (your original format)
        if ':' in date_str:
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        # Try date-only format
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as e:
        logger.error(f"Failed to parse date: {date_str} - Error: {str(e)}")
        return None

def validate_and_normalize_status(status):
    """Validate status and normalize variations to match database ENUM"""
    if not status:
        return None
        
    status = status.strip().title()  # Normalize case
    status_map = {
        'Completed': 'Resolved',
        'Complete': 'Resolved',
        'Finished': 'Resolved',
        'Done': 'Resolved'
    }
    
    normalized_status = status_map.get(status, status)
    
    if normalized_status not in VALID_STATUSES:
        return None
    return normalized_status

# Initialize database
with app.app_context():
    db.create_all()

@app.route('/apartments')
def get_apartments():
    price_min = request.args.get('price_min', type=int)
    price_max = request.args.get('price_max', type=int)
    location = request.args.get('location', type=str)
    area_min = request.args.get('area_min', type=int)
    area_max = request.args.get('area_max', type=int)
    apt_type = request.args.get('type', type=str)

    query = Apartment.query

    if apt_type:
        query = query.filter(Apartment.type.ilike(f'%{apt_type}%'))
    if price_min:
        query = query.filter(Apartment.price >= price_min)
    if price_max:
        query = query.filter(Apartment.price <= price_max)
    if location:
        query = query.filter(Apartment.location.ilike(f'%{location}%'))
    if area_min:
        query = query.filter(Apartment.area >= area_min)
    if area_max:
        query = query.filter(Apartment.area <= area_max)

    apartments = query.all()

    return jsonify([{
        'id': a.id,
        'owner_id': a.owner_id,
        'location': a.location,
        'price': a.price,
        'unit_number': a.unit_number,
        'area': a.area,
        'number_of_rooms': a.number_of_rooms,
        'type': a.type,
        'description': a.description,
        'photos': [f"http://localhost:5000/{p}" for p in a.photos] if a.photos else [],
        'status': a.status,
        'created_at': a.created_at
    } for a in apartments])

@app.route('/apartments/<int:id>', methods=['GET'])
def get_apartment(id):
    apartment = Apartment.query.get(id)
    if not apartment:
        return jsonify({'error': 'Apartment not found'}), 404

    return jsonify({
        'id': apartment.id,
        'owner_id': apartment.owner_id,
        'location': apartment.location,
        'price': apartment.price,
        'unit_number': apartment.unit_number,
        'area': apartment.area,
        'number_of_rooms': apartment.number_of_rooms,
        'type': apartment.type,
        'description': apartment.description,
        'photos': [f"http://localhost:5000/{p}" for p in apartment.photos] if apartment.photos else [],
        'parking_availability': getattr(apartment, 'parking_availability', None),
        'video': getattr(apartment, 'video', None),
        'map_location': getattr(apartment, 'map_location', None),
        'status': apartment.status,
        'created_at': apartment.created_at
    })

@app.route('/api/maintenance-requests', methods=['GET'])
def get_maintenance_requests():
    category = request.args.get('category')
    status = request.args.get('status')
    search_term = request.args.get('searchTerm')
    user_id = request.args.get('user_id', type=int)

    query = MaintenanceRequest.query.options(
        joinedload(MaintenanceRequest.user),
        joinedload(MaintenanceRequest.technician),
        joinedload(MaintenanceRequest.apartment)
    )

    if category:
        query = query.filter(MaintenanceRequest.problem_type.ilike(f'%{category}%'))
    if status:
        query = query.filter(MaintenanceRequest.status.ilike(f'%{status}%'))
    if search_term:
        query = query.filter(MaintenanceRequest.description.ilike(f'%{search_term}%'))
    if user_id is not None:
        query = query.filter(MaintenanceRequest.user_id == user_id)

    requests = query.all()
    return jsonify([r.to_dict() for r in requests])

@app.route('/api/maintenance-requests', methods=['POST'])
def create_maintenance_request():
    user_id = request.form.get('user_id')
    apartment_id = request.form.get('apartment_id')
    technician_id = request.form.get('technician_id') or None
    problem_type = request.form.get('problem_type')
    description = request.form.get('description')
    status = request.form.get('status', 'Pending')

    image_file = request.files.get('image')
    image_path = None

    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(image_path)
        image_path = os.path.relpath(image_path, start='.')

    new_request = MaintenanceRequest(
        user_id=user_id,
        apartment_id=apartment_id,
        technician_id=technician_id,
        problem_type=problem_type,
        description=description,
        status=status,
        images=image_path
    )

    db.session.add(new_request)
    db.session.commit()

    # Return the full request data with relationships
    full_request = MaintenanceRequest.get_with_relations(new_request.id)
    return jsonify({
        'message': 'Maintenance request submitted successfully!',
        'request': full_request.to_dict()
    }), 201

@app.route('/api/maintenance-requests/<int:id>', methods=['PATCH'])
def update_maintenance_request(id):
    logger.info(f"Received PATCH request for maintenance request {id}")
    
    try:
        data = request.get_json()
        if not data:
            logger.error("No data provided in request")
            return jsonify({'error': 'No data provided'}), 400

        # Log incoming data
        logger.info(f"Request data: {data}")

        maintenance_request = MaintenanceRequest.get_with_relations(id)
        if not maintenance_request:
            logger.error(f"Maintenance request {id} not found")
            return jsonify({'error': 'Maintenance request not found'}), 404

        # Log current state
        logger.info(f"Current state - Status: {maintenance_request.status}, Scheduled: {maintenance_request.scheduled_date}")

        # Process status update
        if 'status' in data:
            normalized_status = validate_and_normalize_status(data['status'])
            if not normalized_status:
                error_msg = f'Invalid status. Must be one of: {", ".join(VALID_STATUSES)}'
                logger.error(error_msg)
                return jsonify({'error': error_msg}), 400
            maintenance_request.status = normalized_status
            logger.info(f"Updating status to: {normalized_status}")

        # Process scheduled date update
        if 'scheduled_date' in data:
            parsed_date = parse_scheduled_date(str(data['scheduled_date']))
            if parsed_date is None and data['scheduled_date'] not in [None, '', 'null']:
                error_msg = 'Invalid date format. Use YYYY-MM-DD, YYYY-MM-DD HH:MM:SS, or ISO format'
                logger.error(error_msg)
                return jsonify({'error': error_msg}), 400
            maintenance_request.scheduled_date = parsed_date
            logger.info(f"Updating scheduled_date to: {parsed_date}")

        # Process other fields
        if 'response' in data:
            maintenance_request.response = data['response']
        if 'technician_id' in data:
            maintenance_request.technician_id = data['technician_id']

        db.session.commit()
        logger.info("Transaction committed successfully")

        # Get the updated request with relationships
        updated_request = MaintenanceRequest.get_with_relations(id)
        return jsonify({
            'message': 'Maintenance request updated successfully',
            'request': updated_request.to_dict()
        })

    except exc.SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error updating request {id}: {str(e)}")
        return jsonify({
            'error': 'Database operation failed',
            'details': str(e),
            'solution': 'Check database logs for more information'
        }), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error updating request {id}: {str(e)}")
        return jsonify({
            'error': 'Unexpected server error',
            'details': str(e)
        }), 500

@app.route('/api/technician/<int:technician_id>/requests', methods=['GET'])
def get_requests_for_technician(technician_id):
    requests = MaintenanceRequest.query.options(
        joinedload(MaintenanceRequest.user),
        joinedload(MaintenanceRequest.apartment)
    ).filter_by(technician_id=technician_id).all()
    return jsonify([r.to_dict() for r in requests])

@app.route('/api/technician/<int:technician_id>/requests/pending', methods=['GET'])
def get_pending_requests_for_technician(technician_id):
    requests = MaintenanceRequest.query.options(
        joinedload(MaintenanceRequest.user),
        joinedload(MaintenanceRequest.apartment)
    ).filter_by(technician_id=technician_id, status='Pending').all()
    return jsonify([r.to_dict() for r in requests])

@app.route('/api/maintenance-requests/<int:request_id>', methods=['GET'])
def get_maintenance_request(request_id):
    request = MaintenanceRequest.get_with_relations(request_id)
    if request is None:
        return jsonify({'error': 'Request not found'}), 404
    return jsonify(request.to_dict())

@app.route('/api/technician/<int:technician_id>/stats', methods=['GET'])
def get_technician_stats(technician_id):
    # Count total non-rejected requests
    total_requests = MaintenanceRequest.query.filter(
        MaintenanceRequest.technician_id == technician_id,
        MaintenanceRequest.status != 'Rejected'  # Explicitly exclude rejected
    ).count()

    # Count pending requests (already excludes rejected by status filter)
    pending_requests = MaintenanceRequest.query.filter(
        MaintenanceRequest.technician_id == technician_id,
        MaintenanceRequest.status == 'Pending'
    ).count()

    # Count completed requests (using resolved statuses)
    completed_requests = MaintenanceRequest.query.filter(
        MaintenanceRequest.technician_id == technician_id,
        MaintenanceRequest.status.in_(['Resolved', 'Completed'])
    ).count()

    return jsonify({
        'total': total_requests,
        'pending': pending_requests,
        'completed': completed_requests
    })

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and user.password == password:
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'role': user.role,
                'is_verified': user.is_verified
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

if __name__ == '__main__':
    app.run(debug=True)