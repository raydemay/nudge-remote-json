import logging
import json
import requests
from datetime import datetime, timedelta
import azure.functions as func

app = func.FunctionApp()


@app.schedule(
    schedule="0 0 8-17 * * 1-5",
    arg_name="myTimer",
    run_on_startup=True,
    use_monitor=False,
)
def SOAP_Checker(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function executed.")

    import json


def offset_date_if_weekend(date_str):
    """
    Checks if a date string is a weekend (Saturday or Sunday).

    Args:
        date_str: A string representation of the date in YYYY-MM-DD format.

    Returns:
        The original date string if not a weekend or holiday, otherwise the offset date string (YYYY-MM-DD).
    """
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    if date_obj.weekday() == 6:  # Sunday
        return (date_obj + timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )  # Offset by 1 day for Sunday
    elif date_obj.weekday() == 5:  # Saturday
        return (date_obj + timedelta(days=2)).strftime(
            "%Y-%m-%d"
        )  # Offset by 2 days for Saturday
    else:
        return date_str  # No offset for weekdays


def check_for_updates(sofa_data, nudge_json):
    """
    Checks if the ProductVersion in the JSON data has changed compared to the current Nudge JSON.

    Args:
        sofa_data: JSON data from SOFA
        nudge_json: Nudge remote JSON object

    Returns:
        True if the ProductVersion has changed, False otherwise.
    """
    os_versions = sofa_data["OSVersions"]
    for item in os_versions:
        latest_version = item["Latest"]["ProductVersion"]
        for existing_item in nudge_json["osVersionRequirements"]:
            if (
                existing_item["targetedOSVersionsRule"] == item["OSVersion"].split()[1]
            ):  # Match on major version
                if latest_version != existing_item["requiredMinimumOSVersion"]:
                    return True  # Version has changed for this targetedOSVersionsRule
                else:
                    return False  # No version change found


def update_json(sofa_data, nudge_json, offset):
    """
    Updates Nudge remote JSON files with data gathered from SOFA

    Args:
        sofa_data: JSON data from SOFA
        nudge_json: Nudge remote JSON object
        offset: amount of days to add to deadline

    Returns:
        updated JSON to be written to a file
    """
    latest_os_versions = sofa_data["OSVersions"]
    # Update Nudge JSON with the latest versions and release dates
    for os_version in latest_os_versions:
        latest_version = os_version["Latest"]["ProductVersion"]
        latest_release_date = os_version["Latest"]["ReleaseDate"]

        # Format latest_release_date so it can be manipulated
        date_obj = datetime.fromisoformat(latest_release_date)
        check_date_string = date_obj.strftime("%Y-%m-%d")
        offset_date = datetime.strptime(
            offset_date_if_weekend(check_date_string), "%Y-%m-%d"
        )

        # Use timedelta to offset the release date for the production schedule
        time_delta = timedelta(days=offset, hours=22)
        new_date = offset_date + time_delta

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


def main():
    # Read existing JSON file
    with open("nudge-test.json", "r") as test:
        test_json = json.load(test)

    # Get JSON from SOFA
    sofa_json = requests.get("https://sofa.macadmins.io/v1/macos_data_feed.json")

    # Update Nudge JSON with SOFA data only if a response is received
    if sofa_json.status_code == 200:
        sofa_data = sofa_json.json()

        new_version_available = check_for_updates(sofa_data, test_json)
        if new_version_available:
            test_json = update_json(sofa_data, test_json, 10)

    # Write JSON fies
    with open("nudge-test.json", "w") as test:
        json.dump(test_json, test, indent=4)


if __name__ == "__main__":
    main()
