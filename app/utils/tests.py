import unittest
from unittest.mock import patch, MagicMock
from app.utils import fonts, colors, logo_colors, logo_position
from app.models import complex_llms

class TestBrandCompliance(unittest.TestCase):

    @patch('app.utils.fonts.analyze_pdf_fonts')
    @patch('app.utils.fonts.analyze_slide_fonts')
    def test_verify_fonts_success(self, mock_slide_fonts, mock_pdf_fonts):
        mock_slide_fonts.return_value = {"Arial"}
        mock_pdf_fonts.return_value = {"Arial", "Helvetica"}
        score, explanation = fonts.verify_fonts("dummy.pdf", "dummy.png", "fake_api_key")
        self.assertEqual(score, 1)
        self.assertIn("present", explanation)

    @patch('app.utils.colors.analyze_colors_with_llm')
    def test_analyze_colors_compliant(self, mock_llm):
        mock_llm.return_value = (1, "Colors match.")
        score, explanation = colors.analyze_colors("dummy.pdf", "dummy.png")
        self.assertEqual(score, 1)
        self.assertIn("match", explanation)

    @patch('app.utils.logo_colors.model.generate')
    @patch('app.utils.logo_colors.processor')
    def test_logo_colors_model(self, mock_processor, mock_generate):
        mock_processor.return_value = MagicMock()
        mock_generate.return_value = [MagicMock()]
        mock_processor.tokenizer.decode.return_value = "blue, red"
        score, explanation = logo_colors.check_logo_colors("dummy.png", "dummy.pdf")
        self.assertIn(score, [0, 1])  # Depending on mocked colors

    @patch('app.utils.logo_position.model.generate')
    @patch('app.utils.logo_position.processor')
    def test_logo_position_logic(self, mock_processor, mock_generate):
        mock_generate.return_value = [MagicMock()]
        mock_processor.tokenizer.decode.return_value = "1: Logo is correct."
        score, explanation = logo_position.check_logo_position("dummy.png", "dummy.pdf")
        self.assertEqual(score, 1)

    @patch('app.models.complex_llms.fonts.verify_fonts')
    @patch('app.models.complex_llms.logo_position.check_logo_position')
    @patch('app.models.complex_llms.logo_colors.check_logo_colors')
    @patch('app.models.complex_llms.colors.analyze_colors')
    def test_assessment_pipeline(self, mock_colors, mock_logo_colors, mock_logo_pos, mock_fonts):
        mock_fonts.return_value = (1, "Font OK")
        mock_logo_pos.return_value = (1, "Logo OK")
        mock_logo_colors.return_value = (1, "Colors OK")
        mock_colors.return_value = (1, "Palette OK")
        score, reasons = complex_llms.assess_slide_compliance("image.png", "kit.pdf", "api")
        self.assertEqual(score, 4)
        self.assertEqual(len(reasons), 4)

if __name__ == '__main__':
    unittest.main()
