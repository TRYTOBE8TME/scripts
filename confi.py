{
"protocol":"openid-connect",
"name": "https://aws.amazon.com/tags",
"protocolMapper": "oidc-usermodel-attribute-mapper",
"config": {
"user.attribute":"https://aws.amazon.com/tags",
"claim.name":"https://aws\\.amazon\\.com/tags",
"jsonType.label": "JSON",
"access.token.claim": true,
"userinfo.token.claim": true,
"multivalued": true
}
}
