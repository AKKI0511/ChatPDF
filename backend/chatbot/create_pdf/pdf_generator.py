from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, ListFlowable, ListItem, Table, TableStyle, HRFlowable, XPreformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.lib import colors
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments import highlight
from typing import Tuple, Dict, List, Any
from django.conf import settings
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import markdown2
import uuid
import re
import ast
import os

load_dotenv()

# API key for the LLM service
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set. Please set it as an environment variable.")

# LLM configurations
llm_mixtral = ChatGroq(temperature=0.7, model_name="mixtral-8x7b-32768", groq_api_key=GROQ_API_KEY)
llm_llama = ChatGroq(temperature=0.7, model_name="llama3-70b-8192", groq_api_key=GROQ_API_KEY)

def extract_formatting_and_content(input_text: str) -> Tuple[str, str]:
    """
    Extracts formatting instructions and content description from the user's input text.

    Args:
        input_text (str): The user's input text containing the content description and formatting instructions.

    Returns:
        Tuple[str, str]: A tuple containing the content description and formatting instructions.
    """
    system = (
        "You are an assistant that helps in providing instructions for another LLM based on the user inputs (Prompt) for creating PDFs. "
        "Your task is to separate the given (Prompt) into two parts: "
        "1. Description of the content to be included in the PDF based on the topic provided by the user. "
        "2. Formatting instructions for the PDF provided by the user."
        "Your response should be in this format:"
        "Formatting Instructions: [Your response]\nContent Description: [Your response]"
    )
    human = "Separate the formatting instructions and the content description from the following input:\n\n{text}\n\nFormatting Instructions:\nContent Description:"

    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
    chain = prompt | llm_llama
    response = chain.invoke({"text": input_text})
    result = response.content.strip()
    print(f"LLM-1:\n\n{result}")

    # Extract content description and formatting instructions using regex
    content_desc_match = re.search(r'Content Description:\s*(.*?)\s*(?=Formatting Instructions:|$)', result, re.DOTALL)
    formatting_instructions_match = re.search(r'Formatting Instructions:\s*(.*?)\s*(?=Content Description:|$)', result, re.DOTALL)

    if content_desc_match and formatting_instructions_match:
        content_description = content_desc_match.group(1).strip()
        formatting_instructions = formatting_instructions_match.group(1).strip()
        return content_description, formatting_instructions
    else:
        raise ValueError("Could not parse content description and formatting instructions from input.")


def create_content(content_description: str) -> str:
    """
    Generates detailed content based on the content description using an LLM.

    Args:
        content_description (str): The description of the content to be included in the PDF.

    Returns:
        str: The generated content in Markdown format.
    """
    system = (
        "Your job is to create detailed contents for PDFs including comprehensive information about the provided topic. "
        "Based on the provided description, generate in-depth and informative content about that topic which is to be included in a PDF document. "
        "Ensure the content is detailed, well-structured, and contains substantial information to satisfy the user's needs. "
        "You must also create tables/lists where relevant. "
        "NOTE: While creating tables and lists, make the markdown valid so that it could be converted to HTML tags using markdown2.markdown() in Python. "
        "Ensure the markdown for tables uses proper syntax to avoid conversion issues."
    )
    human = "Create detailed Markdown content for the following description. Only give niche-specific content for the description provided avoiding any extra comments:\n\n{text}"

    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
    chain = prompt | llm_llama
    response = chain.invoke({"text": content_description})
    content = response.content.strip()
    print(f"LLM-Content:\n{content}\n")
    return content


def refine_content_and_structure(initial_content: str, content_description: str) -> str:
    """
    Refines and improves the initial content to ensure it meets the user's requirements.

    Args:
        initial_content (str): The initial content generated by the LLM.
        content_description (str): The description of the content to be included in the PDF.

    Returns:
        str: The refined content in Markdown format.
    """
    system = (
        "You are an assistant that refines and improves content generated by another LLM. "
        "Your task is to enhance the provided Markdown content by removing any unnecessary text, improving the structure, and adding more detailed content if needed. "
        "Use the content description as a guide to ensure the content aligns with the user's requirements."
    )
    human = "Refine and improve the following Markdown content based on the given content description. Ensure the final content is detailed, well-structured, and free of unnecessary text:\n\nContent Description:\n{description}\n\nInitial Content:\n{content}"
    
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
    chain = prompt | llm_mixtral
    response = chain.invoke({"description": content_description, "content": initial_content})
    refined_content = response.content.strip()
    print(f"LLM-Refined:\n{refined_content}\n")
    return refined_content


