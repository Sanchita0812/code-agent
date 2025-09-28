# CodeAssist Minimal - AI Coding Agent v2.0

A secure Python FastAPI application that functions as an AI coding agent powered by Google's Gemini Flash 1.5 model. This application provides a web interface with JWT authentication and exposes a streaming API endpoint that accepts a public GitHub repository URL and a natural language prompt, then automatically clones the repo, uses AI to make the requested code changes, and creates a pull request on GitHub.

## Features

- **🔐 JWT Authentication**: Secure login system with token-based authentication
- **Streaming API**: Real-time progress updates via Server-Sent Events (SSE)
- **GitHub Integration**: Automatic repository cloning and pull request creation
- **Gemini AI-Powered**: Uses Google's Gemini Flash 1.5 for intelligent code analysis and generation
- **Smart File Detection**: Intelligently identifies which files need changes
- **Professional Output**: Generates proper commit messages and PR descriptions
- **Modern Frontend**: Clean, responsive web interface with real-time progress tracking
- **Error Handling**: Robust error handling with informative feedback
- **Docker Support**: Ready for containerized deployment
- **Production Ready**: Environment validation, health checks, and security best practices

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **JWT Authentication**: Secure token-based authentication with python-jose
- **Pydantic Settings**: Environment variable validation and management
- **Google Gemini Flash 1.5**: For intelligent code analysis and generation
- **GitPython**: Git operations and repository management
- **PyGitHub**: GitHub API integration for PR creation
- **Uvicorn**: Lightning-fast ASGI server
- **Redis**: Optional session storage and caching

### Frontend
- **HTML5/CSS3/JavaScript**: Modern web technologies
- **Tailwind CSS**: Utility-first CSS framework
- **Server-Sent Events**: Real-time communication
- **JWT Token Management**: Secure client-side authentication

## Prerequisites

Before running the application, you need:

1. **GitHub Personal Access Token** with `repo` and `public_repo` scopes
   - Generate at: https://github.com/settings/tokens

2. **Google Gemini API Key** 
   - Get from: https://aistudio.google.com/app/apikey

3. **Python 3.11+** or **Docker** for containerized deployment

## Quick Start

### Option 1: Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd codeassist-minimal
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys and tokens
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Option 2: Docker Deployment

1. **Clone and configure**
   ```bash
   git clone <repository-url>
   cd codeassist-minimal
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

## Access the Application

Once running, access:
- **Login Page**: `http://localhost:8000/frontend/login.html`
- **Main App**: `http://localhost:8000/frontend/` (requires login)
- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

### Default Login Credentials

For demo purposes, use:
- **Username**: `admin`
- **Password**: `password123`

> ⚠️ **Security Note**: Change these credentials in production by updating the `DEMO_USERNAME` and `DEMO_PASSWORD` environment variables.

## Authentication Flow

1. **Login**: Users authenticate at `/frontend/login.html`
2. **JWT Token**: Server returns a JWT token valid for 30 minutes
3. **Token Storage**: Client stores token in localStorage
4. **API Calls**: All `/code/` endpoints require `Authorization: Bearer <token>` header
5. **Auto-Refresh**: Frontend checks token validity and redirects to login if expired

## API Usage

### Authentication Endpoints

#### `POST /auth/login`
```json
{
  "username": "admin",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### `GET /auth/verify`
Verify current token (requires Authorization header).

### Code Generation Endpoint

#### `POST /code/prompt_on_repo` (Protected)

**Headers Required:**
```
Authorization: Bearer <your-jwt-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "repoUrl": "https://github.com/username/repository",
  "prompt": "Add authentication middleware to the Express.js routes"
}
```

### Response: Server-Sent Events Stream

The API returns a stream of events showing progress:

```
event: start
data: Initializing AI coding agent for user: admin...

event: clone
data: Repository cloned successfully.

event: analyze
data: Repository analysis complete.

