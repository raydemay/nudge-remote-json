import json
import requests
from datetime import datetime, timedelta


def update_json(sofa_data, nudge_json, offset):
    latest_os_versions = sofa_data["OSVersions"]
    # Update Nudge JSON with the latest versions and release dates
    for os_version in latest_os_versions:
        latest_version = os_version["Latest"]["ProductVersion"]
        latest_release_date = os_version["Latest"]["ReleaseDate"]

        # Format latest_release_date so it can be manipulated
        date_obj = datetime.fromisoformat(latest_release_date)

        # Use timedelta to offset the release date for the production schedule
        time_delta = timedelta(days=offset, hours=22)
        new_date = date_obj + time_delta

        # Format the new date object back to the format that Nudge wants
        update_deadline = new_date.isoformat().replace("+00:00", "Z")

        # Update specific keys while preserving others
        for item in nudge_json["osVersionRequirements"]:
            if (
                item["targetedOSVersionsRule"] == os_version["OSVersion"].split()[1]
            ):  # Slitting OSVersion to grab version number and match against targetedOSVersionsRule
                item["requiredMinimumOSVersion"] = latest_version
                item["requiredInstallationDate"] = update_deadline
                break  # Exit inner loop once a match is found
    return nudge_json


# Read existing JSON files
with open("nudge-test.json", "r") as test:
    test_json = json.load(test)

with open("nudge-pilot.json", "r") as pilot:
    pilot_json = json.load(pilot)

with open("nudge-prod.json", "r") as prod:
    prod_json = json.load(prod)

# Get JSON from SOFA
sofa_json = requests.get("https://sofa.macadmins.io/v1/macos_data_feed.json")

# Update Nudge JSON with SOFA data only if a response is received
if sofa_json.status_code == 200:
    sofa_data = sofa_json.json()

    test_json = update_json(sofa_data, test_json, 1)
    pilot_json = update_json(sofa_data, pilot_json, 3)
    prod_json = update_json(sofa_data, prod_json, 7)


# Write JSON fies
with open("nudge-test.json", "w") as test:
    json.dump(test_json, test)

with open("nudge-pilot.json", "w") as pilot:
    json.dump(pilot_json, pilot)

with open("nudge-prod.json", "w") as prod:
    json.dump(prod_json, prod)