def generate_formatting_kwargs(formatting_instructions: str) -> Dict[str, str]:
    """
    Generates formatting arguments for the PDF based on the provided formatting instructions.

    Args:
        formatting_instructions (str): The formatting instructions provided by the user.

    Returns:
        Dict[str, str]: A dictionary containing the formatting parameters.
    """
    system = (
        "You are an assistant that generates valid formatting arguments for a PDF. "
        "Based on the provided formatting instructions, create a set of formatting parameters that can be used to style a PDF document. "
        "Your result should be a valid JSON dictionary which could be passed directly to the reportlab library. "
        "Only provide the JSON dictionary, excluding all other text. Ensure the JSON is properly formatted and valid."
        "NOTE: If the user asks for a background/theme then you must include 'backColor': [Your response] with the correct color code, also provide the complementary text color to match the background/theme."
        "Ensure that the syntax for colors is valid for the reportlab library"
    )
    human = "Convert the following formatting instructions into a valid JSON dictionary for the reportlab library:\n\n{text}"

    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
    chain = prompt | llm_mixtral
    response = chain.invoke({"text": formatting_instructions})
    kwargs_json = response.content.strip()
    print(f"LLM-Formats Before JSON Check:\n{kwargs_json}\n")

    # Ensure the JSON output is properly formatted and valid
    try:
        match = re.search(r"\{.*\}", kwargs_json, re.DOTALL)
        if match:
            kwargs_dict = match.group(0)
            formatting_kwargs = ast.literal_eval(kwargs_dict)
            return formatting_kwargs
        else:
            raise ValueError("No valid dictionary found in the response")
    except Exception as e:
        print(f"Error parsing formatting kwargs: {e}")
        return {}


def create_pdf(content: str, formatting_kwargs: Dict[str, Any]) -> str:
    """
    Creates a PDF document based on the provided content and formatting arguments.

    Args:
        content (str): The content to be included in the PDF.
        formatting_kwargs (Dict[str, str]): The formatting arguments for styling the PDF.
    """
    try:
        styles = getSampleStyleSheet()
        custom_style = ParagraphStyle(
            name='CustomStyle',
            parent=styles['Normal'],
            fontName=formatting_kwargs.get('fontName', 'Helvetica'),
            fontSize=formatting_kwargs.get('fontSize', 12),
            leading=formatting_kwargs.get('leading', 1.2 * formatting_kwargs.get('fontSize', 12)),
            spaceBefore=formatting_kwargs.get('spaceBefore', 6),
            spaceAfter=formatting_kwargs.get('spaceAfter', 12),
            leftIndent=formatting_kwargs.get('leftIndent', 0),
            rightIndent=formatting_kwargs.get('rightIndent', 0),
            firstLineIndent=formatting_kwargs.get('firstLineIndent', 0),
            alignment=formatting_kwargs.get('alignment', 0),
            spaceShrinkage=formatting_kwargs.get('spaceShrinkage', 0.05),
            textColor=colors.toColor(formatting_kwargs.get('textColor', '#000000')),
            backColor=colors.toColor(formatting_kwargs.get('backColor', '#FFFFFF'))
        )

        # Ensure the media directory exists
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        # Define the PDF file path in the media directory
        pdf_filename = f"{uuid.uuid4()}.pdf"
        pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_filename)
        pdf_url = os.path.join(settings.MEDIA_URL, pdf_filename)

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=formatting_kwargs.get('pageSize', letter),
            topMargin=formatting_kwargs.get('topMargin', 72),
            bottomMargin=formatting_kwargs.get('bottomMargin', 36),
            leftMargin=formatting_kwargs.get('leftMargin', 36),
            rightMargin=formatting_kwargs.get('rightMargin', 36)
        )
        elements: List[ListFlowable] = []

        # Convert markdown to HTML
        html_content = markdown2.markdown(content, extras=['tables', 'fenced-code-blocks'])
        print(f"HTML CONTENT:\n{html_content}\n")

        # Parse HTML and add elements to PDF
        for element in parse_html(html_content, custom_style, formatting_kwargs):
            elements.append(element)

        def add_background(canvas, doc):
            """
            Adds a background to each page of the PDF document.
            """
            canvas.setFillColor(custom_style.backColor)
            canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1)
            canvas.setFont('Helvetica', 10)
            canvas.setFillColor(custom_style.textColor)
            canvas.drawRightString(200 * mm, 10 * mm, f"Page {doc.page}")
            canvas.drawString(10 * mm, doc.pagesize[1] - 10 * mm, formatting_kwargs.get('header', ''))

        doc.build(elements, onFirstPage=add_background, onLaterPages=add_background)
        print(f"PDF has been created successfully at {pdf_url}.")
        return pdf_path
    except Exception as e:
        print(f"An error occurred while creating the PDF: {e}")
        return ""

