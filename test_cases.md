# Manual Test Cases — LearnSpace

Run the application with `python app.py` and open `http://127.0.0.1:5000`.

| ID | Scenario | Steps | Expected result |
|---|---|---|---|
| TC_LEARN_01 | Register with valid details | Sign up with a name, unused email, and password of 8+ characters | Account created and dashboard opens |
| TC_LEARN_02 | Register with duplicate email | Register again using an existing email | Clear “account already exists” error |
| TC_LEARN_03 | Invalid email | Enter an invalid email while registering | Clear validation message |
| TC_LEARN_04 | Weak password | Enter fewer than 8 characters | Password validation error |
| TC_LEARN_05 | Login with valid details | Log out and log in with the registered credentials | Dashboard opens |
| TC_LEARN_06 | Wrong password | Log in using the correct email and incorrect password | Invalid email or password message |
| TC_LEARN_07 | Browse courses | Open Explore | Sample courses and lesson counts display |
| TC_LEARN_08 | Search courses | Search for “Python” | Python course appears |
| TC_LEARN_09 | Filter category | Select “Programming” | Only programming courses appear |
| TC_LEARN_10 | View course details | Select a course card | Course description and lesson list display |
| TC_LEARN_11 | Enroll | Log in and select Enroll | Course appears in My Learning |
| TC_LEARN_12 | Duplicate enrollment | Select Enroll again for the same course | Friendly already-enrolled message |
| TC_LEARN_13 | Access lesson without enrollment | Open a lesson URL without enrollment | Access denied with a clear response |
| TC_LEARN_14 | Complete lesson | Enroll, open a lesson, click Mark as complete | Completion message and progress update |
| TC_LEARN_15 | Complete same lesson twice | Click complete again | Progress is not counted twice |
| TC_LEARN_16 | Full course progress | Complete all lessons in a course | Progress reaches 100% |
| TC_LEARN_17 | Persistence | Restart Flask and log in again | Account, enrollment, and progress remain |
| TC_LEARN_18 | Responsive layout | Resize browser to tablet and mobile widths | Layout adapts without horizontal overflow |
| TC_LEARN_19 | Logout | Click Log out | User session ends and login buttons return |
| TC_LEARN_20 | Unknown course | Request `/api/courses/99999` | HTTP 404 with JSON error |
