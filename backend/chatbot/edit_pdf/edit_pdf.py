from typing import Dict, Any, Optional
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from .editor import PDFEditor
import os
from django.conf import settings
import shutil

# settings.configure()
load_dotenv()

# API key for the LLM service
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not set. Please set it as an environment variable."
    )


class FormatArgs(BaseModel):
    """Instructions for custom formatting of a PDF."""

    text_color: Optional[str] = Field(
        None,
        description="The color of the text in hexadecimal format (e.g., '#FF00FF').",
    )
    font_scale: Optional[float] = Field(
        1.0,
        description="The scale factor to be applied to change the font size of the text. Use values less than 1 for smaller font sizes and values greater than 1 for larger font sizes. Default is 1.",
    )
    background_color: Optional[str] = Field(
        None,
        description="The background color in hexadecimal format (e.g., '#330080').",
    )


@tool
def generate_formatting_args(instructions: str) -> Dict[str, Any]:
    """
    Generates formatting arguments based on user instructions for editing PDF as a valid dict.
    Args:
        instructions: Formatting instructions given by the user to edit a PDF.
    """
    # Simplified logic for demonstration; real implementation would use NLP to parse instructions
    formatting_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert extraction algorithm. "
                "Only extract relevant information from the instructions. "
                "If you do not know the value of an attribute asked to extract or the attribute is not mentioned in the instructions, "
                "return null for the attribute's value.",
            ),
            ("human", "{instructions}"),
        ]
    )
    runnable = formatting_prompt | llm.with_structured_output(schema=FormatArgs)
    response = runnable.invoke({"instructions": instructions})

    # Filter out None values
    formatting_args = {
        key: value for key, value in response.dict().items() if value is not None
    }
    return formatting_args



@tool
def edit_pdf(formatting_args: Dict[str, Any], input_pdf: str) -> str:
    """
    Edit the PDF based on the given arguments and return the modified pdf content.
    Args:
        formatting_args: The formatting arguments to apply to the pdf.
        input_pdf: The path to the PDF to be edited.
    Returns:
        The path to the modified PDF.
    """
    output_pdf = input_pdf[:-4] + "_edited.pdf"
    print("----------------------------\n",output_pdf, "\n")

    # Extract formatting arguments
    text_color = formatting_args.get("text_color")
    font_scale = formatting_args.get("font_scale", 1.0)
    background_color = formatting_args.get("background_color")

    # Create PDF editor object and apply custom formats
    editor = PDFEditor(input_pdf, output_pdf, text_color, background_color, font_scale)
    editor.apply_custom_formats()

    return output_pdf


@tool
def summarize_text(text: str) -> str:
    """Generate a summary of the provided text."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a highly skilled text summarizer."),
            ("human", "Summarize the following text: {}".format(text)),
        ]
    )
    runnable = prompt | llm.with_structured_output(schema=str)
    response = runnable.invoke()
    summary = response
    return summary


# Define the chains
llm = ChatGroq(
    temperature=0.7, model_name="mixtral-8x7b-32768", groq_api_key=GROQ_API_KEY
)
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a highly skilled PDF editor. Your job is to accurately interpret user instructions "
            "and apply the specified formatting to the PDF. Follow the given instructions precisely and "
            "ensure the output is as expected. Only return the modified PDF once the instructions have been fully applied.",
        ),
        (
            "system",
            "Instructions can include changes to background color, text color, and font size. "
            "Apply these changes to the entire PDF. If any attribute is not mentioned in the instructions, leave it unchanged.",
        ),
        (
            "human",
            "Given the instructions: {instructions}, modify the PDF: {input_pdf} accordingly.",
        ),
        ("placeholder", "{agent_scratchpad}"),
    ]
)


output_parser = StrOutputParser()

# Define the tools
formatting_tool = generate_formatting_args
pdf_editor_tool = edit_pdf
summary_tool = summarize_text

# Create the agent
tools = [formatting_tool, pdf_editor_tool, summary_tool]
agent = create_tool_calling_agent(llm, tools, prompt)


# Function to process the user's request
def edit_pdf_from_description(input_pdf, instructions):

    i = 3
    while i > 0:
        try:
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            result = agent_executor.invoke(
                {"instructions": instructions, "input_pdf": input_pdf}
            )
            print("----------------------------\n",result, "\n")
            break
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            i -= 1

    # Define the source and destination paths
    # current_directory = os.getcwd()
    # source_path = os.path.join(current_directory, "edited_" + input_pdf)
    # media_root = settings.MEDIA_ROOT
    # destination_path = os.path.join(media_root, "edited_" + input_pdf)

    # print("----------------------------\n",source_path, "\n")
    # print("----------------------------\n",destination_path, "\n")


    # Move the file
    # shutil.move(source_path, destination_path)

    return input_pdf[:-4] + "_edited.pdf"


# def main():
#     # Example usage
#     input_pdf = "apple_small.pdf"
#     instructions = "Change the background to black and the text to white."
#     result = edit_pdf_from_description(input_pdf, instructions)
#     print(f"PDF processed successfully. Output saved at: {result}")


# if __name__ == "__main__":
#     main()