def parse_html(html_content: str, custom_style: ParagraphStyle, formatting_kwargs: Dict[str, str]) -> List[ListFlowable]:
    """
    Parses HTML content and converts it to ReportLab flowable elements.

    Args:
        html_content (str): The HTML content to be parsed.
        custom_style (ParagraphStyle): The custom style to be applied to the elements.
        formatting_kwargs (Dict[str, str]): Additional formatting arguments.

    Returns:
        List[Flowable]: A list of ReportLab flowable elements.
    """
    elements = []
    soup = BeautifulSoup(html_content, 'html.parser')
    background_color = formatting_kwargs.get('backColor', colors.white)

    for elem in soup.find_all(True):
        if elem.name in ["p", "h1", "h2", "h3", "h4", "h5", "h6"]:
            style_name = elem.name.upper() if elem.name.startswith("h") else "Normal"
            if elem.name.startswith("h"):
                style = ParagraphStyle(
                    name=style_name,
                    parent=custom_style,
                    fontSize=custom_style.fontSize * (1.4 if elem.name == "h1" else 1.2 if elem.name == "h2" else 1.1),
                    spaceBefore=custom_style.spaceBefore * (1.4 if elem.name == "h1" else 1.2 if elem.name == "h2" else 1.1),
                    spaceAfter=custom_style.spaceAfter * (1.4 if elem.name == "h1" else 1.2 if elem.name == "h2" else 1.1),
                    alignment=TA_CENTER if elem.name == "h1" else custom_style.alignment,
                    textColor=custom_style.textColor,
                    fontName='Helvetica-Bold'
                )
            else:
                style = custom_style
            elements.append(Paragraph(elem.get_text(), style))
        elif elem.name == "pre":
            code_elem = elem.find("code")
            code = code_elem.get_text()
            classes = code_elem.get("class", [])
            language = classes[0].split("-")[-1] if classes else "text"
            lexer = get_lexer_by_name(language, stripall=True)
            formatter = HtmlFormatter(style='colorful', noclasses=True)
            highlighted_code = highlight(code, lexer, formatter)
            code_paragraph = XPreformatted(highlighted_code, ParagraphStyle(
                name='CodeStyle',
                fontName='Courier',
                fontSize=custom_style.fontSize,
                leading=12
            ))
            elements.append(code_paragraph)
        elif elem.name == "img":
            src = elem.get("src", "")
            elements.append(Image(src, width=formatting_kwargs.get('imageWidth', 400), height=formatting_kwargs.get('imageHeight', 300)))
        elif elem.name == "ul":
            list_items = [ListItem(Paragraph(item.get_text(), custom_style)) for item in elem.find_all("li")]
            elements.append(ListFlowable(list_items, bulletType="bullet"))
        elif elem.name == "ol":
            list_items = [ListItem(Paragraph(item.get_text(), custom_style)) for item in elem.find_all("li")]
            elements.append(ListFlowable(list_items, bulletType="i"))
        elif elem.name == "table":
            table_data = []
            for row in elem.find_all("tr"):
                cells = []
                for cell in row.find_all(["td", "th"]):
                    cell_style = ParagraphStyle(
                        name='TableHeader' if cell.name == "th" else 'TableCell',
                        parent=custom_style,
                        fontName='Helvetica-Bold' if cell.name == "th" else custom_style.fontName,
                        fontSize=custom_style.fontSize,
                        leading=custom_style.leading,
                        textColor=colors.toColor(formatting_kwargs.get('tableTextColor', custom_style.textColor)),
                        backColor=colors.toColor(formatting_kwargs.get('tableBackColor', background_color))
                    )
                    cells.append(Paragraph(cell.get_text(), cell_style))
                table_data.append(cells)
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.toColor(formatting_kwargs.get('tableHeaderBackColor', custom_style.textColor))),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.toColor(formatting_kwargs.get('tableHeaderTextColor', background_color))),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
        elif elem.name == "hr":
            elements.append(HRFlowable(width="100%", thickness=2, color=custom_style.textColor))
    return elements


def generate_pdf_from_description(description: str) -> str:
    count = 0
    while count < 5:
        try:
            content_description, formatting_instructions = extract_formatting_and_content(description)
            initial_content = create_content(content_description)
            refined_content = refine_content_and_structure(initial_content, content_description)
            formatting_kwargs = generate_formatting_kwargs(formatting_instructions)
            pdf_path = create_pdf(refined_content, formatting_kwargs)
            return pdf_path
        except ValueError as e:
            print(f'Error {count}: {e}')
        count += 1
    return ""

# def main() -> None:
#     """
#     The main function to parse user input, generate content, and create a PDF.
#     """
#     parser = argparse.ArgumentParser(description="Generate a custom PDF based on user input.")
#     parser.add_argument("input_text", type=str, help="The user input containing the content and formatting instructions for the PDF.")
#     args = parser.parse_args()

#     input_text = args.input_text

#     try:
#         content_description, formatting_instructions = extract_formatting_and_content(input_text)
#         initial_content = create_content(content_description)
#         refined_content = refine_content_and_structure(initial_content, content_description)
#         formatting_kwargs = generate_formatting_kwargs(formatting_instructions)

#         create_pdf(refined_content, formatting_kwargs)
#     except ValueError as e:
#         print(f"Error: {e}")

# if __name__ == "__main__":
#     main()