event: plan
data: Planning complete: Files to edit: 2, Files to create: 1, Files to delete: 0

event: edit
data: Successfully edited: src/middleware/auth.js

event: create
data: Successfully created: src/routes/protected.js

event: commit
data: Changes committed and pushed successfully.

event: pr
data: Creating pull request...

event: done
data: {"pr_url": "https://github.com/user/repo/pull/123", "branch_name": "ai-agent-abc123", "files_modified": 2, "user": "admin", "summary": "Successfully created pull request with 2 modified files."}
```

## Architecture

```
codeassist-minimal/
├── app/
│   ├── api/
│   │   ├── auth.py           # Authentication endpoints
│   │   └── code.py           # Main AI coding endpoint
│   ├── core/
│   │   ├── auth.py           # JWT authentication logic
│   │   └── config.py         # Settings and environment validation
│   ├── services/
│   │   ├── git_service.py    # Git and GitHub operations (FIXED)
│   │   ├── repo_analyzer.py  # Repository structure analysis
│   │   ├── edit_planner.py   # AI-based change planning
│   │   └── code_editor.py    # File editing and PR generation
│   ├── schemas/
│   │   └── request.py        # Pydantic models
│   └── main.py               # FastAPI application with auth middleware
├── frontend/
│   ├── login.html           # Authentication page
│   ├── index.html           # Main application (protected)
│   └── script.js            # Frontend JavaScript (deprecated)
├── tests/                   # Test files
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Multi-service deployment
├── .env.example            # Environment variables template
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | Yes | - |
| `GEMINI_API_KEY` | Google Gemini API Key | Yes | - |
| `SECRET_KEY` | JWT signing secret | Yes | `your-secret-key-change-in-production` |
| `ALGORITHM` | JWT algorithm | No | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry time | No | `30` |
| `DEMO_USERNAME` | Demo login username | No | `admin` |
| `DEMO_PASSWORD` | Demo login password | No | `password123` |
| `HOST` | Server host | No | `0.0.0.0` |
| `PORT` | Server port | No | `8000` |
| `DEBUG` | Enable debug mode | No | `false` |
| `REDIS_URL` | Redis connection URL | No | - |

### GitHub Token Scopes

Your GitHub token needs these scopes:
- `repo` - Full control of private repositories
- `public_repo` - Access to public repositories

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Protected Routes**: All code generation endpoints require authentication
- **Token Expiration**: Configurable token expiry (default: 30 minutes)
- **Environment Validation**: Pydantic-based configuration validation
- **CORS Protection**: Configurable CORS middleware
- **User Attribution**: All commits and PRs are attributed to the authenticated user

## Deployment

### Docker Deployment

1. **Build and run**:
   ```bash
   docker-compose up -d
   ```

2. **View logs**:
   ```bash
   docker-compose logs -f app
   ```

3. **Scale services**:
   ```bash
   docker-compose up -d --scale app=3
   ```

### Production Considerations

1. **Change default credentials**:
   ```bash
   export DEMO_USERNAME=your_admin_user
   export DEMO_PASSWORD=your_secure_password
   ```

2. **Use a strong JWT secret**:
   ```bash
   export SECRET_KEY=$(openssl rand -hex 32)
   ```

3. **Enable HTTPS** with a reverse proxy (nginx, Traefik, etc.)

4. **Set up proper user management** (replace demo authentication)

5. **Configure Redis** for session storage and caching

## What's Fixed in v2.0

### 🔧 Git Operations Fixed
- **Proper GitHub authentication**: Fixed token injection in clone and push operations
- **Branch management**: Improved branch creation and push logic with fallback strategies
- **Error handling**: Better error messages for Git operations
- **URL handling**: Proper parsing and authentication URL construction

### 🔐 Security Added
- **JWT Authentication**: Complete login/logout system
- **Protected endpoints**: All code generation requires authentication
- **Token management**: Automatic token validation and refresh
- **User attribution**: All commits and PRs are tagged with the authenticated user

