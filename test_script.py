import json
import requests
from datetime import datetime, timedelta

nudge_json = {
    "osVersionRequirements": [
        {
            "aboutUpdateURL": "https://support.apple.com/en-us/109035",
            "requiredInstallationDate": "2024-03-29T22:00:00Z",
            "requiredMinimumOSVersion": "14.4.1",
            "targetedOSVersionsRule": "14",
        },
        {
            "aboutUpdateURL": "https://support.apple.com/en-us/106337",
            "requiredInstallationDate": "2024-03-29T22:00:00Z",
            "requiredMinimumOSVersion": "13.6.6",
            "targetedOSVersionsRule": "13",
        },
        {
            "aboutUpdateURL": "https://support.apple.com/en-us/106339",
            "requiredInstallationDate": "2024-03-29T22:00:00Z",
            "requiredMinimumOSVersion": "12.7.4",
            "targetedOSVersionsRule": "12",
        },
    ],x
}
# Get JSON from SOFA
sofa_json = requests.get("https://sofa.macadmins.io/v1/macos_data_feed.json")

# Update Nudge JSON with SOFA data only if a response is received
if sofa_json.status_code == 200:
    sofa_data = sofa_json.json()

    latest_os_versions = sofa_data["OSVersions"]

    # Update Nudge JSON with the latest versions and release dates
    for os_version in latest_os_versions:
        latest_version = os_version["Latest"]["ProductVersion"]
        print(latest_version)
        latest_release_date = os_version["Latest"]["ReleaseDate"]

        # Format latest_release_date so it can be manipulated
        date_obj = datetime.fromisoformat(latest_release_date)

        # Use timedelta to offset the release date for the production schedule
        time_delta = timedelta(days=7, hours=22)
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


print(nudge_json)
