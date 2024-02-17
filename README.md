# ScammerAutoReplier
This script connects to your inbox and monitors any phishing email, if one is detected, then a conversation is initiated with the scammer

## Configuration

1. Install dependencies with `pip install -r ./requirements.txt` in the project directory
2. Configure email credentials using these environment variables:

```bash
SCAMMERREPLIER_IMAP="imap.some.domainm"
SCAMMERREPLIER_USER="email@some.domain"
SCAMMERREPLIER_PASS="secretpassword"
SCAMMERREPLIER_SMTP="smtp.some.domainm"
```

3. Execute the script with `python3 ./main.py`
4. Have fun!

## Functioning

The program connects to an IMAP server and retrieves all emails from a specific folder (default is "INBOX"). It then parses each email's body and generates some answers using Bing APIs, response is then sent via SMTP
