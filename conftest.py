import pytest
import os
import Classes as cl
import OAuthSession as auth

@pytest.fixture(autouse=True, scope="session")
def coverage():

    if not os.path.exists("Client_information.yaml"):
        auth.OAuthSession(input("Client_id: "), input("Client_secret: "))
    yield

    if os.path.exists("Test course's title.yaml"):
        course = cl.Course()
        course.load_from_file("Test course's title.yaml")
        if not course.id == None:
            course.auth(auth.OAuthSession())
            course.delete_network_course()
            for j in range( len( course.sections)):
                for i in range( len( course.sections[j].lessons )):
                    course.delete_network_lesson(j, i)
        os.remove("Test course's title.yaml")

