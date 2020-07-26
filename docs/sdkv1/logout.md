# `logout` SDK method

The `logout` SDK method is used to perform a logout for the currently logged in user.

## Expected return value format

The expected return value format is `Tuple[bool, Dict[str,str]]`.
* The resulting tuple's first position is the success (`True`) or failure ('False`) of the logout request
* The resulting tuple's second position will always be a dictionary with a `rows` element that is an empty array.

## Usage

    sdk.logout()