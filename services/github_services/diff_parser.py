from io import StringIO
from typing import List, Dict, Any
from unidiff import PatchSet


class DiffParser:
    """
    Parses unified diff text into a structured, LLM-friendly format.
    """
    def parse(self, diff_text: str) -> List[Dict[str, Any]]:
        """
        Parses the raw diff text.

        Args:
            diff_text: The raw diff text from the GitHub API.

        Returns:
            A list of dictionaries, where each dictionary represents a changed file.
        """
        patch_set = PatchSet(StringIO(diff_text))
        parsed_diff = []

        for patched_file in patch_set:
            if patched_file.is_binary_file:
                continue

            file_change = {
                "source_file": patched_file.source_file,
                "target_file": patched_file.target_file,
                "is_new_file": patched_file.is_added_file,
                "is_deleted_file": patched_file.is_removed_file,
                "is_renamed_file": patched_file.is_rename,
                "hunks": self._parse_hunks(patched_file)
            }
            parsed_diff.append(file_change)

        print(f"Parsed {len(parsed_diff)} changed file(s).")
        return parsed_diff

    def _parse_hunks(self, patched_file: Any) -> List[Dict[str, Any]]:
        """Helper method to parse hunks from a patched file."""
        hunks_data = []
        for hunk in patched_file:
            hunk_data = {
                "hunk_header": str(hunk.section_header).strip(),
                "lines": self._parse_lines(hunk)
            }
            hunks_data.append(hunk_data)
        return hunks_data

    def _parse_lines(self, hunk: Any) -> List[Dict[str, Any]]:
        """Helper method to parse lines from a hunk."""
        lines_data = []
        for line in hunk:
            line_data = {
                "type": self._get_line_type(line),
                "content": line.value,
                "source_line_no": line.source_line_no,
                "target_line_no": line.target_line_no,
            }
            lines_data.append(line_data)
        return lines_data

    def _get_line_type(self, line: Any) -> str:
        """Determines the type of line (added, removed, or context)."""
        if line.is_added:
            return "added"
        elif line.is_removed:
            return "removed"
        else:
            return "context"