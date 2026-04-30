# church-attendance-management-system
A Backend API designed to help church track and manage membership and attendance status with face recognition AI, robust reporting, analytics, and communication features.

## Installation and Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/otumuyen-gospel/church-attendance-management-system.git
   cd church-attendance-management-system
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r apis/requirements.txt
   ```

3. **Configure environment**:
   - Set up your database in `apis/settings.py`.
   - Configure email and SMS services using the setup guides:
     - [Face Recognition Setup](FACE_RECOGNITION_SETUP.md)
     - [Email Setup](apis/EMAIL_SETUP.md)
     - [SMS Setup](apis/SMS_SETUP_SUMMARY.md)
     - [Twilio SMS Setup](apis/TWILIO_SMS_SETUP.md)

4. **Install API documentation dependencies**:
   ```bash
   cd apis
   pip install -r requirements.txt
   ```

5. **Run migrations** (if needed):
   ```bash
   python manage.py migrate
   ```

6. **Start the server**:
   ```bash
   python manage.py runserver
   ```

7. **Access API documentation**:
   - Swagger UI: `http://localhost:8000/api/schema/swagger-ui/`
   - ReDoc: `http://localhost:8000/api/schema/redoc/`

## Authentication

Most endpoints require authentication. Use the `/auth/` endpoints to obtain access tokens:

1. **Register/Login**: Use `/auth/register/` or `/auth/login/` to get `access` and `refresh` tokens.
2. **Include in requests**: Add the `Authorization` header:
   ```
   Authorization: Bearer <access_token>
   ```
3. **Refresh tokens**: Use `/auth/refresh/` with the `refresh` token to get a new `access` token.

## Data Models Overview

- **Church**: Represents church organizations.
- **Person**: Individual members with contact info.
- **Household**: Family units containing multiple persons.
- **Membership**: Tracks membership status and types.
- **Attendance**: Records attendance for services.
- **Faces**: Stores face recognition data for persons.
- **Leadership**: Church leadership roles and assignments.
- **Ministries/Services**: Church ministries and service schedules.
- **Messages**: Communication logs (SMS/Email).
- **Reports/Analytics**: Generated reports and analytics data.

## Error Handling

Common error responses:

- `400 Bad Request`: Invalid request data.
- `401 Unauthorized`: Missing or invalid authentication.
- `403 Forbidden`: Insufficient permissions.
- `404 Not Found`: Resource not found.
- `500 Internal Server Error`: Server error.

Example error response:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

## Usage Examples

### Complete Workflow: Register Member and Mark Attendance

1. **Register a new person**:
   ```http
   POST /person/new-person/
   Authorization: Bearer <token>
   Content-Type: application/json

   {
     "first_name": "Jane",
     "last_name": "Doe",
     "email": "jane@example.com"
   }
   ```

2. **Upload face for recognition**:
   ```http
   POST /faces/upload-face/
   Authorization: Bearer <token>
   Content-Type: application/json

   {
     "person_id": 15,
     "image": "base64_encoded_image_data"
   }
   ```

3. **Mark attendance manually**:
   ```http
   POST /attendance/mark-attendance/
   Authorization: Bearer <token>
   Content-Type: application/json

   {
     "person_id": 15,
     "status": "present"
   }
   ```

4. **Or mark attendance via face recognition and automatically capture attendance**:
   ```http
   POST /faces/recognize-face/
   Authorization: Bearer <token>
   Content-Type: application/json

   {
     "image": "base64_encoded_live_image_data"
   }
   ```
   *Response*: `{"recognized_person":"Jane Doe","confidence":0.92}`
   
   Then automatically mark attendance:
   ```http
   POST /attendance/mark-attendance/
   Authorization: Bearer <token>
   Content-Type: application/json

   {
     "person_id": 15,  // From recognition result
     "status": "present"
   }
   ```

5. **View attendance report**:
   ```http
   GET /report/attendance-report/
   Authorization: Bearer <token>
   ```

