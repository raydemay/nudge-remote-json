# nudge-json

## Description
[Nudge](https://github.com/macadmins/nudge) supports multiple ways of setting the configuration: an MDM-provided configuration profile, a local .plist, a local JSON, or a remote JSON. The MDM configuration profile take precedence. This project utilizes this feature. A configuration profile is deployed via Jamf Pro that configures every Nudge setting except any `osVersionRequirements` property. JSON files stored in this repository are used as the Remote JSON objects that Nudge reads to determine the required OS version and install deadline. The JSON files are automatically updated when a new version of MacOS is released. This is done by reading a JSON file served by [SOFA](https://sofa.macadmins.io/), which provides the most current MacOS version information.

## Usage
A custom JSON schema for Jamf Pro and sample configuration profile are available. The configuration file will define all properties except the OS Version Requirements.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## License
GNU General Public License v3.0

## Project status
This is a work in progress. It was initially meant to be an Azure Function with the JSON stored in Azure Blob Storage, so there is some work being done to convert the automation and how the JSON files are accessed.
