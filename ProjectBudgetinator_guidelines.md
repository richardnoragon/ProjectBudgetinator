# ProjectBudgetinator

project     ProjectBudgetinator
author      Richard Noragon
created     tbd

## Project Code Guidelines and Instructions

## Purpose of This Document

This document provides guidelines and standards for code generation,
development and testing to maintain consistent, high-quality across the project.
User experience and reliability is focal point. With that in mind,
development scaling and trouble shooting are forward thought in this project.
It is designed to used with Richard and AI Pair Programer.

## General

The ProjectBudgetinator is designed to improve the workflow, 
reduce the workload and ultimitly the use of sharing microsoft excel amoung colleages.
In its final form the ProjectBudgetinator will allow for compfortable
creation of reports and analysis aobuve what is known today,
short it will become State of the Art (SOTA).
This project will adhere to the European Digital Services Act (DSA),
this will taken in consideration in all phases of the project.
After the completetion of each phase a review will be perfromed to see if objectives are the same or changed and if they objectives have been reached and if the overall project guidelines are valid and met

## Project Overview

* This project is designed for users basic office IT skills assocated with 2025.
* This project is designed to work with files with a format compatible
to microsoft excel 1997
* This project consists of four major Phases.

## Project Assumtions:

* All users basic office IT skills assocated with 2025.
* All users can understand basic english computer menus
* All users are familar with standard office programs
* // TODO users could be color blind do not only rely on color of text  user option
* Multiple users multiple files multiple computers,
hence the versioning and logging is necessary,
this will be covered later in the document

### Phase 1 Objectives

[x] create a python project enviroment
[x] install necessary python packages
[x] project files folders and workspaces will be created in the IDE
[x] github repository will be created 
[x] the hub gui will be created,
[x] Create Start methods / function 
[x] Create Exit methods / function
[x] Create place holders for the other functions
[x] after all Objectives of Phase 1 have been completed the guthub repository will be updated
[x] update phase 1 objectives checklist

#### Start

after starting the program the user will be presented with the following
dialog (splash sqreen) 
If new user then a welcome will be shown and the folder structure will be implemented,
and a diagnostics run. new user is dertermied, when there is no ProjectBudgetinator file structure.
If already a user then the a welcome back, which the user can disable, will be shown
and diagnsitics will be run either verbose or minimal display user option

a check will be performed if this is the first time this program been run
on this computer. (how)
   if first time say welcome
   then i will be creating some directries in your user folder if you do not mind
   (otherwise i will not be able to operate) -> exit

while the loading process a staus bar will be shown, 1 from 2 from and so on

The directories will be checked and a status will be returned

Sample User Directory Structure
ProjectBudgetinator/
│
├─ workbooks/                   # Original or user-edited Excel files
│   ├─ workbook_v1.xlsx
│   ├─ workbook_v2.xlsx
│
├─ logs/
│   ├─ system/                  # Diagnostic and runtime logs
│   │   └─ diagnostic.log
│   ├─ user_actions/            # User-driven events like opens, saves
│   │   └─ user_journal_20250622.json
│   └─ comparisons/
│       ├─ comparison_20250622_2358.json
│       └─ snapshots/
│           ├─ snapshot_v1_sales_q2.json
│           ├─ snapshot_v2_sales_q2.json
│
├─ config/
│   ├─ user.config.json         # Preferences, themes, recent files
│   ├─ backup.config.json       # Backup frequency, rotation, archive location
│   └─ diagnostic.config.json   # Debug mode, logging verbosity, etc.
│
├─ backups/
│   ├─ workbook_v1_backup_20250620.xlsx
│   └─ backup_log.json
│
└─ templates/
    ├─ basic_template.xlsx
    └─ sales_template_q2.xlsx

Sample Startup Status
╔══════════════════════════════════════╗
║     🛠 WorkbookApp Startup Check     ║
╚══════════════════════════════════════╝

📁 Directory Check
✅ workbooks/          …exists
✅ logs/system/        …ready
✅ logs/user_actions/  …ready
🆕 logs/comparisons/snapshots/  …created
✅ config/             …ready
⚠️  backups/            …missing (created default)
✅ templates/          …exists

🧾 Config File Check
✅ user.config.json     …loaded successfully
⚠️  backup.config.json   …not found (restored defaults)
🆕 diagnostic.config.json …created new with defaults

🗃 Log Integrity
⚠️  2 comparison logs from v0.8 detected  → marked as legacy
✅ latest snapshot valid (2025-06-22)

💬 Summary
Startup passed with 2 warnings and 2 recoveries.
New folders/configs have been generated where needed.

