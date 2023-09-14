#################
# Miscellaneous #
#################
def test_readiness(test_client):
    response = test_client.get("/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


######################
# Test course router #
######################
def test_get_course(test_client):
    response = test_client.get("/api/v1/course")
    print(response.json())