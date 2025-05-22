#!/usr/bin/env python3
"""
Changeblogger
Analyzes staged Git changes and appends a summary to README.md
"""

import os
import sys
import subprocess
import re
import json
from datetime import datetime
from pathlib import Path
try:
    import requests
except ImportError:
    print("❌ Error: 'requests' library not found. Install with: pip install requests")
    sys.exit(1)

def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path.cwd() / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('"\'')

# Load .env file at startup
load_env_file()

class GitChangesSummarizer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.readme_path = self.project_root / "README.md"
        self.openai_api_key = self.get_openai_api_key()

    def get_openai_api_key(self):
        """Get OpenAI API key from environment variable or config file"""
        # First try environment variable
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            return api_key

        # Try global config file
        config_dir = Path.home() / '.config' / 'changeblogger'
        config_file = config_dir / 'config'

        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    for line in f:
                        if line.startswith('OPENAI_API_KEY='):
                            return line.split('=', 1)[1].strip()
            except Exception:
                pass

        print("⚠️  Warning: OPENAI_API_KEY not found.")
        print("   Option 1: Set environment variable: export OPENAI_API_KEY='your-key'")
        print("   Option 2: Create .env file with: OPENAI_API_KEY=your-key")
        print("   Option 3: Run 'changeblogger --setup' to configure globally")
        print("   Continuing without AI summary...")
        return None

    def setup_config(self):
        """Setup configuration interactively"""
        print("🔧 changeblogger Setup")
        print("=" * 30)

        api_key = input("Enter your OpenAI API key: ").strip()
        if not api_key:
            print("❌ No API key provided. Setup cancelled.")
            return

        # Create config directory
        config_dir = Path.home() / '.config' / 'changeblogger'
        config_dir.mkdir(parents=True, exist_ok=True)

        # Write config file
        config_file = config_dir / 'config'
        with open(config_file, 'w') as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")

        # Set restrictive permissions
        os.chmod(config_file, 0o600)

        print(f"✅ Configuration saved to {config_file}")
        print("   You can now use 'changeblogger' in any Git repository!")

    def is_git_repository(self):
        """Check if current directory is a Git repository"""
        git_dir = self.project_root / ".git"
        if git_dir.exists():
            return True

        # Check if we're in a subdirectory of a git repo
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def get_staged_changes(self):
        """Get list of staged files and their change types"""
        try:
            # Get staged files with their status
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-status"],
                capture_output=True,
                text=True,
                check=True
            )

            staged_files = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    status = parts[0]
                    filename = parts[1]
                    staged_files.append((status, filename))

            return staged_files

        except subprocess.CalledProcessError as e:
            print(f"Error getting staged changes: {e}")
            return []

    def get_file_diff(self, filename):
        """Get the actual diff content for a specific file"""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", filename],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return ""

    def get_file_content(self, filename):
        """Get the current content of a file (for new files)"""
        try:
            with open(self.project_root / filename, 'r', encoding='utf-8') as f:
                return f.read()
        except (FileNotFoundError, UnicodeDecodeError):
            return ""

    def call_openai_api(self, changes_data):
        """Call OpenAI API to get a human-readable summary of changes"""
        if not self.openai_api_key:
            return None

        # Prepare the prompt
        system_prompt = """You are a code analyst. Analyze Git changes and provide a concise summary focusing on:

1. For new files: What they do and their purpose
2. For modified files: What functions/sections were changed and what the changes accomplish
3. Overall impact of the changes

Keep the summary brief (2-4 sentences) and technical but accessible."""

        user_prompt = "Please analyze the following Git changes:\n\n"

        for change in changes_data:
            filename = change['filename']
            change_type = change['type']

            user_prompt += f"\n### {filename} ({change_type})\n"

            if change_type == 'added':
                content = change.get('content', '')
                if content:
                    # Limit content length to avoid API limits
                    if len(content) > 3000:
                        content = content[:3000] + "\n... (truncated)"
                    user_prompt += f"```\n{content}\n```\n"
            else:
                diff = change.get('diff', '')
                if diff:
                    # Limit diff length
                    if len(diff) > 2000:
                        diff = diff[:2000] + "\n... (truncated)"
                    user_prompt += f"```diff\n{diff}\n```\n"

        # API call
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.openai_api_key}'
            }

            data = {
                'model': 'gpt-4o-mini',  # Using the cost-effective model
                'messages': [
                    {
                        'role': 'system',
                        'content': system_prompt
                    },
                    {
                        'role': 'user',
                        'content': user_prompt
                    }
                ],
                'max_tokens': 300,
                'temperature': 0.3
            }

            print("🤖 Generating AI summary...")
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                print(f"❌ OpenAI API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"❌ Error calling OpenAI API: {e}")
            return None

    def get_file_stats(self):
        """Get statistics about changes in staged files"""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--stat"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""

    def prepare_changes_for_ai(self, staged_files):
        """Prepare change data for AI analysis"""
        changes_data = []

        for status, filename in staged_files:
            change_info = {
                'filename': filename,
                'type': 'modified'  # default
            }

            # Determine change type
            if status.startswith('A'):
                change_info['type'] = 'added'
                # For new files, get the full content
                change_info['content'] = self.get_file_content(filename)
            elif status.startswith('M'):
                change_info['type'] = 'modified'
                # For modified files, get the diff
                change_info['diff'] = self.get_file_diff(filename)
            elif status.startswith('D'):
                change_info['type'] = 'deleted'
                # Skip deleted files for AI analysis
                continue
            elif status.startswith('R'):
                change_info['type'] = 'renamed'
                change_info['diff'] = self.get_file_diff(filename)

            # Only include files with actual content/diff and skip binary files
            if change_info['type'] == 'added' and change_info.get('content'):
                # Skip if it looks like a binary file
                content = change_info['content']
                if self.is_likely_text_file(filename, content):
                    changes_data.append(change_info)
            elif change_info['type'] in ['modified', 'renamed'] and change_info.get('diff'):
                changes_data.append(change_info)

        return changes_data

    def is_likely_text_file(self, filename, content):
        """Check if a file is likely to be a text file worth analyzing"""
        # Skip common binary file extensions
        binary_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip',
                           '.tar', '.gz', '.exe', '.dll', '.so', '.dylib'}

        file_ext = Path(filename).suffix.lower()
        if file_ext in binary_extensions:
            return False

        # Check if content contains null bytes (binary indicator)
        if '\x00' in content:
            return False

        # Skip very large files
        if len(content) > 50000:  # 50KB limit
            return False

        return True

    def categorize_changes(self, staged_files):
        """Categorize changes by type"""
        categories = {
            'added': [],
            'modified': [],
            'deleted': [],
            'renamed': [],
            'copied': []
        }

        status_map = {
            'A': 'added',
            'M': 'modified',
            'D': 'deleted',
            'R': 'renamed',
            'C': 'copied'
        }

        for status, filename in staged_files:
            # Handle complex status codes (like R100 for rename)
            base_status = status[0]
            if base_status in status_map:
                categories[status_map[base_status]].append(filename)
            else:
                categories['modified'].append(filename)

        return {k: v for k, v in categories.items() if v}

    def generate_summary(self, categories, stats, ai_summary=None):
        """Generate a human-readable summary of changes"""
        timestamp = datetime.now().strftime("%Y-%m-%d")

        summary_lines = [f"## Changes - {timestamp}"]

        # Add AI-generated summary first if available
        if ai_summary:
            summary_lines.append("")
            summary_lines.append("**Summary:**")
            summary_lines.append(ai_summary)
            summary_lines.append("")

        # Add categorized changes
        if categories.get('added'):
            summary_lines.append(f"**Added files:** {', '.join(categories['added'])}")

        if categories.get('modified'):
            summary_lines.append(f"**Modified files:** {', '.join(categories['modified'])}")

        if categories.get('deleted'):
            summary_lines.append(f"**Deleted files:** {', '.join(categories['deleted'])}")

        if categories.get('renamed'):
            summary_lines.append(f"**Renamed files:** {', '.join(categories['renamed'])}")

        if categories.get('copied'):
            summary_lines.append(f"**Copied files:** {', '.join(categories['copied'])}")

        # Add stats if available
        if stats:
            summary_lines.append(f"**Changes summary:**")
            # Extract the summary line from git diff --stat
            stat_lines = stats.split('\n')
            if stat_lines:
                summary_line = stat_lines[-1]  # Usually the last line has the summary
                summary_lines.append(f"```\n{summary_line}\n```")

        # Add a separator
        summary_lines.append("")

        return '\n'.join(summary_lines)

    def update_readme(self, summary):
        """Update README.md with the changes summary"""
        if not self.readme_path.exists():
            print(f"Creating new README.md file...")
            content = "# Project README\n\n## Changelog\n\n"
        else:
            with open(self.readme_path, 'r', encoding='utf-8') as f:
                content = f.read()

        # Look for existing changelog section
        changelog_pattern = r'(## Changelog\s*\n)'

        if re.search(changelog_pattern, content, re.IGNORECASE):
            # Insert after changelog header
            content = re.sub(
                changelog_pattern,
                r'\1' + summary + '\n',
                content,
                flags=re.IGNORECASE
            )
        else:
            # Add changelog section at the end
            if not content.endswith('\n'):
                content += '\n'
            content += f"\n## Changelog\n\n{summary}\n"

        # Write back to file
        with open(self.readme_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ Updated {self.readme_path} with changes summary")

    def run(self):
        """Main execution method"""
        print("🔍 changeblogger")
        print("=" * 30)

        # Check if we're in a Git repository
        if not self.is_git_repository():
            print("❌ Error: Current directory is not a Git repository.")
            sys.exit(1)

        print("✅ Git repository detected")

        # Get staged changes
        staged_files = self.get_staged_changes()

        if not staged_files:
            print("⚠️  No staged changes found. Use 'git add' to stage files first.")
            sys.exit(1)

        print(f"✅ Found {len(staged_files)} staged files")

        # Get file statistics
        stats = self.get_file_stats()

        # Categorize changes
        categories = self.categorize_changes(staged_files)

        # Prepare changes for AI analysis
        ai_summary = None
        if self.openai_api_key:
            changes_data = self.prepare_changes_for_ai(staged_files)
            if changes_data:
                ai_summary = self.call_openai_api(changes_data)

        # Generate summary
        summary = self.generate_summary(categories, stats, ai_summary)

        print("\n📝 Generated summary:")
        print("-" * 30)
        print(summary)
        print("-" * 30)

        # Ask for confirmation
        response = input("\n❓ Add this summary to README.md? (y/N): ").strip().lower()

        if response in ['y', 'yes']:
            self.update_readme(summary)
        else:
            print("❌ Summary not added to README.md")
            sys.exit(0)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--setup':
        summarizer = GitChangesSummarizer()
        summarizer.setup_config()
    else:
        summarizer = GitChangesSummarizer()
        summarizer.run()

if __name__ == "__main__":
    main()