## API Documentation Access

The API uses OpenAPI 3.0 specification and provides interactive documentation:

- **Swagger UI**: `GET /api/schema/swagger-ui/` — Interactive API documentation
- **ReDoc**: `GET /api/schema/redoc/` — Alternative documentation viewer
- **OpenAPI Schema**: `GET /api/schema/` — Raw OpenAPI JSON schema

These endpoints are automatically generated from your Django REST Framework views using drf-spectacular.

## API Documentation

All Django API endpoints are defined in the `apis` project and the included app URL configurations. The base URL is the project root; each app adds its own prefix.

### API Base Routes
- `GET /admin/` — Django admin interface
- `GET /church/` — Church management endpoints
- `GET /household/` — Household management endpoints
- `GET /role/` — Role management endpoints(create a role and add neccessary permissions)
- `GET /permissions/` — Permission management endpoints
- `GET /capturemethod/` — Capture method endpoints
- `GET /membership/` — Membership management endpoints
- `GET /ministries/` — Ministries management endpoints
- `GET /services/` — Service management endpoints
- `GET /person/` — Person management endpoints
- `GET /contact/` — Contact management endpoints
- `GET /leadership/` — Leadership management endpoints
- `GET /attendance/` — Attendance management endpoints
- `GET /faces/` — Face recognition endpoints
- `GET /user/` — User management endpoints
- `GET /auth/` — Authentication and login endpoints
- `GET /analytics/` — Analytics endpoints
- `GET /report/` — Reporting endpoints
- `GET /message/` — Messaging endpoints

---

## Structured Endpoint Reference

### `/church/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/churches-lists/` | List churches | none | `[{"id":1,"name":"First Assembly","location":"Main Street"}]` |
| POST | `/new-church/` | Create a church | `{"name":"...","location":"...","phone":"..."}` | `{"id":12,"name":"...","location":"..."}` |
| DELETE | `/remove-church/<int:id>/` | Delete church by ID | none | `{"detail":"Church deleted"}` |
| PUT/PATCH | `/modify-church/<int:id>/` | Update church by ID | `{"name":"...","location":"..."}` | `{"id":12,"name":"...","location":"..."}` |

### `/household/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/households-lists/` | List households | none | `[{"id":1,"head_name":"John Doe","members":4}]` |
| POST | `/new-household/` | Create household | `{"head_name":"...","address":"..."}` | `{"id":7,"head_name":"..."}` |
| DELETE | `/remove-household/<int:id>/` | Delete household by ID | none | `{"detail":"Household deleted"}` |
| PUT/PATCH | `/modify-household/<int:id>/` | Update household by ID | `{"address":"..."}` | `{"id":7,"head_name":"..."}` |

### `/role/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/list-roles/` | List roles | none | `[{"id":1,"name":"Administrator"}]` |
| POST | `/new-role/` | Create a role | `{"name":"..."}` | `{"id":5,"name":"..."}` |
| DELETE | `/remove-role/<int:id>/` | Delete role by ID | none | `{"detail":"Role deleted"}` |
| PUT/PATCH | `/modify-role/<int:id>/` | Update role by ID | `{"name":"..."}` | `{"id":5,"name":"..."}` |

### `/permissions/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/all-permissions/` | List permissions | none | `[{"id":1,"codename":"view_user"}]` |
| POST | `/generate-all-permissions/` | Create/update permissions | none | `{"detail":"Permissions generated"}` |

### `/capturemethod/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/capture-methods-lists/` | List capture methods | none | `[{"id":1,"name":"Face"}]` |
| POST | `/new-capture-method/` | Create capture method | `{"name":"..."}` | `{"id":2,"name":"..."}` |
| DELETE | `/remove-capture-method/<int:id>/` | Delete capture method by ID | none | `{"detail":"Capture method deleted"}` |
| PUT/PATCH | `/modify-capture-method/<int:id>/` | Update capture method by ID | `{"name":"..."}` | `{"id":2,"name":"..."}` |

