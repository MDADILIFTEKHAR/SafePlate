import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.init_db import init_db

@pytest.fixture(scope="module")
def client():
    init_db()
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["database"] == "ok"
    assert "ollama_available" in data
    assert "demo_mode" in data

def test_profile_get_and_put(client):
    res = client.get("/api/profile")
    assert res.status_code == 200
    profile = res.json()
    assert profile["name"] == "Aisha"
    assert "Peanut" in profile["allergies"]

    # Update profile
    update_payload = {
        "name": "Aisha Updated",
        "daily_budget": 160.0,
        "max_cooking_time_minutes": 25,
        "spice_level": "Medium",
        "cuisines": ["Indian"],
        "allergies": ["Peanut", "Tree nuts", "Sesame"],
        "dietary_preference": "Vegetarian",
        "disliked_ingredients": ["Bitter gourd"]
    }
    put_res = client.put("/api/profile", json=update_payload)
    assert put_res.status_code == 200
    data = put_res.json()
    assert data["name"] == "Aisha Updated"
    assert data["daily_budget"] == 160.0
    assert "Sesame" in data["allergies"]

    # Revert back to Aisha default
    revert_payload = {
        "name": "Aisha",
        "daily_budget": 150.0,
        "max_cooking_time_minutes": 30,
        "spice_level": "Low/medium",
        "cuisines": ["Indian"],
        "allergies": ["Peanut", "Tree nuts"],
        "dietary_preference": "Vegetarian",
        "disliked_ingredients": []
    }
    client.put("/api/profile", json=revert_payload)

def test_pantry_crud(client):
    # Add pantry item
    add_res = client.post("/api/pantry", json={"name": "Garlic", "quantity": "1 bulb", "category": "Vegetables"})
    assert add_res.status_code in [200, 201]
    item = add_res.json()
    assert item["name"] == "Garlic"
    item_id = item["id"]

    # List pantry
    list_res = client.get("/api/pantry")
    assert list_res.status_code == 200
    names = [i["name"] for i in list_res.json()]
    assert "Garlic" in names

    # Delete pantry item
    del_res = client.delete(f"/api/pantry/{item_id}")
    assert del_res.status_code == 200

def test_safety_check_scenarios(client):
    # Action 2: peanut butter -> AVOID
    res_pb = client.post("/api/safety/check", json={"query": "peanut butter"})
    assert res_pb.status_code == 200
    assert res_pb.json()["status"] == "AVOID"

    # Action 3: rice -> SAFE
    res_rice = client.post("/api/safety/check", json={"query": "steamed basmati rice"})
    assert res_rice.status_code == 200
    assert res_rice.json()["status"] == "SAFE"

    # Action 4: cashew -> AVOID (active allergen: Tree nuts)
    res_cashew = client.post("/api/safety/check", json={"query": "roasted cashew nuts"})
    assert res_cashew.status_code == 200
    assert res_cashew.json()["status"] == "AVOID"

    # Cross contamination trace warning -> CAUTION
    res_trace = client.post("/api/safety/check", json={"query": "may contain traces of peanuts"})
    assert res_trace.status_code == 200
    assert res_trace.json()["status"] == "CAUTION"

    # Unknown product -> UNKNOWN
    res_unk = client.post("/api/safety/check", json={"query": "unknown packaged seasoning blend"})
    assert res_unk.status_code == 200
    assert res_unk.json()["status"] == "UNKNOWN"

def test_generate_meal_plan_and_invalidation(client):
    # Generate plan
    res = client.post("/api/meal-plan/generate", json={})
    assert res.status_code == 200
    plan = res.json()
    assert plan["is_valid"] is True
    assert len(plan["meals"]) == 4

    # Verify each meal has required fields
    for meal in plan["meals"]:
        assert meal["name"]
        assert meal["cooking_time_minutes"] <= 30
        assert meal["safety_status"] == "SAFE"
        assert len(meal["ingredients"]) > 0

    # Changing user allergy invalidates current plan
    update_payload = {
        "name": "Aisha",
        "daily_budget": 150.0,
        "max_cooking_time_minutes": 30,
        "spice_level": "Low/medium",
        "cuisines": ["Indian"],
        "allergies": ["Peanut"],  # Changed from Peanut + Tree nuts to only Peanut
        "dietary_preference": "Vegetarian",
        "disliked_ingredients": []
    }
    client.put("/api/profile", json=update_payload)

    # Check meal plan validity
    plan_res = client.get("/api/meal-plan")
    assert plan_res.status_code == 200
    assert plan_res.json()["is_valid"] is False

    # Restore default
    update_payload["allergies"] = ["Peanut", "Tree nuts"]
    client.put("/api/profile", json=update_payload)
