from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import unittest
from unittest.mock import patch
from pdf_generator import (
    extract_formatting_and_content,
    create_content,
    refine_content_and_structure,
    generate_formatting_kwargs,
    create_pdf
)

class TestPDFGenerator(unittest.TestCase):

    def setUp(self):
        self.valid_input = """
        Create a technical whitepaper on the advancements in artificial intelligence and machine learning. The whitepaper should cover:
        Abstract
        Introduction
        Recent advancements with a focus on neural networks
        Tables showing performance metrics of different models
        Future trends and research directions
        Conclusion

        Formatting instructions:
        Use a white background with black text.
        Headings should be bold.
        Use a 12-point font for body text and 10-point font for tables.
        Add a header with the document title on each page.
        Include citations in APA format.
        """
        self.invalid_input = "Create a document."

    @patch('pdf_generator.ChatPromptTemplate')
    @patch('pdf_generator.llm_mixtral')
    def test_extract_formatting_and_content_valid(self, mock_llm, mock_template):
        mock_response = unittest.mock.Mock()
        mock_response.content.strip.return_value = """
        Content Description: Create a technical whitepaper on the advancements in artificial intelligence and machine learning...
        Formatting Instructions: Use a white background with black text...
        """
        mock_template.from_messages.return_value = unittest.mock.Mock()
        mock_llm.invoke.return_value = mock_response
        
        content_description, formatting_instructions = extract_formatting_and_content(self.valid_input)
        self.assertIn("Create a technical whitepaper", content_description)
        self.assertIn("Use a white background", formatting_instructions)

    @patch('pdf_generator.ChatPromptTemplate')
    @patch('pdf_generator.llm_mixtral')
    def test_extract_formatting_and_content_invalid(self, mock_llm, mock_template):
        mock_response = unittest.mock.Mock()
        mock_response.content.strip.return_value = "Invalid response"
        mock_template.from_messages.return_value = unittest.mock.Mock()
        mock_llm.invoke.return_value = mock_response
        
        with self.assertRaises(ValueError):
            extract_formatting_and_content(self.invalid_input)

    @patch('pdf_generator.ChatPromptTemplate')
    @patch('pdf_generator.llm_llama')
    def test_create_content(self, mock_llm, mock_template):
        mock_response = unittest.mock.Mock()
        mock_response.content.strip.return_value = "# Introduction\nThis is the introduction."
        mock_template.from_messages.return_value = unittest.mock.Mock()
        mock_llm.invoke.return_value = mock_response
        
        content_description = "Create a technical whitepaper on the advancements in AI and ML..."
        content = create_content(content_description)
        self.assertIn("# Introduction", content)

    @patch('pdf_generator.ChatPromptTemplate')
    @patch('pdf_generator.llm_mixtral')
    def test_refine_content_and_structure(self, mock_llm, mock_template):
        mock_response = unittest.mock.Mock()
        mock_response.content.strip.return_value = "# Introduction\nThis is the refined introduction."
        mock_template.from_messages.return_value = unittest.mock.Mock()
        mock_llm.invoke.return_value = mock_response
        
        initial_content = "# Introduction\nThis is the introduction."
        content_description = "Create a technical whitepaper on the advancements in AI and ML..."
        refined_content = refine_content_and_structure(initial_content, content_description)
        self.assertIn("refined introduction", refined_content)

    @patch('pdf_generator.ChatPromptTemplate')
    @patch('pdf_generator.llm_mixtral')
    def test_generate_formatting_kwargs(self, mock_llm, mock_template):
        mock_response = unittest.mock.Mock()
        mock_response.content.strip.return_value = '{"fontName": "Helvetica", "fontSize": 12, "backColor": "#FFFFFF"}'
        mock_template.from_messages.return_value = unittest.mock.Mock()
        mock_llm.invoke.return_value = mock_response
        
        formatting_instructions = "Use a white background with black text."
        formatting_kwargs = generate_formatting_kwargs(formatting_instructions)
        self.assertEqual(formatting_kwargs['fontName'], 'Helvetica')
        self.assertEqual(formatting_kwargs['fontSize'], 12)

    @patch('pdf_generator.SimpleDocTemplate')
    @patch('pdf_generator.markdown2.markdown')
    @patch('pdf_generator.parse_html')
    def test_create_pdf(self, mock_parse_html, mock_markdown, mock_doc_template):
        mock_doc_template.return_value = unittest.mock.Mock()
        mock_markdown.return_value = "<h1>Introduction</h1>"
        mock_parse_html.return_value = [Paragraph("Introduction", getSampleStyleSheet()["Normal"])]
        
        content = "# Introduction\nThis is the introduction."
        formatting_kwargs = {
            "fontName": "Helvetica",
            "fontSize": 12,
            "backColor": "#FFFFFF",
            "textColor": "#000000",
            "header": "Technical Whitepaper"
        }
        create_pdf(content, formatting_kwargs)
        self.assertTrue(mock_doc_template.called)

if __name__ == "__main__":
    unittest.main()