### `/membership/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/membership-list/` | List memberships | none | `[{"id":1,"member_name":"Alice","status":"active"}]` |
| POST | `/new-membership/` | Create membership | `{"member_name":"...","type":"..."}` | `{"id":10,"member_name":"..."}` |
| DELETE | `/remove-membership/<int:id>/` | Delete membership by ID | none | `{"detail":"Membership deleted"}` |
| PUT/PATCH | `/modify-membership/<int:id>/` | Update membership by ID | `{"status":"..."}` | `{"id":10,"status":"..."}` |

### `/ministries/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/ministries-list/` | List ministries | none | `[{"id":1,"name":"Choir","leader":"Pastor John"}]` |
| POST | `/new-ministry/` | Create ministry | `{"name":"...","leader":"..."}` | `{"id":8,"name":"..."}` |
| DELETE | `/remove-ministry/<int:id>/` | Delete ministry by ID | none | `{"detail":"Ministry deleted"}` |
| PUT/PATCH | `/modify-ministry/<int:id>/` | Update ministry by ID | `{"leader":"..."}` | `{"id":8,"name":"..."}` |

### `/services/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/list-services/` | List services | none | `[{"id":1,"name":"Sunday Service","time":"9:00 AM"}]` |
| POST | `/new-service/` | Create service | `{"name":"...","time":"..."}` | `{"id":4,"name":"..."}` |
| DELETE | `/remove-service/<int:id>/` | Delete service by ID | none | `{"detail":"Service deleted"}` |
| PUT/PATCH | `/modify-service/<int:id>/` | Update service by ID | `{"time":"..."}` | `{"id":4,"name":"..."}` |

### `/person/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/persons/` | List persons | none | `[{"id":1,"first_name":"Jane","last_name":"Doe","email":"..."}]` |
| POST | `/new-person/` | Create person | `{"first_name":"...","last_name":"..."}` | `{"id":15,"first_name":"..."}` |
| DELETE | `/remove-person/<int:id>/` | Delete person by ID | none | `{"detail":"Person deleted"}` |
| PUT/PATCH | `/modify-person/<int:id>/` | Update person by ID | `{"email":"..."}` | `{"id":15,"first_name":"..."}` |

### `/contact/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/contacts-list/` | List contacts | none | `[{"id":1,"name":"John Doe","phone":"..."}]` |
| POST | `/new-contact/` | Create contact | `{"name":"...","phone":"..."}` | `{"id":12,"name":"..."}` |
| DELETE | `/remove-contact/<int:id>/` | Delete contact by ID | none | `{"detail":"Contact deleted"}` |
| PUT/PATCH | `/modify-contact/<int:id>/` | Update contact by ID | `{"phone":"..."}` | `{"id":12,"name":"..."}` |

### `/leadership/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/leadership-lists/` | List leadership entries | none | `[{"id":1,"title":"Deacon","person":"Jane"}]` |
| POST | `/new-leadership/` | Create leadership entry | `{"title":"...","person":"..."}` | `{"id":6,"title":"..."}` |
| DELETE | `/remove-leadership/<int:id>/` | Delete leadership entry by ID | none | `{"detail":"Leadership deleted"}` |
| PUT/PATCH | `/modify-leadership/<int:id>/` | Update leadership entry by ID | `{"title":"..."}` | `{"id":6,"title":"..."}` |

### `/attendance/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/attendance-lists/` | List attendance records | none | `[{"id":1,"person":"Jane Doe","status":"present"}]` |
| POST | `/mark-attendance/` | Create attendance record | `{"person_id":1,"status":"present"}` | `{"id":22,"person":"Jane Doe"}` |
| DELETE | `/remove-attendance/<int:id>/` | Delete attendance record by ID | none | `{"detail":"Attendance deleted"}` |
| PUT/PATCH | `/modify-attendance/<int:id>/` | Update attendance by ID | `{"status":"absent"}` | `{"id":22,"status":"absent"}` |