📌 All systems go — launching interface...

a check will be performed if another instance is running, if another
instance(s) are running a dialog will appear showing each instance (ID)
and the files they have open.

validate—it and heal

Missing folders? Create on the spot.

Missing config? Default generated.

Corrupted config? Backed up and replaced with defaults.

Legacy or deprecated items? Optionally scanned and logged for user review.

prompt the user at startup if something unexpected was altered:
“We restored your backup.config.json from default due to errors. View details?”

then the GUI will be presented

### Phase 1 GUI

ProjectBudgetinator Hub Window Title
File                    Top Menu Item
    -------              dividing line
   Backup               Drop Down Menu Item 1
    -------              dividing line
   Clone                Drop Down Menu Item 2
   -------              dividing line
   Compare              Drop Down Menu Item 3
   -------              dividing line
   Create from scratch  Drop Down Menu Item 4
   Create from template Drop Down Menu Item 5
   -------              dividing line
   Modify               Drop Down Menu Item 6
   -------              dividing line
   Restore               Drop Down Menu Item 7
      -------              dividing line
   Exit                 Drop Down Menu Item 8
Preferences             Top Menu Item
Tools                   Top Menu Item
Help                    Top Menu Item


#### Exit

The progam saves all changes after asking the user, then closes.

### Phase 2 Overview

Phase 2 is broken down into multiple Sub-Phases. after the succesful complition of each Sub-Phase the projsect files will be updated before continuing. If an item cannot be completed and placeholder Method/function will be used. These Methods/Functions will be changed later wehn apporiate.

### Phase 2 Objectives

#### Preferences [Menu Item]

the user will have the option to merge user config files for their user only
[x] the user preferences will be saved in a json file
[x] the user can select light or dark mode, option will be saved in user preferences
[x] users can select verbose (default) or silent startup diagnostic,
option will be saved in user preferences
[x] the user will be able to select from multiple user config files, option will be saved in user preferences
[x] users can create a new user config, option will be saved in user preferences
the user will have the option to merge user config files for their user only
[x] A merge_configs() method that takes the union of keys (or prioritizes user-edited fields).
An interactive diff/merge UI or console prompt:
“Found similar settings in backup. Merge them into your current configuration?”
[x] an option to delete user preferences will be created with warning a new default will be created
[x] the user can choose the default locataiion of where to look for opening files,
also user can say remember last or leave to default as dscribed in folder strutce section.
[x] user can select not to have welcome screen, option will be saved in user preferences
[x] user can slecet a new location to save files, the user can change this later
[x] update Phase 2 Preferences checklist

##### Diagnostics [Menu Item]

[x] when the button is clicked a dashboard of the start up diagnostics will shown, allowing the user to select each catagory. when a user selects a category, detailed informmation will be displayed.

##### Help [Menu Item]

// Help menu implemented
[x] create a place holder which returns a text window
title "Hub" bold text "Attention needed" standard text "Help menu"


##### Dev Tools [Menu Item]

[x] a developer mode will also be implemented (see dev_tools.py). It is a drop down menu item under Tools menu, above Diagnostics. Includes debug console, developer mode toggle, and placeholder integration.

### Phase 2 File handling

* changes should always be shown, displayed
or highlighted before saving. the colors will be gradient with newest changes
being  brightest getting fainter each step the last 3 changes will be
displayed this way.
* by changes to a file a go back and go forward icon should always be offered
* when the file is opened it will look for PrjectBudgetinator tab, if not found
it will be created and Versioning info placeholder will be inserted
// TODO Versioning Info

[ ] versioning see attached file versioning_upgrading_py.md
[ ] Logging see the section Error Handling later in this document
* monitoring
* backup methods will be implemented
* // TODO make option for languages also to save in options

* When opening a file it will ensure that it is really of the specified file type progess result and status will be shown
* A check to see if the file is locked will be performed result and status will be shown. if file is locked the user can eitehr abort or must select a new file name to save it, once this has been done the file will be opened
* When opening a file for the first time initalize it, the following assumations will be made
* 1) the Partner sheet name will start with a "P" here the workpackages will start with integers till a sum is found


#### Clone

[x] When Clone is selected, a dialog opens to select a file, then a second dialog allows the user to select where the clone will be saved, with options to edit the directory, name, and file ending, and to enter a project name. (GUI flow implemented)


#### Compare

[x] The user can choose up to three files to compare. The first file is by default the reference file. The user can choose which file is the reference file, and the display of the differences will refresh. (GUI implemented: file selection, reference selection, and difference display)

