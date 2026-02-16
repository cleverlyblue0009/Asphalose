# AI-Based Suspicious Activity & File Threat Detection System

A production-ready full-stack application that uses machine learning to detect suspicious system activities and scan files for threats. Built as an industry-level college demo project.

## 🚀 Features

- **Real-time Activity Monitoring** - Tracks system processes, file access, login attempts, and network events
- **ML-Powered Threat Detection** - Uses RandomForest and Isolation Forest models for behavioral analysis
- **File Malware Scanner** - Scans uploaded files with SHA-256 hashing and ML classification
- **Smart Alert System** - Generates and manages security alerts with severity levels
- **Analytics Dashboard** - Beautiful visualizations and comprehensive reports
- **Firebase Authentication** - Secure email/password authentication
- **Background Workers** - Celery-based task queue for activity generation
- **Docker Support** - Complete containerized deployment

## 📋 Tech Stack

### Backend
- **Python 3.10+**
- **FastAPI** - High-performance async API framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM for database operations
- **Redis + Celery** - Background task processing
- **scikit-learn** - Machine learning models
- **Firebase Admin SDK** - Authentication
- **Docker** - Containerization

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **Axios** - HTTP client
- **React Router** - Navigation
- **Firebase Web SDK** - Authentication

## 🏗️ Project Structure

```
Asphalose/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── core/             # Core config, database, auth
│   │   ├── models/           # Database models
│   │   ├── services/         # Business logic
│   │   ├── ml/               # ML models
│   │   ├── workers/          # Celery tasks
│   │   └── main.py           # FastAPI app
│   ├── scripts/              # Utility scripts
│   ├── migrations/           # Database migrations
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API & Firebase
│   │   ├── contexts/         # React contexts
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml
└── README.md
```

## 🔧 Prerequisites

Before you begin, ensure you have:

- **Python 3.10+** installed
- **Node.js 18+** and npm installed
- **PostgreSQL 12+** installed (or use Docker)
- **Redis** installed (or use Docker)
- **Docker & Docker Compose** (optional, for containerized setup)
- **Firebase account** (for authentication)

## 🔐 Firebase Setup

### 1. Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" and follow the wizard
3. Enable **Authentication** with Email/Password provider

### 2. Get Firebase Credentials

#### For Frontend (Web App):
1. Go to Project Settings → General
2. Scroll to "Your apps" and click the Web icon (</>)
3. Register your app
4. Copy the `firebaseConfig` values:
   - `apiKey`
   - `authDomain`
   - `projectId`
   - `appId`

#### For Backend (Admin SDK):
1. Go to Project Settings → Service Accounts
2. Click "Generate new private key"
3. Download the JSON file
4. Extract these values:
   - `project_id`
   - `private_key`
   - `client_email`

## 💻 Local Development Setup

### Option 1: Manual Setup (Without Docker)

#### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create .env file:**
   ```bash
   cp .env.example .env
   ```

5. **Configure .env file with your credentials:**
   ```env
   # Database
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/threat_detection_db

   # Redis
   REDIS_URL=redis://localhost:6379/0
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0

   # Firebase Admin SDK (from downloaded JSON)
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_KEY_HERE\n-----END PRIVATE KEY-----\n"
   FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com

   # Encryption (generate a random 32-character string)
   ENCRYPTION_KEY=your-secure-32-character-key-here

   # CORS
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000
   ```

6. **Create PostgreSQL database:**
   ```bash
   psql -U postgres
   CREATE DATABASE threat_detection_db;
   \q
   ```

7. **Initialize database:**
   ```bash
   python scripts/init_db.py
   ```

8. **Train ML models:**
   ```bash
   python scripts/train_models.py
   ```

9. **Run the backend server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

10. **In a new terminal, start Celery worker:**
    ```bash
    celery -A app.workers.celery_app worker --loglevel=info
    ```

11. **In another terminal, start Celery beat:**
    ```bash
    celery -A app.workers.celery_app beat --loglevel=info
    ```

#### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create .env file:**
   ```bash
   cp .env.example .env
   ```

4. **Configure .env file:**
   ```env
   # Firebase Web SDK Config
   VITE_FIREBASE_API_KEY=your-api-key
   VITE_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=your-project-id
   VITE_FIREBASE_APP_ID=your-app-id

   # API URL
   VITE_API_BASE_URL=http://localhost:8000
   ```

5. **Run the development server:**
   ```bash
   npm run dev
   ```

6. **Open your browser:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Docker Setup (Recommended)