### 🚀 Production Ready
- **Docker support**: Complete containerization with docker-compose
- **Environment validation**: Pydantic-based configuration management
- **Health checks**: Built-in health monitoring
- **Redis integration**: Optional caching and session storage
- **Proper logging**: Structured logging with configurable levels

## Example Use Cases

1. **Add Authentication** (requires login first)
   ```json
   {
     "repoUrl": "https://github.com/user/express-app",
     "prompt": "Add JWT authentication middleware to all API routes"
   }
   ```

2. **Fix Bug**
   ```json
   {
     "repoUrl": "https://github.com/user/react-app", 
     "prompt": "Fix the memory leak in the useEffect hook in the UserProfile component"
   }
   ```

3. **Add Feature**
   ```json
   {
     "repoUrl": "https://github.com/user/todo-app",
     "prompt": "Add a search functionality to filter todos by title and description"
   }
   ```

## Limitations

- Only works with **public** GitHub repositories
- Limited to repositories that can be analyzed textually
- Changes are made automatically - always review PRs before merging
- Large repositories may take longer to process
- Demo authentication (replace with proper user management in production)

## Security Considerations

- **Never expose API keys** in code or version control
- **Review all generated PRs** before merging
- **Use strong JWT secrets** in production
- **Implement proper user management** (replace demo auth)
- **Enable HTTPS** in production
- **Monitor API usage** to prevent abuse
- **Regularly rotate tokens** and secrets

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Style
The project follows PEP 8 guidelines. Use tools like `black` and `flake8` for code formatting and linting.

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Troubleshooting

### Common Issues

1. **"GitHub token not configured"**
   - Ensure `GITHUB_TOKEN` is set in your `.env` file
   - Verify the token has correct permissions

2. **"Failed to clone repository"**
   - Check if the repository URL is correct and public
   - Ensure you have internet connectivity
   - Verify GitHub token has repo access

3. **"Authentication failed"**
   - Check if you're logged in at `/frontend/login.html`
   - Verify JWT token hasn't expired
   - Clear localStorage and log in again

4. **"Failed to push branch"**
   - Ensure GitHub token has push permissions
   - Check if branch name conflicts with existing branches
   - Verify repository allows pushes from your token

5. **"Gemini API error"**
   - Verify your `GEMINI_API_KEY` is valid
   - Check if you have sufficient API quota

### Logs and Debugging

Enable debug mode by setting `DEBUG=true` in your `.env` file for detailed logging.

**Docker logs**:
```bash
docker-compose logs -f app
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support  

If you encounter any issues:

1. Check the logs for detailed error messages
2. Ensure your tokens have the correct permissions
3. Verify the repository URL is accessible and public
4. Test authentication by visiting `/auth/verify` with your token
5. Check that the repository structure is analyzable

For additional support, please open an issue on GitHub.

---

**Made with care by Sanchita Kiran - Now with Security & Production Ready! 🚀**
   - API docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

## API Usage

### Endpoint: `POST /code/`

Send a JSON request with a repository URL and a natural language prompt:

```json
{
  "repoUrl": "https://github.com/username/repository",
  "prompt": "Add authentication middleware to the Express.js routes"
}
```

### Response: Server-Sent Events Stream

The API returns a stream of events showing progress:

```
event: start
data: Initializing AI coding agent...

event: clone
data: Repository cloned successfully.

event: analyze
data: Repository analysis complete.

event: plan
data: Planning complete: Files to edit: 2, Files to create: 1, Files to delete: 0

event: edit
data: Successfully edited: src/middleware/auth.js

event: create
data: Successfully created: src/routes/protected.js

event: commit
data: Changes committed and pushed successfully.

event: pr
data: Creating pull request...