#### Create from Scratch

[x] When Create from Scratch is selected, the user is prompted to select a path, input a name and file ending, or go back. (GUI flow implemented)

#### Create from Template

[x] When Create from Template is selected, the user is prompted to select a path and input a template or already created file (with validation), or go back. (GUI flow implemented)

#### Modify

#### Add partner
[x] 
when adding a partner the worksheet name will consist of the partner number,
a space then the partner acronym (the letter P and a positive integer) if the partner exsists, then a dialoge wiilll appear saying partner already exsist would you like to edit or reviewthis partner, or add a different new partner. If the user selects edit or review option the partneer table will be opened for editing. if the user selects add a new different partner a  new dialog will appear listing the partners and a dialog where the user can enter the new partner

the following information will be asked when add partner button is selected
in a new dialog box:
{
  "project_partner_number": "string",
  "partner_identification_code": "string",
  "partner_acronym": "string",
  "name_of_beneficiary": "string",
  "country": "string",
  "role": "string",
  "personnel_costs": "number",
  "subcontracting_costs": "number",
  "purchase_costs_travel_and_subsistence": "number",
  "purchase_costs_equipment": "number",
  "purchase_costs_other_goods_works_and_services": "number",
  "financial_support_to_third_parties": "number",
  "internally_invoiced_goods_and_services": "number",
  "indirect_costs": "number",
  "total_eligible_costs": "number",
  "funding_rate": "number",
  "maximum_eu_contribution_eligible_costs": "number",
  "requested_eu_contribution_eligible_costs": "number",
  "max_grant_amount": "number",
  "income_generated": "number",
  "financial_contributions": "number",
  "own_resources": "number",
   "name_subcontractor_1": "string",
  "person_months": {
    "wp1": "number",
    "wp2": "number",
    "wp3": "number",
    "wp4": "number",
    "wp5": "number",
    "wp6": "number",
    "wp7": "number",
    "wp8": "number",
    "wp9": "number",
    "wp10": "number",
    "wp11": "number",
    "wp12": "number"
  },
  "subcontractors": [
    {
      "name": "string",
      "sum": "number",
      "explanation": "string"
    }
  ],
  "purchase_costs_travel": "number",
  "purchase_costs_equipment_alt": "number",
  "purchase_costs_other": "number",
  "other_costs_third_party": "number",
  "other_costs_internal": "number",
   "sum_subcontractor_1": "string",
   "explanation_subcontractor_1": "string",
  "other_explanation_self": "string"
}
after the information is added a comit or cancel can be preseed

when commit is pressed a new work sheet will be added, with the name 'P' partner number
and a space then partner acronym.

The partner P1 (Coordinator) cannot be chosen. P1 and any acronym cannot be chosen.

only the values will be added, as follows
project_partner_number": "string" "D2:E2",
  "partner_identification_code": "string" "D4:E4",
  "partner_acronym": "string" "D3:E3",
  "name_of_beneficiary": "string" "D13",
  "country": "string" "D5:E5",
  "role": "string" "D6:E6",
  "personnel_costs": "number", // TODO remove and add Formula
  "subcontracting_costs": "number",
  "purchase_costs_travel_and_subsistence": "number",
  "purchase_costs_equipment": "number",
  "purchase_costs_other_goods_works_and_services": "number",
  "financial_support_to_third_parties": "number",
  "internally_invoiced_goods_and_services": "number",
  "indirect_costs": "number",
  "total_eligible_costs": "number",
  "funding_rate": "number",
  "maximum_eu_contribution_eligible_costs": "number",
  "requested_eu_contribution_eligible_costs": "number",
  "max_grant_amount": "number",
  "income_generated": "number",
  "financial_contributions": "number",
  "own_resources": "number",
   "name_subcontractor_1": "string",
  "person_months": {
    "wp1": "number",
    "wp2": "number",
    "wp3": "number",
    "wp4": "number",
    "wp5": "number",
    "wp6": "number",
    "wp7": "number",
    "wp8": "number",
    "wp9": "number",
    "wp10": "number",
    "wp11": "number",
    "wp12": "number"
  },
  "subcontractors": [
    {
      "name": "string",
      "sum": "number",
      "explanation": "string"
    }
  ],
  "purchase_costs_travel": "number",
  "purchase_costs_equipment_alt": "number",
  "purchase_costs_other": "number",
  "other_costs_third_party": "number",
  "other_costs_internal": "number",
   "sum_subcontractor_1": "string",
   "explanation_subcontractor_1": "string",
  "other_explanation_self": "string"

