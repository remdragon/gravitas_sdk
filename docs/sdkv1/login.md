# `login` SDK method

The `login` SDK method is used to log in and establish a session with the Gravitas API server

|Attribute|Required|Type|Description|
|-|-|-|-|
|`username`|yes|string|Username of the user to be logged in|
|`password`|yes|string|Password of the user to be logged in|

## Expected return value format

The expected return value format is `bool` to indicate the success or failure of the login.

## Usage

    success = sdk.login(
        username = 'restuser',
        password = 'gravitas1234567890'
    )