### `/faces/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/face-lists/` | List faces | none | `[{"id":1,"person":"Jane","image_url":"..."}]` |
| POST | `/upload-face/` | Upload a face | `{"person_id":1,"image":"..."}` | `{"id":7,"person":"Jane"}` |
| DELETE | `/remove-face/<int:id>/` | Delete face by ID | none | `{"detail":"Face deleted"}` |
| PUT/PATCH | `/modify-face/` | Update face record | `{"image":"..."}` | `{"id":7,"person":"Jane"}` |
| POST | `/recognize-face/` | Recognize a face image and mark attendance | `{"image":"..."}` | `{"recognized_person":"Jane Doe","confidence":0.92}` |
| POST | `/cache-face/` | Cache faces for recognition | `{"face_ids":[1,2,3]}` | `{"detail":"Faces cached"}` |

### `/user/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/list-users/` | List users | none | `[{"id":1,"username":"admin","email":"..."}]` |
| DELETE | `/remove-user/<int:id>/` | Delete user by ID | none | `{"detail":"User deleted"}` |
| PUT/PATCH | `/modify-user/<int:id>/` | Update user by ID | `{"email":"..."}` | `{"id":1,"username":"admin"}` |

### `/auth/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| POST | `/auth/register/` | Register user | `{"username":"...","password":"..."}` | `{"id":5,"username":"..."}` |
| POST | `/auth/refresh/` | Refresh auth token/session | `{"refresh":"..."}` | `{"access":"..."}` |
| POST | `/auth/face-login/` | Face login | `{"image":"..."}` | `{"access":"...","refresh":"..."}` |
| POST | `/auth/login/` | Login | `{"username":"...","password":"..."}` | `{"access":"...","refresh":"..."}` |
| POST | `/auth/verify-login/` | Verify OTP login | `{"otp":"..."}` | `{"access":"..."}` |
| PUT/PATCH | `/auth/user-password-update/<int:id>/` | Update user password | `{"password":"..."}` | `{"detail":"Password updated"}` |
| POST | `/auth/logout-user/` | Logout user | none | `{"detail":"Logged out"}` |
| POST | `/auth/email-verification/` | Request password reset email | `{"email":"..."}` | `{"detail":"Email sent"}` |
| POST | `/auth/otp-verification/` | Verify OTP | `{"otp":"..."}` | `{"detail":"OTP verified"}` |
| POST | `/auth/password-reset/` | Reset password | `{"token":"...","password":"..."}` | `{"detail":"Password reset"}` |
| GET | `/auth/user-log-entries/` | Retrieve user log entries | none | `[{"id":1,"action":"login","user":"..."}]` |

### `/analytics/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/analytics/` | Retrieve analytics data | none | `{"total_attendance":120,"active_members":45}` |
| GET | `/followup-analytics/` | Retrieve follow-up analytics | none | `{"follow_ups_due":8}` |

### `/report/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/attendance-report/` | Attendance report | none | `[{"date":"2026-04-01","present":45}]` |
| GET | `/households-report/` | Household report | none | `[{"household":"Doe","members":5}]` |
| GET | `/contacts-report/` | Contacts report | none | `[{"contact":"Jane Doe","messages_sent":3}]` |
| GET | `/persons-report/` | Persons report | none | `[{"person":"Jane Doe","attendance":20}]` |
| GET | `/users-report/` | Users report | none | `[{"user":"admin","last_login":"2026-04-27"}]` |

### `/message/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/all-messages/` | List messages | none | `[{"id":1,"subject":"Welcome","status":"sent"}]` |
| POST | `/send-sms-message/` | Send SMS message | `{"recipient_phone":"...","message":"..."}` | `{"detail":"SMS sent"}` |
| DELETE | `/remove-message/<int:id>/` | Delete message by ID | none | `{"detail":"Message deleted"}` |
| POST | `/send-email-message/` | Send email message | `{"recipient_email":"...","subject":"...","body":"..."}` | `{"detail":"Email sent"}` |
| POST | `/send-bulk-sms-message/` | Send bulk SMS | `{"recipient_phones":["..."],"message":"..."}` | `{"detail":"Bulk SMS queued"}` |

