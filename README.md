# CodeAssist Minimal - AI Coding Agent

A powerful Python FastAPI application that functions as an AI coding agent powered by Google's Gemini Flash 1.5 model. This application exposes a streaming API endpoint that accepts a public GitHub repository URL and a natural language prompt, then automatically clones the repo, uses AI to make the requested code changes, and creates a pull request on GitHub.

## Features

- **Streaming API**: Real-time progress updates via Server-Sent Events (SSE)
- **GitHub Integration**: Automatic repository cloning and pull request creation
- **Gemini AI-Powered**: Uses Google's Gemini Flash 1.5 for intelligent code analysis and generation
- **Smart File Detection**: Intelligently identifies which files need changes
- **Professional Output**: Generates proper commit messages and PR descriptions
- **Modern Frontend**: Clean, responsive web interface with real-time progress tracking
- **Error Handling**: Robust error handling with informative feedback

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Google Gemini Flash 1.5**: For intelligent code analysis and generation
- **GitPython**: Git operations and repository management
- **PyGitHub**: GitHub API integration for PR creation
- **Uvicorn**: Lightning-fast ASGI server

### Frontend
- **HTML5/CSS3/JavaScript**: Modern web technologies
- **Tailwind CSS**: Utility-first CSS framework
- **Font Awesome**: Icon library
- **Server-Sent Events**: Real-time communication

## Prerequisites

Before running the application, you need:

1. **GitHub Personal Access Token** with `repo` and `public_repo` scopes
   - Generate at: https://github.com/settings/tokens

2. **Google Gemini API Key** 
   - Get from: https://aistudio.google.com/app/apikey

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd backspace-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your tokens
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the application**
   - Frontend: `http://localhost:8000/frontend/`
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