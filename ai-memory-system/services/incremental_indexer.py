"""
Incremental Indexer with Git Diff Tracking
Only re-indexes files that changed since last indexing

Expected Benefit: 90-95% time savings for typical updates
Example: 20 changed files vs 3973 total files = 99.5% skip rate
"""

import subprocess
import json
import logging
from pathlib import Path
from typing import List, Dict, Set, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class IncrementalIndexer:
    """
    Git-based incremental indexer

    Features:
    - Tracks last indexed commit hash
    - Uses git diff to find changed files
    - Only re-indexes changed .bsl files
    - Maintains incremental state in metadata
    """

    def __init__(
        self,
        repo_path: str = "../",
        state_file: str = "data/index/incremental_state.json"
    ):
        self.repo_path = Path(repo_path)
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Load state
        self.state = self._load_state()

        logger.info(f"IncrementalIndexer initialized")
        logger.info(f"  Repository: {self.repo_path}")
        logger.info(f"  Last indexed commit: {self.state.get('last_commit', 'None')}")

    def _load_state(self) -> Dict:
        """Load incremental indexing state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load state: {e}")

        return {
            'last_commit': None,
            'last_indexed_at': None,
            'total_files_indexed': 0,
            'incremental_runs': []
        }

    def _save_state(self):
        """Save incremental indexing state"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            logger.info(f"State saved: {self.state_file}")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def _run_git_command(self, command: List[str]) -> str:
        """
        Run git command and return output

        Args:
            command: Git command as list of args

        Returns:
            Command output as string
        """
        try:
            result = subprocess.run(
                ['git'] + command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                encoding='utf-8',
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {e}")
            logger.error(f"stderr: {e.stderr}")
            return ""
        except Exception as e:
            logger.error(f"Error running git command: {e}")
            return ""

    def get_current_commit(self) -> Optional[str]:
        """Get current HEAD commit hash"""
        commit_hash = self._run_git_command(['rev-parse', 'HEAD'])
        if commit_hash:
            logger.debug(f"Current commit: {commit_hash}")
            return commit_hash
        return None

    def get_changed_files(self, from_commit: Optional[str] = None) -> Set[str]:
        """
        Get list of changed .bsl files since specified commit

        Args:
            from_commit: Start commit (default: last indexed commit)

        Returns:
            Set of changed .bsl file paths (relative to repo root)
        """
        if from_commit is None:
            from_commit = self.state.get('last_commit')

        if not from_commit:
            logger.warning("No previous commit found, will index all files")
            return self._get_all_bsl_files()

        # Get diff with current HEAD
        current_commit = self.get_current_commit()
        if not current_commit:
            logger.error("Failed to get current commit")
            return set()

        # Get list of changed files
        diff_output = self._run_git_command([
            'diff',
            '--name-only',
            '--diff-filter=ACMRT',  # Added, Copied, Modified, Renamed, Type changed
            from_commit,
            current_commit
        ])

        if not diff_output:
            logger.info("No changes detected")
            return set()

        # Filter .bsl files
        changed_files = set()
        for line in diff_output.split('\n'):
            if line.strip() and line.endswith('.bsl'):
                # Convert to absolute path
                file_path = (self.repo_path / line.strip()).resolve()
                if file_path.exists():
                    changed_files.add(str(file_path))

        logger.info(f"Found {len(changed_files)} changed .bsl files")
        return changed_files

    def _get_all_bsl_files(self) -> Set[str]:
        """Get all .bsl files in repository (fallback for first run)"""
        all_files = set()

        # Use git ls-files to get tracked .bsl files
        output = self._run_git_command(['ls-files', '*.bsl'])

        if output:
            for line in output.split('\n'):
                if line.strip():
                    file_path = (self.repo_path / line.strip()).resolve()
                    if file_path.exists():
                        all_files.add(str(file_path))

        logger.info(f"Found {len(all_files)} total .bsl files")
        return all_files

    def get_files_to_index(self) -> List[str]:
        """
        Get list of files that need to be indexed

        Returns:
            List of file paths to index
        """
        changed_files = self.get_changed_files()
        return sorted(list(changed_files))

    def mark_indexed(self, indexed_files: List[str]):
        """
        Mark files as indexed and update state

        Args:
            indexed_files: List of successfully indexed file paths
        """
        current_commit = self.get_current_commit()

        if not current_commit:
            logger.error("Failed to get current commit, state not updated")
            return

        # Update state
        self.state['last_commit'] = current_commit
        self.state['last_indexed_at'] = datetime.now().isoformat()
        self.state['total_files_indexed'] = len(indexed_files)

        # Add run to history
        self.state['incremental_runs'].append({
            'commit': current_commit,
            'indexed_at': datetime.now().isoformat(),
            'files_count': len(indexed_files)
        })

        # Keep last 10 runs
        if len(self.state['incremental_runs']) > 10:
            self.state['incremental_runs'] = self.state['incremental_runs'][-10:]

        self._save_state()

        logger.info(f"Marked {len(indexed_files)} files as indexed")
        logger.info(f"Updated last commit to: {current_commit}")

    def get_statistics(self) -> Dict:
        """Get incremental indexing statistics"""
        total_files = len(self._get_all_bsl_files())

        return {
            'last_commit': self.state.get('last_commit'),
            'last_indexed_at': self.state.get('last_indexed_at'),
            'total_files_in_repo': total_files,
            'total_runs': len(self.state.get('incremental_runs', [])),
            'state_file': str(self.state_file)
        }

    def print_statistics(self):
        """Print incremental indexing statistics"""
        stats = self.get_statistics()

        print("\n" + "=" * 60)
        print("INCREMENTAL INDEXER STATISTICS")
        print("=" * 60)
        print(f"Total .bsl files:     {stats['total_files_in_repo']}")
        print(f"Last commit:          {stats['last_commit'] or 'None'}")
        print(f"Last indexed:         {stats['last_indexed_at'] or 'Never'}")
        print(f"Incremental runs:     {stats['total_runs']}")
        print(f"State file:           {stats['state_file']}")
        print("=" * 60 + "\n")


# Example usage
if __name__ == "__main__":
    import sys

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Create incremental indexer
    indexer = IncrementalIndexer(repo_path="../")

    # Print current state
    indexer.print_statistics()

    # Get files to index
    files_to_index = indexer.get_files_to_index()

    print(f"\n[INFO] Files to index: {len(files_to_index)}")

    if files_to_index:
        print("\n[INFO] Changed files:")
        for i, file_path in enumerate(files_to_index[:10], 1):
            print(f"  {i}. {Path(file_path).relative_to(Path('../').resolve())}")

        if len(files_to_index) > 10:
            print(f"  ... and {len(files_to_index) - 10} more files")
    else:
        print("\n[OK] No files to index (repository unchanged)")

    # Simulate marking as indexed (for testing)
    if len(sys.argv) > 1 and sys.argv[1] == '--mark-indexed':
        indexer.mark_indexed(files_to_index)
        print("\n[OK] Files marked as indexed")