---

## Common Response Patterns

### List endpoints
- Success: `200 OK`
- Response body: array of objects
- Example:
```json
[
  {"id":1,"name":"First Assembly","location":"Main Street"}
]
```

### Create endpoints
- Success: `201 Created`
- Response body: created object with `id`
- Example:
```json
{"id":10,"name":"Membership A","status":"active"}
```

### Update endpoints
- Success: `200 OK`
- Response body: updated object
- Example:
```json
{"id":10,"status":"active"}
```

### Delete endpoints
- Success: `204 No Content` or `200 OK`
- Response body:
```json
{"detail":"Deleted successfully"}
```

### Auth endpoints
- Login/register success: `200 OK`
- Response body example:
```json
{"access":"<token>","refresh":"<token>"}
```

## Notes
- The route prefixes are defined in `apis/apis/urls.py`.
- The endpoint paths inside each app are defined in the app-level `urls.py` files.
- HTTP methods may vary based on view implementation; the tables above use the likely method for each action.

| --- | --- | --- | --- | --- |
| GET | `/list-roles/` | List roles | none | `[{"id":1,"name":"Administrator"}]` |
| POST | `/new-role/` | Create a role | `{"name":"..."}` | `{"id":5,"name":"..."}` |
| DELETE | `/remove-role/<int:id>/` | Delete role by ID | none | `{"detail":"Role deleted"}` |
| PUT/PATCH | `/modify-role/<int:id>/` | Update role by ID | `{"name":"..."}` | `{"id":5,"name":"..."}` |

