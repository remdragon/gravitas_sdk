# `login` SDK method

The `login` SDK method is used to log in and establish a session with the Gravitas API server

|Attribute|Required|Type|Description|
|-|-|-|-|
|`username`|yes|string|Username of the user to be logged in|
|`password`|yes|string|Password of the user to be logged in|

## Expected return value format

The expected return value format is `None`.
* The class variable `loggedin` is the success (`True`) or failure ('False`) of the login request
* If the login is successful then the class variable `userdata` is a dictionary of the user attributes provided by the API:

|Attribute|Type|Description|Example|
|-|-|-|-|
|`FORCE_PWD_CHANGE`|boolean|Determines if user is forced to change their password|`False`|
|`LAST_ACCT`|integer|The last account that this user accessed|`1`|
|`NEXT_PWNED`|??? or `None`|TODO FIXME: get description for this|`None`|
|`PWD_EXPIRE`|string (formatted as `YYYY-MM-DD` date)|Date that the user's password expires|`2020-10-23`|
|`ROOT`|boolean|The administrative status of the user|`True`|
|`USER`|string|The username of the user|`restuser`|
|`USER_ID`|integer|The user ID number of the user|`2`|
|`expired_pwd`|boolean|Whether or not the user's password is expired|`False`|

## Usage

    sdk.login(
        username = 'restuser',
        password = 'gravitas1234567890'
    )
    print(sdk.loggedin)
    print(sdk.userdata)