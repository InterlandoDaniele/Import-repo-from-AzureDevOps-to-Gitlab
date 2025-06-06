**Documentazione Tecnica: Script di Migrazione Repository da Azure DevOps a GitLab**

1. **Panoramica**
2. 
Questo documento descrive uno script Python progettato per automatizzare la migrazione di repository Git da Azure DevOps a GitLab. Lo script clona i repository da Azure DevOps, crea progetti corrispondenti su GitLab tramite l'API, esegue il push dei dati e gestisce i file Git Large File Storage (LFS), se presenti. Include anche la gestione degli errori e il supporto per configurazioni di rete tramite proxy.

**Scopo**

Migrare repository Git da Azure DevOps a GitLab mantenendo la cronologia completa.
Automatizzare la creazione di progetti su GitLab.
Gestire file LFS, se utilizzati.
Fornire un processo robusto con logging dettagliato e pulizia automatica.

**Prerequisiti**

Python 3.6+ installato.

Librerie Python:
```
pip install requests
```
Git installato e configurato:
```
git --version
```
Accesso a Azure DevOps e GitLab con permessi adeguati.
Personal Access Token (PAT) per Azure DevOps e GitLab.
Namespace ID di GitLab.
Connessione di rete (eventualmente tramite proxy).

2.**Descrizione dello Script**

Funzionalità

Clona i repository da Azure DevOps in modalità --mirror per preservare tutti i branch e tag.
Utilizza l'API di GitLab per creare progetti nel namespace specificato.
Gestisce il caso in cui il progetto esiste già.
Esegue il push di tutti i dati (commit, branch, tag) al nuovo progetto GitLab.
Verifica e migra file LFS, se presenti.
Rimuove i file temporanei dopo ogni migrazione.
Registra errori dettagliati per clonazione, creazione progetto, push e LFS.
Configurabile per ambienti con proxy.

**Struttura del Codice**

Configurazione:
Variabili per PAT, URL, namespace ID, repository e proxy.

Funzioni:
run_command: Esegue comandi shell con gestione degli errori.

create_gitlab_project: Crea un progetto su GitLab tramite API.

migrate_repository: Gestisce la migrazione di un singolo repository.

main: Itera sui repository specificati.

Gestione Eccezioni:
Try-except per catturare errori in ogni fase.

Pulizia:
Blocco finally per rimuovere directory temporanee.

3.**Manuale Utente**
3.1 Installazione
Installa Python e Git:
Su Linux:
```
sudo apt-get update
sudo apt-get install python3 python3-pip git
```
Su Windows: Scarica Python da python.org e Git da git-scm.com.

Installa la libreria requests:
```
pip install requests
```
Scarica lo script:
Salva il codice come migrate_repos.py.

3.2 Configurazione
Modifica le seguenti variabili nel file migrate_repos.py:
AZURE_PAT:
Personal Access Token di Azure DevOps.

Come ottenerlo:
```
Accedi a Azure DevOps.
Vai su User Settings > Personal Access Tokens.
Crea un nuovo PAT con scope:
Code: Read (obbligatorio).
Code: Write (opzionale).
Copia il token e incollalo in:
AZURE_PAT = "<your-azure-pat>"
```
GITLAB_PAT:
Personal Access Token di GitLab.

Come ottenerlo:
```
Accedi a GitLab.
Vai su Settings > Access Tokens.
Crea un nuovo PAT con scope:
api (per creare progetti).
write_repository (per push).
read_repository (per lettura).
Copia il token e incollalo in:
GITLAB_PAT = "<your-gitlab-pat>"
```
AZURE_URL:
URL base dei repository su Azure DevOps.
```
Formato: https://dev.azure.com/<organization>/<project>/_git.

Esempio:
AZURE_URL = "https://dev.azure.com/myorg/myproject/_git"
```
GITLAB_URL:
URL del server GitLab.
```
GITLAB_URL = "http://gitlab.mydomain.com"
```
NAMESPACE_ID:
ID del namespace GitLab (gruppo o utente) dove creare i progetti.

Come ottenerlo:
```
Accedi a GitLab.
Vai su Groups > Your Group (es. mygroup).
In Settings > General, trova il Group ID.

In alternativa, usa l'API:
curl --header "PRIVATE-TOKEN: <gitlab-pat>" "<gitlab-url>/api/v4/namespaces?search=<group-name>"
Cerca l'id nel JSON restituito.

Inserisci l'ID:
NAMESPACE_ID = "<group-id>"
```
REPOS:
Lista dei repository da migrare.
```
REPOS = ["repo1", "repo2"]
```
PROXY (opzionale):
Configura il proxy se necessario.
```
PROXY = {
    "http": "http://proxy.mydomain.com:3128",
    "https": "http://proxy.mydomain.com:3128"
}
```
Se il proxy richiede autenticazione:
```
PROXY = {
    "http": "http://<username>:<password>@proxy.mydomain.com:3128",
    "https": "http://<username>:<password>@proxy.mydomain.com:3128"
}
```
Se non usi un proxy, lascia:
```
PROXY = None
```
no_proxy (opzionale):
Esclude indirizzi dal proxy (es. server GitLab interno).
```
os.environ["no_proxy"] = "10.10.100.50,localhost"
```
3.3 Configurazione di Rete
Proxy per Git:
Configura il proxy per i comandi Git:
```
git config --global http.proxy http://proxy.mydomain.com:3128
git config --global https.proxy http://proxy.mydomain.com:3128
```
Con autenticazione:
```
git config --global http.proxy http://<username>:<password>@proxy.mydomain.com:3128
git config --global https.proxy http://<username>:<password>@proxy.mydomain.com:3128
```
Verifica:
```
git config --global --get http.proxy
```
Bypass Proxy per GitLab:
Aggiungi il server GitLab a no_proxy nel sistema:
```
sudo nano /etc/environment

Aggiungi:
no_proxy=localhost,127.0.0.1,<gitlab-ip>

Applica:
source /etc/environment
```
3.4 Esecuzione
Salva lo script come migrate_repos.py.

