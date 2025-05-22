# Changeblogger

An AI-powered Git changes summarizer that automatically analyzes your staged changes and updates your README.md with intelligent changelog entries.

This was made purely for my own usecase with a team I work on, so does a very specific job in a very specific way.

## Features

- Analyzes staged Git changes and understands what they do
- Uses OpenAI's GPT-4o-mini to generate human-readable summaries
- Updates your README.md with dated organized changelog entries
- Distinguishes between new files, modifications, deletions, and renames
- Simple command-line interface that works in any Git repository
- Multiple API key configuration options with secure storage

## Installation

### Option 1: Install from PyPI (when published)
```bash
pip install changeblogger
```

### Option 2: Install from Source
```bash
git clone https://github.com/obsoletenerd/changeblogger.git
cd changeblogger
pip install -e .
```

### Option 3: Development Installation
```bash
git clone https://github.com/obsoletenerd/changeblogger.git
cd changeblogger
pip install -r requirements.txt
pip install -e .
```

## Setup

### 1. Get an OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Generate a new API key

### 2. Configure Your API Key

Choose one of these methods:

#### Method A: Global Configuration (Recommended)
```bash
changeblogger --setup
```
This will prompt you for your API key and store it securely in `~/.config/changeblogger/config`.

#### Method B: Environment Variable
```bash
export OPENAI_API_KEY="your-api-key-here"
```

Add this to your shell profile (`.bashrc`, `.zshrc`, etc.) to make it permanent.

#### Method C: Per-Project `.env` File
Create a `.env` file in your project root:
```
OPENAI_API_KEY=your-api-key-here
```

⚠️ **Important**: Add `.env` to your `.gitignore` to avoid committing your API key!

## Usage

### Basic Usage

1. **Make your changes** to your project files
2. **Stage them** with Git:
   ```bash
   git add .
   # or stage specific files:
   git add file1.py file2.py
   ```
3. **Run changeblogger**:
   ```bash
   changeblogger
   ```
4. **Review the generated summary** and confirm to add it to your README.md

### Example Workflow

```bash
# Make some changes to your code
echo "print('Hello, World!')" > hello.py

# Stage the changes
git add hello.py

# Generate changelog entry
changeblogger
```

This will generate output like:
```
🔍 changeblogger
==============================
✅ Git repository detected
✅ Found 1 staged files
🤖 Generating AI summary...

📝 Generated summary:
------------------------------
## Changes - 2025-05-22

**Summary:**
Added a simple Python script that prints "Hello, World!" to demonstrate basic program output functionality.

**Added files:** hello.py
**Changes summary:**
```
 1 file changed, 1 insertion(+)
```
------------------------------

❓ Add this summary to README.md? (y/N):
```

## What Gets Analyzed

changeblogger intelligently analyzes different types of changes:

- **New Files**: Analyzes the full content to understand the file's purpose
- **Modified Files**: Examines the diff to understand what changed and why
- **Deleted Files**: Notes deletions but doesn't analyze content
- **Renamed Files**: Tracks renames and analyzes any content changes
- **Binary Files**: Automatically skips binary files (images, executables, etc.)

## Configuration Options

### API Key Precedence
changeblogger looks for your API key in this order:
1. `OPENAI_API_KEY` environment variable
2. Project-level `.env` file
3. Global config file (`~/.config/changeblogger/config`)

### Customization
The tool automatically:
- Creates a "Changelog" section if your README.md doesn't have one
- Adds new entries at the top of the changelog
- Handles existing changelog sections intelligently
- Formats entries with date stamps

## Example Output

Here's what gets added to your README.md:

```markdown
## Changelog

## Changes - 2025-05-22

**Summary:**
Implemented user authentication system with JWT tokens and role-based access control. Added middleware for request validation and updated the database schema to support user sessions and permissions.

**Added files:** auth/jwt_handler.py, middleware/auth_middleware.py, models/user_role.py
**Modified files:** app.py, database/schema.sql, routes/api.py
**Changes summary:**
```
 6 files changed, 187 insertions(+), 23 deletions(-)
```

## Changes - 2025-05-21

**Summary:**
Fixed bug in data processing pipeline that was causing memory leaks during large file operations.

**Modified files:** data/processor.py, utils/memory_manager.py
**Changes summary:**
```
 2 files changed, 15 insertions(+), 8 deletions(-)
```
```

## Troubleshooting

### Common Issues

**"No staged changes found"**
- Make sure you've run `git add` on your files before running changeblogger

**"OPENAI_API_KEY not found"**
- Follow the setup instructions above to configure your API key
- Verify your API key is valid and has sufficient credits

**"Not a Git repository"**
- Make sure you're running changeblogger inside a Git repository
- Run `git init` if you haven't initialized Git yet

**"API rate limit exceeded"**
- You're making too many requests. Wait a moment and try again
- Check your OpenAI account usage limits

### Getting Help

If you encounter issues:
1. Check that your API key is correctly configured
2. Ensure you're in a Git repository with staged changes
3. Verify your internet connection for API calls
4. Check the OpenAI status page for service issues

## Cost Estimation

changeblogger uses OpenAI's `gpt-4o-mini` model, which is very cost-effective:
- Typical usage costs only a few cents per run
- Most projects will spend less than $1/month even with frequent use
- Large files are automatically truncated to stay within reasonable token limits

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

```bash
git clone https://github.com/yourusername/changeblogger.git
cd changeblogger
pip install -r requirements.txt
pip install -e .
```

### Running Tests
```bash
python -m pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

## Changes - 2025-05-22

**Summary:**
Initial release of changeblogger with AI-powered Git change analysis, OpenAI integration, and automatic README.md changelog updates.

**Added files:** Complete package structure with setup.py, main module, and documentation
**Changes summary:**
```
 Multiple files changed, initial project setup
```