1. **Create .env files** (follow the configuration steps above)

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Access the application:**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

5. **Stop services:**
   ```bash
   docker-compose down
   ```

6. **Remove volumes (reset database):**
   ```bash
   docker-compose down -v
   ```

## 🎯 Usage Guide

### 1. Create an Account

1. Navigate to http://localhost:5173 (or http://localhost for Docker)
2. Click "Sign up"
3. Enter email and password (any valid email format, doesn't need to be real)
4. Click "Create Account"

### 2. Explore the Dashboard

- **Dashboard** - Overview of security status with charts
- **Alerts** - View and acknowledge security alerts
- **Activities** - Browse system activities and logs
- **File Scanner** - Upload files to scan for threats
- **Reports** - Detailed analytics and reports
- **ML Models** - View model metrics and retrain models
- **Settings** - User profile and application settings

### 3. Features to Try

- **Real-time Activity Generation**: Activities are automatically generated every 5 seconds
- **File Scanning**: Upload any file to see the ML-based threat detection
- **Alert Management**: Acknowledge active alerts
- **Model Training**: Retrain ML models from the Models page
- **Analytics**: View charts and statistics in Dashboard and Reports

## 📊 ML Models

### Behavioral Classifier
- **Algorithm**: Random Forest
- **Purpose**: Classify activities as normal or suspicious
- **Features**: Activity type, time patterns, resource usage
- **Metrics**: Accuracy, Precision, Recall, F1-Score

### Anomaly Detector
- **Algorithm**: Isolation Forest
- **Purpose**: Detect unusual behavioral patterns
- **Features**: System metrics, process counts, network activity
- **Contamination**: 10% (expected outliers)

## 🔌 API Endpoints

### Authentication
All endpoints (except `/health`) require Firebase authentication via Bearer token in the Authorization header.

### Main Endpoints
- `GET /health` - Health check (no auth required)
- `GET /api/activities` - Get system activities
- `GET /api/threats` - Get security threats/alerts
- `POST /api/threats/acknowledge` - Acknowledge an alert
- `POST /api/scan-file` - Scan uploaded file
- `GET /api/scan-results` - Get file scan results
- `GET /api/reports/summary` - Get security summary
- `POST /api/models/train` - Train ML models
- `GET /api/models/metrics` - Get model metrics

Full API documentation available at: http://localhost:8000/docs

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🐛 Troubleshooting

### Backend Issues

**Database connection error:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql
```

**Redis connection error:**
```bash
# Check if Redis is running
redis-cli ping

# Start Redis
redis-server
```

**Firebase authentication error:**
- Verify Firebase credentials in .env file
- Check that private key is properly formatted with `\n` for newlines
- Ensure Firebase Authentication is enabled in console

### Frontend Issues

**Firebase not initialized:**
- Check that all VITE_FIREBASE_* variables are set in .env
- Restart the dev server after changing .env

**API connection error:**
- Verify VITE_API_BASE_URL is correct
- Check that backend is running
- Check CORS settings in backend

**Module not found:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📝 Environment Variables Reference

### Backend (.env)
```env
APP_NAME=AI Threat Detection System
DEBUG=True
HOST=0.0.0.0
PORT=8000
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-client-email
ENCRYPTION_KEY=your-encryption-key
CORS_ORIGINS=http://localhost:5173
ACTIVITY_GENERATION_INTERVAL=5
```

### Frontend (.env)
```env
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-auth-domain
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_APP_ID=your-app-id
VITE_API_BASE_URL=http://localhost:8000
```

## 🚀 Production Deployment

### Docker Production Build

1. Update environment variables for production
2. Build and deploy:
   ```bash
   docker-compose -f docker-compose.yml up -d --build
   ```

### Security Considerations

- Use strong encryption keys
- Enable HTTPS/TLS in production
- Secure Firebase credentials
- Configure proper CORS origins
- Use environment-specific Firebase projects
- Enable database backups
- Monitor logs for security events

## 📜 License

This project is created as a college demo project. Feel free to use it for educational purposes.

## 👥 Contributors

Built with Claude Code as an educational demonstration of a production-ready AI security application.

## 🙏 Acknowledgments

- FastAPI for the excellent async framework
- Firebase for authentication services
- scikit-learn for ML capabilities
- React and Tailwind CSS for the beautiful UI
- Recharts for data visualization

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review API docs at http://localhost:8000/docs
3. Check browser console and backend logs for errors

---

**Note**: This is a demonstration project. For production use, implement additional security measures, proper error handling, logging, monitoring, and testing.