### `/permissions/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/all-permissions/` | List permissions | none | `[{"id":1,"codename":"view_user"}]` |
| POST | `/generate-all-permissions/` | Create/update permissions | none | `{"detail":"Permissions generated"}`` |

### `/capturemethod/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/capture-methods-lists/` | List capture methods | none | `[{"id":1,"name":"Face"}]` |
| POST | `/new-capture-method/` | Create capture method | `{"name":"..."}` | `{"id":2,"name":"..."}` |
| DELETE | `/remove-capture-method/<int:id>/` | Delete capture method by ID | none | `{"detail":"Capture method deleted"}` |
| PUT/PATCH | `/modify-capture-method/<int:id>/` | Update capture method by ID | `{"name":"..."}` | `{"id":2,"name":"..."}` |

### `/membership/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/membership-list/` | List memberships | none | `[{"id":1,"member_name":"Alice","status":"active"}]` |
| POST | `/new-membership/` | Create membership | `{"member_name":"...","type":"..."}` | `{"id":10,"member_name":"..."}` |
| DELETE | `/remove-membership/<int:id>/` | Delete membership by ID | none | `{"detail":"Membership deleted"}` |
| PUT/PATCH | `/modify-membership/<int:id>/` | Update membership by ID | `{"status":"..."}` | `{"id":10,"status":"..."}` |

### `/ministries/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/ministries-list/` | List ministries | none | `[{"id":1,"name":"Choir","leader":"Pastor John"}]` |
| POST | `/new-ministry/` | Create ministry | `{"name":"...","leader":"..."}` | `{"id":8,"name":"..."}` |
| DELETE | `/remove-ministry/<int:id>/` | Delete ministry by ID | none | `{"detail":"Ministry deleted"}` |
| PUT/PATCH | `/modify-ministry/<int:id>/` | Update ministry by ID | `{"leader":"..."}` | `{"id":8,"name":"..."}` |

### `/services/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/list-services/` | List services | none | `[{"id":1,"name":"Sunday Service","time":"9:00 AM"}]` |
| POST | `/new-service/` | Create service | `{"name":"...","time":"..."}` | `{"id":4,"name":"..."}` |
| DELETE | `/remove-service/<int:id>/` | Delete service by ID | none | `{"detail":"Service deleted"}` |
| PUT/PATCH | `/modify-service/<int:id>/` | Update service by ID | `{"time":"..."}` | `{"id":4,"name":"..."}` |

### `/person/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/persons/` | List persons | none | `[{"id":1,"first_name":"Jane","last_name":"Doe","email":"..."}]` |
| POST | `/new-person/` | Create person | `{"first_name":"...","last_name":"..."}` | `{"id":15,"first_name":"..."}` |
| DELETE | `/remove-person/<int:id>/` | Delete person by ID | none | `{"detail":"Person deleted"}` |
| PUT/PATCH | `/modify-person/<int:id>/` | Update person by ID | `{"email":"..."}` | `{"id":15,"first_name":"..."}` |

### `/contact/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/contacts-list/` | List contacts | none | `[{"id":1,"name":"John Doe","phone":"..."}]` |
| POST | `/new-contact/` | Create contact | `{"name":"...","phone":"..."}` | `{"id":12,"name":"..."}` |
| DELETE | `/remove-contact/<int:id>/` | Delete contact by ID | none | `{"detail":"Contact deleted"}` |
| PUT/PATCH | `/modify-contact/<int:id>/` | Update contact by ID | `{"phone":"..."}` | `{"id":12,"name":"..."}` |

### `/leadership/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/leadership-lists/` | List leadership entries | none | `[{"id":1,"title":"Deacon","person":"Jane"}]` |
| POST | `/new-leadership/` | Create leadership entry | `{"title":"...","person":"..."}` | `{"id":6,"title":"..."}` |
| DELETE | `/remove-leadership/<int:id>/` | Delete leadership entry by ID | none | `{"detail":"Leadership deleted"}` |
| PUT/PATCH | `/modify-leadership/<int:id>/` | Update leadership entry by ID | `{"title":"..."}` | `{"id":6,"title":"..."}` |

### `/attendance/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/attendance-lists/` | List attendance records | none | `[{"id":1,"person":"Jane Doe","status":"present"}]` |
| POST | `/mark-attendance/` | Create attendance record | `{"person_id":1,"status":"present"}` | `{"id":22,"person":"Jane Doe"}` |
| DELETE | `/remove-attendance/<int:id>/` | Delete attendance record by ID | none | `{"detail":"Attendance deleted"}` |
| PUT/PATCH | `/modify-attendance/<int:id>/` | Update attendance by ID | `{"status":"absent"}` | `{"id":22,"status":"absent"}` |

### `/faces/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/face-lists/` | List faces | none | `[{"id":1,"person":"Jane","image_url":"..."}]` |
| POST | `/upload-face/` | Upload a face | `{"person_id":1,"image":"..."}` | `{"id":7,"person":"Jane"}` |
| DELETE | `/remove-face/<int:id>/` | Delete face by ID | none | `{"detail":"Face deleted"}` |
| PUT/PATCH | `/modify-face/` | Update face record | `{"image":"..."}` | `{"id":7,"person":"Jane"}` |
| POST | `/recognize-face/` | Recognize a face image and mark-attendance | `{"image":"..."}` | `{"recognized_person":"Jane Doe","confidence":0.92}` |
| POST | `/cache-face/` | Cache faces for recognition | `{"face_ids":[1,2,3]}` | `{"detail":"Faces cached"}` |

### `/user/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/list-users/` | List users | none | `[{"id":1,"username":"admin","email":"..."}]` |
| DELETE | `/remove-user/<int:id>/` | Delete user by ID | none | `{"detail":"User deleted"}` |
| PUT/PATCH | `/modify-user/<int:id>/` | Update user by ID | `{"email":"..."}` | `{"id":1,"username":"admin"}` |

### `/auth/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| POST | `/auth/register/` | Register user | `{"username":"...","password":"..."}` | `{"id":5,"username":"..."}` |
| POST | `/auth/refresh/` | Refresh auth token/session | `{"refresh":"..."}` | `{"access":"..."}` |
| POST | `/auth/face-login/` | Face login | `{"image":"..."}` | `{"access":"...","refresh":"..."}` |
| POST | `/auth/login/` | Login | `{"username":"...","password":"..."}` | `{"access":"...","refresh":"..."}` |
| POST | `/auth/verify-login/` | Verify OTP login | `{"otp":"..."}` | `{"access":"..."}` |
| PUT/PATCH | `/auth/user-password-update/<int:id>/` | Update user password | `{"password":"..."}` | `{"detail":"Password updated"}` |
| POST | `/auth/logout-user/` | Logout user | none | `{"detail":"Logged out"}` |
| POST | `/auth/email-verification/` | Request password reset email | `{"email":"..."}` | `{"detail":"Email sent"}` |
| POST | `/auth/otp-verification/` | Verify OTP | `{"otp":"..."}` | `{"detail":"OTP verified"}` |
| POST | `/auth/password-reset/` | Reset password | `{"token":"...","password":"..."}` | `{"detail":"Password reset"}` |
| GET | `/auth/user-log-entries/` | Retrieve user log entries | none | `[{"id":1,"action":"login","user":"..."}]` |

