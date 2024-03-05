import pytest
import os
import Course as co
import OAuthSession as auth

@pytest.fixture(autouse=True, scope="session")
def clean():
    yield
    # if os.path.exists("Check_file.yaml"):
    #     os.remove("Check_file.yaml")
    if os.path.exists("Test course's title.yaml"):
        course = co.Course()
        course.load_from_file("Test course's title.yaml")
        course.auth(auth.OAuthSession())
        course.delete_network_course()
        for j in range( len( course.structure["Course"]["Sections"])):
            for i in range( len( course.structure["Course"]["Sections"][j]["Lessons"] )):
                course.delete_network_lesson(j, i)
        os.remove("Test course's title.yaml")

