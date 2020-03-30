*** Settings ***
Library      RPA.Tasks    schema=${SCHEMA_FILE}

*** Variables ***
${SCHEMA_FILE}  ${CURDIR}${/}..${/}resources${/}tasks_schema.json
${CURRENT}      ${1}
${TARGET}       ${5}

*** Tasks ***
Check if satisfied
    [Documentation]    Checks if we've reached the target number or not
    ...
    ...    This is just something else to show a multiline docstring.
    ...    Lorem ipsum etc.
    Log    I'm trying to count to ${TARGET}
    #Should be true    ${CURRENT} >= ${TARGET}    Value is too low

This will not run
    Fail    This should never run

Increment current number
    ${CURRENT}=    Evaluate    ${CURRENT} + 1
    Set suite variable    ${CURRENT}
    Log    Number is now ${CURRENT}
    #Set next task    Check if satisfied

Satisfaction
    Log    Those are some good numbers!

Keyword conditional
    Jump to task if keyword fails   Increment current number
    ...    Should be true    ${CURRENT} >= ${TARGET}
    Log    Number was as expected
    Jump to task    Satisfaction