Esegui:
python3 migrate_repos.py

Output:
Lo script mostra ogni passo (clonazione, creazione progetto, push, LFS).
In caso di errore, visualizza il messaggio dettagliato.

3.5 Debug
Errore 503 su Azure DevOps:
Verifica lo stato del servizio: Azure DevOps Status.
```
Controlla il PAT e i permessi.
```
Riprova dopo alcune ore.

Errore 403 su GitLab:
Verifica gli scope del PAT.
```
Controlla l'URL di GitLab e il namespace ID.
```
Contatta l'amministratore del proxy se ricevi "Access Denied".

Errori di rete:
Testa la connettività:
```
curl -v --proxy http://proxy.mydomain.com:3128 <gitlab-url>/api/v4/projects
curl -v --proxy http://proxy.mydomain.com:3128 <azure-url>
```
Configura correttamente il proxy.

Log di GitLab:
```
sudo tail -f /var/log/gitlab/gitlab-rails/production.log
```
4. Dettagli Tecnici
Dipendenze
Python: subprocess, requests, os, shutil, json, sys.
Git: Per clonazione e push.
requests: Per chiamate API a GitLab.

**Flusso di Esecuzione**
```
main():
Itera sui repository in REPOS.
Chiama migrate_repository per ogni repository.
migrate_repository(repo):
Clona il repository da Azure DevOps (git clone --mirror).
Crea il progetto su GitLab (create_gitlab_project).
Aggiunge il remoto GitLab e fa il push (git push --mirror).
Gestisce Git LFS, se presente.
Pulisce i file temporanei.
create_gitlab_project(repo_name, namespace_id):
Invia una richiesta POST all'API di GitLab per creare il progetto.
Gestisce errori 400 (progetto esistente) e altri codici HTTP.
run_command(command):
Esegue comandi shell e cattura output/errror.
Gestione Errori
Clonazione:
Fallisce se il repository non esiste o il PAT non ha permessi.
Creazione Progetto:
Fallisce se il namespace ID è errato o il PAT manca di scope api.
Push:
Fallisce se l'URL di GitLab è errato o il PAT manca di scope write_repository.
Rete:
Gestisce errori di connettività tramite requests.RequestException.
Sicurezza
I PAT devono essere trattati come dati sensibili e non inclusi in repository pubblici.
Usa HTTPS per GitLab, se possibile, per maggiore sicurezza:

GITLAB_URL = "https://<gitlab-domain>"

Configura certificati SSL se necessario:

git config --global http.sslCAInfo /path/to/gitlab-cert.pem
```
5. **Manutenzione e Miglioramenti Futuri**
Aggiungere ritmi di esecuzione:
Includere time.sleep() per gestire i limiti di Azure DevOps:
```
import time
time.sleep(5)  # Ritardo di 5 secondi
```
Support per sottogruppi:
Modificare create_gitlab_project per gestire namespace annidati.

Logging avanzato:
Usare il modulo logging per scrivere output in un file di log:
```
import logging
logging.basicConfig(level=logging.DEBUG, filename='migration.log')
logging.debug('Messaggio di debug')
```
Validazione preventiva:
Verifica PAT e URL prima di iniziare la migrazione.

6. **Esempio di Configurazione**
```
AZURE_PAT = "abc123xyz789"
GITLAB_PAT = "glpat-xyz789abc123"
AZURE_URL"https://dev.azure.com/myorg/myproject/_git"
GITLAB_URL"http://gitlab.local"
NAMESPACE_ID"10"
REPOS = ["repo1", "repo2"]
PROXY = {
    "http": "http://proxy.mydomain.com:3128",
    "https": "http://proxy.mydomain.com:3128"
}
os.environ["no_proxy"] = "http://gitlab.local"
```
7. **Risoluzione dei Problemi Comuni**
7.1: Errore 503 su Azure DevOps
Controlla: Azure DevOps Status.

Verifica il PAT:
```
git clone https://<azure-pat>@dev.azure.com/<org>/<project>/_git/<repo>
```
Configura il proxy correttamente.

7.2: Errore 403 su GitLab
Verifica gli scope del PAT.

Testa l'API:
```
curl --header "PRIVATE-TOKEN: <gitlab-pat>" -X POST -d '{"name":"test-repo","namespace_id":"<id>"}' <gitlab-url>/api/v4/projects
```
Controlla il proxy:
```
curl -v --proxy http://proxy.mydomain.com:3128 <gitlab-url>/api/v4/projects
```
7.3: Repository non trovato
Verifica il nome del repository su Azure DevOps.

Aggiorna REPOS con i nomi corretti.

7.4: Problemi di rete
Configura PROXY e no_proxy.

Testa la connettività:
```
ping <gitlab-url>
ping dev.azure.com
```
8. **Conclusione**
Questo script offre un metodo automatizzato e robusto per migrare repository da Azure DevOps a GitLab. Con una configurazione corretta e la gestione dei requisiti di rete, consente di risparmiare tempo e ridurre gli errori manuali. Per problemi persistenti, consulta i log di GitLab/Azure DevOps o contatta gli amministratori di sistema.

