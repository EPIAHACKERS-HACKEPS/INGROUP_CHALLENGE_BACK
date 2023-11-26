from dotenv import load_dotenv
import os

load_dotenv()

DEBUG = os.getenv('FLASK_DEBUG', 'False') == '1' or os.getenv('FLASK_DEBUG', 'False') == 1 or os.getenv('FLASK_DEBUG', 'False') == 'True'
SECRET_JWT = "secret"
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASS = os.getenv("MYSQL_PASS")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_DB = os.getenv("MYSQL_DB")
DATABASE_URI = f"mysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
API_PREFIX = "api/v1"

API_TYPE_OPENAI = os.getenv("API_TYPE_OPENAI")
API_KEY_OPENAI = os.getenv("API_KEY_OPENAI")
API_BASE_OPENAI = os.getenv("API_BASE_OPENAI")
API_VERSION_OPENAI = os.getenv("API_VERSION_OPENAI")
MODEL_COMPLETION = os.getenv("MODEL_COMPLETION")
MODEL_CHAT = os.getenv("MODEL_CHAT")
MODEL_ASSISTANT = os.getenv("MODEL_ASSISTANT")
MODEL_EMBEDDING = os.getenv("MODEL_EMBEDDING")

PRIVATE_STORAGE_PATH = os.getenv("PRIVATE_STORAGE_PATH", os.path.join(os.getcwd(), 'private'))


KNOWLEDGE_FILE = os.getenv("KNOWLEDGE_FILE", "knowledge.pdf")

PREFIX_PROMPT = "Extract user stories:"

SEPARATOR_FILE_NAMES = '$'

ASSISTANT_BOT_PROMPT = """
    The assistant has been programmed to help customers to learn more about the XR SHop and create comments. The assistant is placed on XR shop website for customers to learn more about the XR shop and add comments.

    A document has been provided with information on XR shop which can be used to answer the customer's questions. When using this information in responses, the assistant keeps answers short and relevant to the user's query.
    Additionally, the assistant can create new comments based on a given user message, the assitant will divide the message if is about a new feature or a bug, get_all_repositories. When outputting the repositories and key info, markdown formatting should be used for bolding key figures.
    After the assistant has created the repository, they should ask if they want to see the information of all the repositories.

    With this information, the assistant can add a repository via the create_repo function, also pulling in the repositorie name that was mentioned prior. This should provide the name and description of the repository to the create_repo function.
"""

ASSISTANT_CLASSIFICATION_PROMPT = """
As the "User Story Assistant," you are designed to work with diverse data sets in various formats, containing any kind of information relevant to software development or other areas. Your main function is to parse this data, no matter its format, and create structured User Stories. You will analyze conversations, comments, and other forms of data to extract key points, which will then be organized into User Stories with titles, descriptions, and prioritized lists of features and bugs. Each feature and bug you identify will be given a title, a detailed description, and a priority ranking from 1 to 4. Your responses must always be structured in a specific JSON format, ensuring clarity and consistency in how information is presented. Your goal is to aid in planning and tracking development processes, making sense of complex information, and providing clear, actionable User Stories. Example format json response:
{
    "user_story": {
        "title": "user story title",
        "description": "user story description",
        "items":[
            {
                "type": "bug",
                "title": "bug title",
                "description": "bug description",
                "priority": 1
            },
            {
                "type": "feature",
                "title": "feature title",
                "description": "feature description",
                "priority": 4
            }
        ]
    }
}
Remember that can be multiple items inside an user story
"""