event: done
data: {"pr_url": "https://github.com/user/repo/pull/123", "branch_name": "ai-agent-abc123", "files_modified": 2, "summary": "Successfully created pull request with 2 modified files."}
```

## Architecture

```
backspace-agent/
├── app/
│   ├── api/
│   │   └── code.py           # Main API endpoint
│   ├── services/
│   │   ├── git_service.py    # Git and GitHub operations
│   │   ├── repo_analyzer.py  # Repository structure analysis
│   │   ├── edit_planner.py   # AI-based change planning
│   │   └── code_editor.py    # File editing and PR generation
│   ├── schemas/
│   │   └── request.py        # Pydantic models
│   └── main.py               # FastAPI application
├── frontend/
│   ├── index.html           # Web interface
│   └── script.js            # Frontend JavaScript
├── tests/                   # Test files
├── .env.example            # Environment variables template
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | Yes |
| `GEMINI_API_KEY` | Google Gemini API Key | Yes |
| `HOST` | Server host (default: 0.0.0.0) | No |
| `PORT` | Server port (default: 8000) | No |
| `DEBUG` | Enable debug mode | No |
| `LOG_LEVEL` | Logging level | No |

### GitHub Token Scopes

Your GitHub token needs these scopes:
- `repo` - Full control of private repositories
- `public_repo` - Access to public repositories

## Example Use Cases

1. **Add Authentication**
   ```json
   {
     "repoUrl": "https://github.com/user/express-app",
     "prompt": "Add JWT authentication middleware to all API routes"
   }
   ```

2. **Fix Bug**
   ```json
   {
     "repoUrl": "https://github.com/user/react-app", 
     "prompt": "Fix the memory leak in the useEffect hook in the UserProfile component"
   }
   ```

3. **Add Feature**
   ```json
   {
     "repoUrl": "https://github.com/user/todo-app",
     "prompt": "Add a search functionality to filter todos by title and description"
   }
   ```

4. **Refactor Code**
   ```json
   {
     "repoUrl": "https://github.com/user/python-api",
     "prompt": "Refactor the database connection code to use connection pooling"
   }
   ```

## Frontend Interface

The application includes a modern web interface with:

- **Clean Design**: Glass-morphism effects with gradient backgrounds
- **Real-time Progress**: Live updates during processing
- **Form Validation**: Input validation with helpful error messages
- **Responsive Layout**: Works on desktop and mobile devices
- **Status Indicators**: Visual feedback for different process stages
- **Direct PR Links**: Quick access to created pull requests

## Limitations

- Only works with **public** GitHub repositories
- Limited to repositories that can be analyzed textually
- Changes are made automatically - always review PRs before merging
- Large repositories may take longer to process
- Some complex changes may require human intervention

## Security Considerations

- Never expose your API keys in code or version control
- Review all generated pull requests before merging
- Use tokens with minimal required permissions
- Consider rate limiting in production environments
- Monitor API usage to prevent abuse

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Style
The project follows PEP 8 guidelines. Use tools like `black` and `flake8` for code formatting and linting.

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Troubleshooting

### Common Issues

1. **"GitHub token not configured"**
   - Ensure `GITHUB_TOKEN` is set in your `.env` file
   - Verify the token has correct permissions

2. **"Failed to clone repository"**
   - Check if the repository URL is correct and public
   - Ensure you have internet connectivity

3. **"Gemini API error"**
   - Verify your `GEMINI_API_KEY` is valid
   - Check if you have sufficient API quota

4. **Frontend not loading**
   - Ensure the backend is running on port 8000
   - Check browser console for JavaScript errors

### Logs and Debugging

Enable debug mode by setting `DEBUG=True` in your `.env` file for detailed logging.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support  

If you encounter any issues:

1. Check the logs for detailed error messages
2. Ensure your tokens have the correct permissions
3. Verify the repository URL is accessible and public
4. Check that the repository structure is analyzable

For additional support, please open an issue on GitHub.

---

**Made with care by Sanchita Kiran**