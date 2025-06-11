import os
import pytest
from unittest.mock import patch, call, DEFAULT # DEFAULT may not work as expected with click.prompt
from click.testing import CliRunner

from main import create_catalog_page
from generate_pdf import generate_pdf # For type hinting if needed, not for direct call

# Re-using the dummy_image fixture concept from test_generate_pdf.py
# To make it available here, we can define it in a conftest.py later
# For now, let's define a simple one here or rely on a known dummy file.
# To avoid complexity, let's assume a dummy file "dummy_photo_for_main.png" will be created.

@pytest.fixture
def dummy_photo_for_main(tmp_path):
    dummy_file = tmp_path / "dummy_photo_for_main.png"
    dummy_file.write_text("dummy content") # Doesn't need to be a real image for os.path.exists
    return str(dummy_file)

def test_main_output_dir_prompt_default(dummy_photo_for_main):
    """
    Test that main.py prompts for output directory with the correct default
    and calls generate_pdf with that directory.
    """
    runner = CliRunner()

    # Mocking os.path.expanduser for the default downloads path
    # Mocking os.path.exists for the photo path validation
    # Mocking click.prompt to simulate user input
    # Mocking generate_pdf to check how it's called

    with patch('os.path.expanduser') as mock_expanduser, \
         patch('os.path.exists') as mock_os_exists, \
         patch('main.click.prompt') as mock_click_prompt, \
         patch('main.generate_pdf') as mock_generate_pdf:

        # Configure mocks
        # First expanduser call is for photo_path, second for '~/Downloads'
        mock_expanduser.side_effect = lambda path: dummy_photo_for_main if path == dummy_photo_for_main else ('/fake/downloads_dir' if path == '~/Downloads' else path)

        mock_os_exists.return_value = True # Assume photo file exists

        # Simulate user inputs via click.prompt
        # The last prompt for output_dir should receive the default and the user "accepts" it (returns the default)
        def prompt_side_effect(*args, **kwargs):
            prompt_text = args[0]
            if "タイトル" in prompt_text:
                return "Main Test Title"
            elif "リンク" in prompt_text:
                return "http://main.example.com"
            elif "写真のパス" in prompt_text:
                return dummy_photo_for_main
            elif "出力先ディレクトリ" in prompt_text:
                # This is the crucial part. We want to check kwargs['default']
                # And simulate user accepting the default.
                # click.prompt returns the default value if user just hits Enter.
                # So, the mock should return kwargs.get('default')
                assert kwargs.get('default') == '/fake/downloads_dir'
                return kwargs.get('default') # Simulate user accepting default
            return DEFAULT # Should not happen with specific checks

        mock_click_prompt.side_effect = prompt_side_effect
        mock_generate_pdf.return_value = "/fake/downloads_dir/Main_Test_Title_catalog.pdf"

        # Call the main function
        result = runner.invoke(create_catalog_page, []) # No CLI args, rely on prompts

        assert result.exit_code == 0, f"CLI exited with error: {result.output}"

        # Assertions
        # Check that os.path.expanduser was called for '~/Downloads'
        # The first call to expanduser is for the photo path.
        # The second call is for the default downloads path.
        # We need to be careful how we assert this.
        # Let's check calls to expanduser more generally.
        expanduser_calls = [c[0][0] for c in mock_expanduser.call_args_list]
        assert '~/Downloads' in expanduser_calls

        # Check that click.prompt for output directory was called with correct default
        # This is implicitly checked by the assert within prompt_side_effect now.
        # We can also check the call list for more explicit assertion:
        prompt_output_dir_called_correctly = False
        for call_args in mock_click_prompt.call_args_list:
            args, kwargs = call_args
            if args and "出力先ディレクトリ" in args[0]:
                assert kwargs.get('default') == '/fake/downloads_dir'
                prompt_output_dir_called_correctly = True
                break
        assert prompt_output_dir_called_correctly, "Prompt for output directory was not called with the correct default."

        # Check that generate_pdf was called with the correct output_dir
        mock_generate_pdf.assert_called_once_with(
            "Main Test Title",
            "http://main.example.com",
            dummy_photo_for_main, # This should be the path returned by the first expanduser
            '/fake/downloads_dir'
        )
