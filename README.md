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

## Sample

### Received email

```txt
Alla vostra attenzione
È necessario effettuare il bonifico a questi dettagli di contatto
A seguito dell'accordo stragiudiziale Risoluzione 4850 euro.
Di seguito è riportato l'IBAN del nostro agente (contabile della Sezione Multe e Pagamenti Telematici dell'UE).
NOME :  AAAAAAAAAAAAAAA
IBAN:  AAAAAAAAAAAAAA
BIC :  AAAAAAAAAAAAAA
MOTIVO DEL PAGAMENTO: SPESE DI ASSISTENZA LEGALE
Vi chiediamo di effettuare il bonifico immediatamente, non appena ricevete i dettagli. Vi preghiamo di effettuare il bonifico non appena riceverete questa lettera per evitare ritardi e complicazioni nel vostro caso.
Una volta effettuato il bonifico, vi preghiamo di inviarci una copia scannerizzata dell'ordine di bonifico per conferma.
Cordiali saluti
```

### Chat response

```txt
Caro Ufficio Protezione,
Grazie per la vostra comunicazione. Sono disposto a seguire le vostre istruzioni e a effettuare il bonifico immediatamente. Ho preso nota dei dettagli di contatto e procederò con il pagamento come richiesto.
Cordiali saluti
```
