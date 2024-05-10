import pytest
import os
from src.API.Classes import Course
from src.API.OAuthSession import OAuthSession
from requests.exceptions import ConnectionError

@pytest.fixture(autouse=True, scope="session")
def coverage():

    if not os.path.exists("src/API/Client_information.yaml"):
        try:
            OAuthSession(input("Client_id: "), input("Client_secret: "))
        except ConnectionError:
            raise ConnectionError("Failed to resolve stepic.org. Check your Internet connection")
    yield

    if os.path.exists("src/API/Test course's title.yaml"):
        course = Course()
        course.load_from_file("Test course's title.yaml")
        if course.id:
            course.auth(OAuthSession())
            course.delete_network()
            for j in range( len( course.sections)):
                for i in range( len( course.sections[j].lessons )):
                    course.delete_network_lesson(j, i)
        os.remove("src/API/Test course's title.yaml")

