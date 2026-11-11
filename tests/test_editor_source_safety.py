"""Inert adversarial fixtures: none launches VS Code, Node, or a font."""

from pathlib import Path
import shutil
import tempfile
import unittest

from security.check_editor_source_safety import PINNED_FONTS, check_tree


REPO = Path(__file__).resolve().parents[1]


class EditorSourceSafetyTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="tkal-editor-static-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        editor = self.root / ".vscode"
        editor.mkdir()
        (editor / "tasks.json").write_text('{"version":"2.0.0","tasks":[]}', encoding="utf-8")
        (editor / "settings.json").write_text('{"task.allowAutomaticTasks":"off"}', encoding="utf-8")
        shutil.copytree(REPO / "public" / "fonts", self.root / "public" / "fonts")

    def failures(self):
        return check_tree(self.root)

    def task(self, value):
        (self.root / ".vscode" / "tasks.json").write_text(value, encoding="utf-8")

    def setting(self, value):
        (self.root / ".vscode" / "settings.json").write_text(value, encoding="utf-8")

    def test_current_source(self):
        self.assertEqual(check_tree(REPO), [])

    def test_safe_manual_task(self):
        self.task('{"tasks":[{"command":"echo", "args":["safe // text"],'
                  '"runOptions":{"reevaluateOnRerun":true}}]}')
        self.assertEqual(self.failures(), [])

    def test_safe_bom_comments_and_trailing_comma(self):
        (self.root / ".vscode" / "tasks.json").write_bytes(
            b'\xef\xbb\xbf{ /* comment */ "tasks":[{"label":"manual",},],}'
        )
        self.assertEqual(self.failures(), [])

    def test_reject_original_hidden_folder_open(self):
        self.task('{"tasks":[{"label":"eslint-check","type":"shell",'
                  '"command":"node","args":["./public/fonts/fa-solid-600.ttf"],'
                  '"hide":true,"runOptions":{"runOn":"folderOpen"}}]}')
        result = self.failures()
        self.assertTrue(any("folderOpen" in item or "font asset" in item for item in result), result)

    def test_nested_os_override_and_top_level_folder_open(self):
        fixtures = (
            '{"windows":{"tasks":[{"runOptions":{"runOn":"folderOpen"}}]},"tasks":[]}',
            '{"tasks":[{"windows":{"runOptions":{"runOn":"folderOpen"}}}]}',
            '{"tasks":[{"osx":{"runOptions":{"runOn":"folderOpen"}}}]}',
            '{"tasks":[{"linux":{"runOn":"folderOpen"}}]}',
        )
        for fixture in fixtures:
            with self.subTest(fixture=fixture):
                self.task(fixture)
                self.assertTrue(any("folderOpen" in value for value in self.failures()))

    def test_reject_settings_auto_tasks_and_embedded_task(self):
        self.setting('{"task.allowAutomaticTasks":true}')
        self.assertTrue(self.failures())
        self.setting('{"task.allowAutomaticTasks":"on"}')
        self.assertTrue(self.failures())
        self.setting('{"task.allowAutomaticTasks":"off","tasks":{"runOn":"folderOpen"}}')
        self.assertTrue(any("embedded" in item for item in self.failures()))

    def test_reject_duplicate_json_keys_and_invalid_jsonc(self):
        for fixture in (
            '{"tasks":[,]}',
            '{"tasks":[{"runOptions":{"runOn":"manual","runOn":"folderOpen"}}]}',
            '{"tasks":[],"tasks":[]}',
            '{"tasks":[{"label":"unterminated"}',
            '{/* missing close "tasks":[]}',
        ):
            with self.subTest(fixture=fixture):
                self.task(fixture)
                self.assertTrue(self.failures(), fixture)

    def test_reject_casefold_nested_editor_directory(self):
        target = self.root / "subproject" / ".VSCODE"
        target.mkdir(parents=True)
        (target / "TASKS.JSON").write_text(
            '{"tasks":[{"runOptions":{"runOn":"folderOpen"}}]}',
            encoding="utf-8",
        )
        self.assertTrue(any("folderOpen" in item for item in self.failures()))

    def test_reject_nested_uppercase_workspace_name(self):
        target = self.root / "subproject"
        target.mkdir()
        (target / "ship.CODE-WORKSPACE").write_text(
            '{"settings":{"task.allowAutomaticTasks":true},'
            '"tasks":{"tasks":[{"runOptions":{"runOn":"folderOpen"}}]}}',
            encoding="utf-8",
        )
        self.assertTrue(any("automatic" in item or "folderOpen" in item for item in self.failures()))

    def test_reject_inherited_font_asset_command(self):
        self.task('{"tasks":[{"command":"node","windows":'
                  '{"args":[".\\\\public\\\\fonts\\\\fa-solid-900.ttf"]}}]}')
        self.assertTrue(any("font asset" in item for item in self.failures()))

    def test_reject_injected_font_filename(self):
        (self.root / "public" / "fonts" / "fa-solid-600.ttf").write_text("inert", encoding="utf-8")
        self.assertTrue(any("unapproved" in item for item in self.failures()))

    def test_reject_font_with_magic_prefix_and_appended_payload(self):
        path = self.root / "public" / "fonts" / "fa-solid-900.ttf"
        path.write_bytes(path.read_bytes() + b"INERT_PAYLOAD")
        self.assertTrue(any("SHA256 mismatch" in item for item in self.failures()))

    def test_svg_line_endings_are_only_permitted_normalization(self):
        path = self.root / "public" / "fonts" / "fa-brands-400.svg"
        path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))
        self.assertEqual(self.failures(), [])
        path.write_bytes(path.read_bytes() + b"<script>inert</script>")
        self.assertTrue(any("SHA256 mismatch" in item for item in self.failures()))

    def test_reject_symlinked_asset_or_config(self):
        font = self.root / "public" / "fonts" / "fa-solid-900.ttf"
        font.unlink()
        font.symlink_to(REPO / "public" / "fonts" / "fa-solid-900.ttf")
        self.assertTrue(any("symlinked" in item for item in self.failures()))
        font.unlink()
        shutil.copyfile(REPO / "public" / "fonts" / "fa-solid-900.ttf", font)
        task = self.root / ".vscode" / "tasks.json"
        task.unlink()
        task.symlink_to(REPO / ".vscode" / "tasks.json")
        self.assertTrue(any("symlinked" in item for item in self.failures()))

    def test_reject_symlinked_editor_directory_even_with_safe_tasks(self):
        shutil.rmtree(self.root / ".vscode")
        (self.root / ".vscode").symlink_to(REPO / ".vscode", target_is_directory=True)
        self.assertTrue(any(".vscode directory" in item for item in self.failures()))

    def test_reject_symlinked_nested_editor_directory(self):
        sub = self.root / "subproject"
        sub.mkdir()
        (sub / ".VSCODE").symlink_to(REPO / ".vscode", target_is_directory=True)
        self.assertTrue(any("nested editor directory" in item for item in self.failures()))

    def test_missing_required_settings_fail_closed(self):
        (self.root / ".vscode" / "settings.json").unlink()
        self.assertTrue(self.failures())

    def test_font_count_is_pinned(self):
        self.assertEqual(len(PINNED_FONTS), 15)
        self.assertNotIn("fa-solid-600.ttf", PINNED_FONTS)

    def test_credentials_remain_ignored_from_parent_source(self):
        rules = {line.strip() for line in (REPO / ".gitignore").read_text(encoding="utf-8").splitlines()}
        self.assertTrue({".env", ".env.*"}.issubset(rules))


if __name__ == "__main__":
    unittest.main()
