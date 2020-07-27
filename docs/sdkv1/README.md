# Gravitas Python SDK v1
This is version 1 of the gravitas SDK. This includes the legacy/compatibility implementation of Gravitas.

|Attribute|Required|Type|Description|
|-|-|-|-|
|`hoststring`|Required|string|Host connect string
|`protocol`|Optional|string|Protocol used for communication with the Gravitas API server. Options are `https` and `wss` (defaults to `https`).
|`port`|Optional|integer|Port number of the Gravitas API server (defaults to `443`)|
|`ssl_verify_enable`|Optional|boolean|Enables/disables SSL certificate verification (defaults to `True`). **NOTE: in production this must remain as `True`**

## Usage

    from gravsdk import sdkv1
    sdk = sdkv1(
        hoststring = 'https://10.10.10.10:4443', # The port is optional
        ssl_verify_enable = False # This should be `True` in production
    )