// TODO add here a way to count the number of workpackages from ProjectBudgetinator tab
// TODO when files are opened a backup is created
// TODO decide how startup diagnostic window should appear
// TODO make the entry of the partner number and acronym a single entry

#### Edit partner

a dialog will appear asking for partner number and acronym,
if the value is correct the worksheet with this name will be opened for editing
all the fields will be avlble for editning  after commit is pressed all
formulas and fields of the entire will be updated accodinlgy
the present values will be deplayed to the left of the field where the new values are being enterd

#### Delete partner

a dialog will appear asking for partner number and acronym,
if the value is correct the worksheet with this name will be deleted
// TODO find out which other values need to be deleted
 after commit is pressed all
formulas and fields of the entire will be updated accodinlgy

#### Add work package

a dialog will appear showing the current number of work packages it will display
a "change to" field with commit and cancel buttons

 "person_months": {
    "wp1": "number",
    "wp2": "number",
    "wp3": "number",
    "wp4": "number",
    "wp5": "number",
    "wp6": "number",
    "wp7": "number",
    "wp8": "number",
    "wp9": "number",
    "wp10": "number",
    "wp11": "number",
    "wp12": "number"
  },

when a work package is added,  or deleted this will then be changed for all partners,
if the change deletes a field ??? which is not null or zero,
 then a message will be created, showing a list of partners where
 the list is not mull or zereo
at the end the user can commit or cancel

#### Delete work package

woark packages are designated as WP1 for Work Package 1,
WP2 for Work Package 2 and WP3 for Work Package 3 etc.

a dialog will appear and ask the user to enter the number of the workpackages
to be deleted, that is WP1, WP3 etc.

if the user should attemt to delete a field in which the the ??? value is not
null or zero than a dialog box will appear with a message that for the for these
users there is a value???

#### Edit work package

this will allow users to edit one or more packages for multiple partners. the user
can select multiple partners and already established workpackages. 
the dialog box will have commit and cancel buttons



outline a database structure

### Phase 3  Objectives

the introduction of an mysql database. Each time a file is handled by
the program it will be added to the database
strat transition to centralized self hosted Web application

introduce database stucture

#### Phase 4 

a self hosted web application
desgin and produce custom reports

## Technology Stack

### Phase 1 Technology Stack

- **Programming Languages**: [Python 3.13.5]
- **Frameworks/Libraries**: [tkinter 8.6, pandas 2.3.0]
- **Build Tools**: [PyInstaller 6.14.1] [Breifcase 0.3.23]
- **Database**: [MySQL 8.43.0]
- **Other Technologies**: [tbd]

### Phase 2 Technology Stack

see Phase 1

### Phase 3 Technology Stack

see Phase 1

### Phase 4 Technology Stack

open will be determined at that time

## Project Structure

### Phase 1 IDE Project Structure

project-root/
├── src/               # Source code
├── tests/             # Test files
├── docs/              # Documentation
├── config/            # Configuration files
│   ├── development.env    # Development environment variables
│   ├── testing.env        # Testing environment variables
│   └── production.env     # Production environment variables
├── build/             # Build output
└── README.md          # Project readme

### Phase 2 Project Structure

### Phase 3 Project Structure

### Phase 4 Project Structure

## Coding Standards

### General Guidelines

- Follow the style guidelines for the respective languages
- If there is no style guide for a language in project,
- you will state this in the output
- Use meaningful and descriptive names for variables, functions, and classes
- Keep functions small and focused on a single responsibility
- Document complex logic with appropriate comments
- Write code that is readable and maintainable
- Ensure code compatibility with existing project versions
- Prioritize version/release choices that maintain compatibility over newer options
  with potential compatibility risks

### Language-Specific Guidelines

#### [Python]

use style guides

#### [Language 2]

use style guide

### Error Handling

1. Guidelines for handling errors and exceptions:
   - Define how errors should be classified (e.g., critical, recoverable)
   - Set up consistent methods for detecting, catching, and resolving exceptions
   - Provide clear instructions for developers on how to gracefully handle failures
   - Ensure that errors don't crash the system and maintain application stability

2. Logging requirements:
   - Define what information should be logged
   - (e.g., timestamps, error type, affected modules)
   - Specify log levels (e.g., info, warning, error, critical)
   - Determine where logs should be stored (e.g., local files, centralized servers)
   - Ensure compliance with privacy and security standards by 
   - omitting sensitive data in logs
 -  log files will be written in the users directory, sub directory "ProjectBudgetinator",
  sub directory "Log Files" the log files will begin with the date in the format
  of day-month-year-error level
  the last 10 log files will be kept irrelevelnat of the date
  the error levels are:
  - DEBUG – Detailed info for diagnosing problems. Useful during development or when debugging edge cases.
