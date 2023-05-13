# COMP.SEC.300 Project work

## Introduction
This work was done for [Secure Programming](https://www.tuni.fi/en/study-with-us/secure-programming-fitech) course at Tampere University. The result of the project was a password manager storing encryted passwords into a mongo database.

**The work is not based on any previous works.**

## Structure  
    root
    |   - .env
    │   - .gitignore
    │   - docker-compose.yml
    │   - environment.yml
    │   - main.py
    │   - README.md
    │   - requirements.txt
    ├───blueprints
    │       - login.py
    │       - signin.py
    │       - vaults.py
    ├───logs
    │       - * Generated log files *
    ├───static
    │       - style.css
    ├───templates
    │       - create_vault.html
    │       - index.html
    │       - login.html
    │       - show_vault.html
    │       - signin.html
    │       - vaults.html
    └───utils
            - crypto.py
            - mongo.py
            - psw_validation.py

## Secure programming solutions
OWASP Top 10 list provided a checklist for programming solutions. Here are points that were taken into consideration:
    
1. [Security Logging and Monitoring Failures](https://owasp.org/Top10/A09_2021-Security_Logging_and_Monitoring_Failures/)

2. [Cryptographic failures](https://owasp.org/Top10/A02_2021-Cryptographic_Failures/)

3. [Vulnerable and Outdated Components](https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/)

4. [Injections](https://owasp.org/Top10/A03_2021-Injection/)

### Other security related things

1. CSRF prevention

2. Sessions

3. Brute-force attack prevention

4. Mongo credentials

## Testing

### Manual testing
During the development extensive manual testing was done. Manually tested things were:
1. CSRF libarary
2. User sign in, login (in and out).
    - Invalid passwords and usernames were tested multiple times.
3. Vault creation and deletion.
    - Invalid vault names (duplicate, empty or just space) tested.
4. Item creation inside vaults.
    - Invalid names (duplicate, empty or just space) and usernames were tested.

### Automated testing
Test are inside tests folder.

    