# `login_session_check` SDK method

The `login_session_check` SDK method checks the current user's logged in status. returns a tuple with the following information:

## Expected return value format

A tuple with the following information is returned:

* A boolean that represents whether or not the user is logged in
* A dictionary with user information (if logged in):

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

    status, userdata = sdk.login_session_check()