- INFO – General events in the program flow (e.g., “Data import started”, “5 files processed”).
- WARNING – Something unexpected, but not harmful (e.g., deprecated API usage, missing optional config).
- ERROR – A problem that prevented part of the program from functioning (e.g., file not found, failed database connection).
- CRITICAL – Severe issues causing the entire application to fail or exit (e.g., corruption detected, essential service down).

## Testing Requirements

1. Unit testing expectations:
   - Write tests for each function or module to validate expected outputs for
   -  various inputs
   - Ensure that edge cases and error scenarios are adequately tested
   - Utilize automated testing tools to run unit tests consistently
   - Maintain clear documentation for each unit test for future reference

2. Integration testing requirements:
   - Create tests that validate data flow and interaction between connected components
   - Test interfaces between software modules, external systems, or APIs
   - Identify and fix issues like mismatched data types or incorrect dependency handling
   - Perform integration tests after major updates or changes to the system architecture

3. Test coverage goals:
   - Define acceptable test coverage thresholds (e.g., 80% code coverage
   -  for critical modules)
   - Prioritize coverage for high-risk or business-critical areas of the application
   - Continuously monitor and report test coverage metrics using appropriate tools
   - Strive for a balance between high test coverage and practical resource constraints

## Documentation Standards

1. Document all public APIs, classes, and methods:
   - Ensure that every public API, class, and method has comprehensive documentation
   - Include details such as purpose, input parameters, output values, return types,
     and any exceptions thrown
   - Use a consistent format or style guide to maintain uniformity across documentation

2. Include usage examples for complex functionality:
   - Provide clear examples demonstrating how to use APIs or methods
   - Include both minimal and advanced use cases
   - Use concise, well-commented code snippets or diagrams where necessary

3. Keep documentation up-to-date when changing code:
   - Make updating documentation a mandatory step in the development process
   - Automate checks to flag outdated documentation tied to changed code sections
   - Conduct periodic audits to ensure documentation
   -  reflects the current state of the codebase

## Version Control Practices

- [Branch naming convention]
- [Commit message format]
- [Pull request process]

## Code Review Process

### Code Review Checklist

- [ ] Does the code follow project standards and guidelines?
- [ ] Is the code well-tested?
- [ ] Is the documentation sufficient and up-to-date?
- [ ] Are there any potential security issues?
- [ ] Is the code optimized for performance?
- [ ] Are error cases properly handled?

### Code Review Best Practices

**Do**
- Assume competence & goodwill
- Discuss in person when there's disagreement
- Explain why changes are needed, not just what is wrong
- Ask for the why if something is unclear
- Find an end to reviews rather than dragging them out
- Reply within a reasonable timeframe
- Mention the positives, not just issues

**Don't**
- Don't shame people
- Don't use extreme or very negative language
- Don't discourage tool use
- Don't bikeshed (focus on trivial matters while missing important issues)

## Security Guidelines

- [Input validation requirements]
- [Authentication/authorization best practices]
- [Data protection requirements]
- [Known security risks to avoid]

## Performance Considerations

- [Performance targets]
- [Resource usage guidelines]
- [Optimization priorities]

## Accessibility Requirements

- [Accessibility standards to follow]
- [Testing tools for accessibility]

## Deployment Process

- [Staging environment details]
- [Deployment procedures]
- [Post-deployment verification steps]

## Monitoring and Logging

* Monitoring and logging will be kept in user specfic json files, see folder structure section

## Dependencies Management

1. How to Add New Dependencies:
   - Specify the process for introducing new dependencies into the project
   - Verify library licenses and document changes in the codebase
   - Ensure compliance with project guidelines or team protocols

2. Versioning Policy:
   - Define how dependency versions are managed (e.g., semantic versioning)
   - Establish procedures for handling deprecated or updated versions

3. Security Scanning Requirements:
   - Outline how dependencies are regularly scanned for vulnerabilities
   - Include policies for responding to security alerts
   - Establish practices for maintaining project integrity with minimal disruption

## Contact Information

- **Project Lead**: [Richard] ([contact info])
- **Technical Lead**: [Richard] ([contact info])
- **QA Lead**: [Richard] ([contact info])
- **Test Automation Lead**: [USER1] ([contact info])
- **Additional Resources**: // TODO [Links to internal documentation, wikis, etc.]

---
