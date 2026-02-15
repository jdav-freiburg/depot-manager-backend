# Local Authentication Service 

---

1. Run auth stack with docker compose up, the first start takes some time
2. go to http://localhost:8080/if/flow/initial-setup/
3. create an admin account, remember your credentials!
3. create a scope mapping:
    - Go to `Customization -> Property Mappings -> Create -> Scope Mapping`
    - Enter a meaningful name
    - Set scope name to: `depot_roles`
    - Enter the following expression:
    ```python
    return {
      "roles" : ["admin", "manager"]
    }
    ```
4. create the local auth application with the following base settings:
    - client type: `public`
    - Redirect URL: `.*` (WARNING: Do NOT use in production, as this can have severe security risks)
    - Access Token Validity: `minutes=60` Choose something reasonable, otherwise you would have to login
      all the time
    - Under `Advanced protocol settings` add the scope from (3) to your selected scopes

5. Add the client id in the frontend and backend