### `/analytics/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/analytics/` | Retrieve analytics data | none | `{"total_attendance":120,"active_members":45}` |
| GET | `/followup-analytics/` | Retrieve follow-up analytics | none | `{"follow_ups_due":8}` |

### `/report/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/attendance-report/` | Attendance report | none | `[{"date":"2026-04-01","present":45}]` |
| GET | `/households-report/` | Household report | none | `[{"household":"Doe","members":5}]` |
| GET | `/contacts-report/` | Contacts report | none | `[{"contact":"Jane Doe","messages_sent":3}]` |
| GET | `/persons-report/` | Persons report | none | `[{"person":"Jane Doe","attendance":20}]` |
| GET | `/users-report/` | Users report | none | `[{"user":"admin","last_login":"2026-04-27"}]` |

### `/message/`
| Method | Path | Description | Request body | Example response |
| --- | --- | --- | --- | --- |
| GET | `/all-messages/` | List messages | none | `[{"id":1,"subject":"Welcome","status":"sent"}]` |
| POST | `/send-sms-message/` | Send SMS message | `{"recipient_phone":"...","message":"..."}` | `{"detail":"SMS sent"}` |
| DELETE | `/remove-message/<int:id>/` | Delete message by ID | none | `{"detail":"Message deleted"}` |
| POST | `/send-email-message/` | Send email message | `{"recipient_email":"...","subject":"...","body":"..."}` | `{"detail":"Email sent"}` |
| POST | `/send-bulk-sms-message/` | Send bulk SMS | `{"recipient_phones":["..."],"message":"..."}` | `{"detail":"Bulk SMS queued"}` |

---

## Common Response Patterns

### List endpoints
- Success: `200 OK`
- Response body: array of objects
- Example:
```json
[
  {"id":1,"name":"First Assembly","location":"Main Street"}
]
```

### Create endpoints
- Success: `201 Created`
- Response body: created object with `id`
- Example:
```json
{"id":10,"name":"Membership A","status":"active"}
```
```

### Update endpoints
- Success: `200 OK`
- Response body: updated object
- Example:
```json
{"id":10,"status":"active"}
```
```

### Delete endpoints
- Success: `204 No Content` or `200 OK`
- Response body:
```json
{"detail":"Deleted successfully"}
```
```

### Auth endpoints
- Login/register success: `200 OK`
- Response body example:
```json
{"access":"<token>","refresh":"<token>"}
```
```

## Notes
- The route prefixes are defined in `apis/apis/urls.py`.
- The endpoint paths inside each app are defined in the app-level `urls.py` files.
- HTTP methods may vary based on view implementation; the tables above use the likely method for each action.
