# ChatPDF AI-PDF Toolkit

ChatPDF is an advanced web application designed to provide an extensive toolkit for interacting with PDFs. Built using Django for the backend and React for the frontend, ChatPDF leverages state-of-the-art AI technologies, including LangChain and LangGraph with Large Language Models (LLMs).

## Main Use Cases

1. **Text to PDF Generator**
   - Create new PDFs by describing what they should contain, similar to chatting with ChatGPT.
   - Specify custom formatting such as background color, font size, and more.

2. **Interactive PDF Editor**
   - Edit existing PDFs based on text descriptions.
   - Upload your PDF and interact with it side by side.
   - Ask the chatbot to make edits in real-time, such as:
     - Changing the background color, font color, and font size.
     - Adding new pages with specified content.
     - Deleting and updating existing text.
     - Answering questions with responses inserted within the PDFs.
   - Watch your PDF being edited visually and download the new version once satisfied.

## Features

- **Automated PDF Generation**: Automatically generate new PDFs based on user descriptions.
- **Detailed PDF Edits**:
  - **Text Changes**: Modify existing text within PDFs.
  - **New Text Insertion**: Add new text to PDFs.
  - **Page Appending**: Append new pages to existing PDFs.
  - **Font and Background Adjustments**: Change the font and background settings of PDFs.
- **Question Answering**: Utilize retrieval-augmented generation techniques to accurately answer questions related to PDF content and insert responses within the PDFs.

## Technology Stack

### Backend
- **Django**: A high-level Python web framework that encourages rapid development and clean, pragmatic design.
- **LangChain**: A library for developing applications powered by language models.
- **LangGraph**: A library for building stateful, multi-actor applications with LLMs, used to create agent and multi-agent workflows.

### Frontend
- **React**: A JavaScript library for building user interfaces.

## Installation

To set up the project locally, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AKKI0511/ChatPDF.git
   ```

2. **Backend Setup**:
   - Create a virtual environment:
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
     ```
   - Install the dependencies:
     ```bash
     cd backend
     pip install -r requirements.txt
     ```
   - Apply migrations:
     ```bash
     python manage.py makemigrations
     python manage.py migrate
     ```
   - Run the development server:
     ```bash
     python manage.py runserver
     ```

3. **Frontend Setup**:
   - Navigate to the frontend directory:
     ```bash
     cd frontend
     ```
   - Install the dependencies:
     ```bash
     npm install
     ```
   - Start the development server:
     ```bash
     npm start
     ```

## Usage

1. **Access the Application**
   - Open your web browser and navigate to `http://localhost:8000` to start using ChatPDF.

2. **Text to PDF Generator**
   - Use the interface to describe what the new PDF should contain, including custom formatting such as background color, font size, etc.

3. **Interactive PDF Editor** (Currently under development)
   - Upload a PDF and interact with it side by side.
   - Use the chatbot to make edits such as changing background color, font color, font size, adding new pages, deleting and updating text, and inserting answers to questions.
   - Watch the edits visually in real-time and download the updated PDF once satisfied.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Django](https://www.djangoproject.com/)
- [React](https://reactjs.org/)
- [LangChain](https://python.langchain.com/v0.2/docs/introduction/)
- [LangGraph](https://www.langchain.com/langgraph)

## Note

This project is currently under development. We are continuously working on improving the AI capabilities to perform better.
