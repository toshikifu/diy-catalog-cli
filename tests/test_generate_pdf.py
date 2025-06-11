import os
import tempfile
import pytest
from pathlib import Path
from PIL import Image
from generate_pdf import generate_pdf

# Helper function to create a dummy image
@pytest.fixture
def dummy_image(tmp_path: Path) -> str:
    img = Image.new('RGB', (10, 10), color='red') # 1x1 might be too small for fpdf
    img_path = tmp_path / "dummy_photo.png"
    img.save(img_path)
    return str(img_path)

def test_pdf_generation_specific_directory(dummy_image: str):
    """Test PDF generation in a specified output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = str(tmpdir)
        title = "Test Specific Dir"
        link = "http://example.com/specific"

        generated_pdf_path = generate_pdf(title, link, dummy_image, output_dir=output_dir)

        expected_filename = f"{title.replace(' ', '_')}_catalog.pdf"
        expected_path = os.path.join(output_dir, expected_filename)

        assert generated_pdf_path == expected_path
        assert os.path.exists(expected_path), f"PDF file should be created at {expected_path}"

def test_pdf_generation_default_directory(dummy_image: str):
    """Test PDF generation in the default (current working) directory."""
    title_none = "Test Default Dir None"
    link_none = "http://example.com/default_none"
    expected_filename_none = f"{title_none.replace(' ', '_')}_catalog.pdf"
    expected_path_none = os.path.join(os.getcwd(), expected_filename_none)

    # Test with output_dir=None
    generated_pdf_path_none = generate_pdf(title_none, link_none, dummy_image, output_dir=None)

    # generate_pdf returns a relative path in this case
    assert generated_pdf_path_none == expected_filename_none
    assert os.path.exists(expected_path_none), f"PDF file should be created at {expected_path_none}"

    if os.path.exists(expected_path_none):
        os.remove(expected_path_none)

    title_empty = "Test Default Dir Empty"
    link_empty = "http://example.com/default_empty"
    expected_filename_empty = f"{title_empty.replace(' ', '_')}_catalog.pdf"
    expected_path_empty = os.path.join(os.getcwd(), expected_filename_empty)

    # Test with output_dir=""
    generated_pdf_path_empty = generate_pdf(title_empty, link_empty, dummy_image, output_dir="")

    # generate_pdf returns a relative path in this case
    assert generated_pdf_path_empty == expected_filename_empty
    assert os.path.exists(expected_path_empty), f"PDF file should be created at {expected_path_empty}"

    if os.path.exists(expected_path_empty):
        os.remove(expected_path_empty)
