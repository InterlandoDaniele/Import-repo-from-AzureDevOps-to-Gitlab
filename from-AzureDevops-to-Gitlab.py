import subprocess
import requests
import os
import shutil
import sys
import json

# Configurazione
AZURE_PAT = "" #TOKEN
GITLAB_PAT = "" #TOKEN
AZURE_URL = "https://dev.azure.com/_git"
GITLAB_URL = "http://..../"
NAMESPACE_ID = ""
REPOS = ["...."]  # Corretto: lista di repository/list repo

# # Configura il proxy/Config Proxy
# PROXY = {
#     "http": "http://<proxy>:<port>",
#     "https": "http://<proxy>:<port>"
# }

# # Bypass proxy per GitLab
# os.environ["no_proxy"] = ""

# Funzione per eseguire comandi shell con gestione degli errori
def run_command(command, cwd=None):
    try:
        result = subprocess.run(command, cwd=cwd, shell=True, capture_output=True, text=True, check=True)
        print(f"Comando eseguito con successo: {command}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'esecuzione del comando: {command}")
        print(f"Errore: {e.stderr}")
        raise

# Funzione per creare un progetto su GitLab
def create_gitlab_project(repo_name, namespace_id):
    url = f"{GITLAB_URL}/api/v4/projects"
    headers = {"PRIVATE-TOKEN": GITLAB_PAT}
    data = {
        "name": repo_name,
        "namespace_id": namespace_id,
        "visibility": "private"
    }
    try:
        response = requests.post(url, headers=headers, json=data, proxies=PROXY)
        if response.status_code == 201:
            print(f"Progetto {repo_name} creato con successo su GitLab.")
            return response.json()
        elif response.status_code == 400 and "has already been taken" in response.text:
            print(f"Il progetto {repo_name} esiste già su GitLab.")
            return None
        else:
            print(f"Errore durante la creazione del progetto {repo_name}: {response.status_code} - {response.text}")
            raise Exception(f"Errore API GitLab: {response.text}")
    except requests.RequestException as e:
        print(f"Errore di rete durante la creazione del progetto {repo_name}: {e}")
        raise

# Funzione principale per la migrazione
def migrate_repository(repo):
    repo_dir = f"{repo}.git"
    try:
        # Clona il repository da Azure DevOps
        print(f"Clonazione del repository {repo} da Azure DevOps...")
        run_command(f"git clone --mirror https://{AZURE_PAT}@dev.azure.com/_git/{repo}")

        # Crea il progetto su GitLab
        print(f"Creazione del progetto {repo} su GitLab...")
        create_gitlab_project(repo, NAMESPACE_ID)

        # Aggiungi il remoto GitLab
        os.chdir(repo_dir)
        print(f"Aggiunta del remoto GitLab per {repo}...")
        run_command(f"git remote add gitlab http://oauth2:{GITLAB_PAT}@gitlab/{repo}.git")

        # Esegui il push del repository
        print(f"Push del repository {repo} su GitLab...")
        run_command(f"git push --mirror gitlab")

        # Gestione Git LFS (se applicabile)
        print(f"Verifica Git LFS per {repo}...")
        os.chdir("..")
        shutil.rmtree(repo_dir)  # Pulisci il clone mirror
        run_command(f"git clone https://{AZURE_PAT}@dev.azure.com/_git/{repo}")
        os.chdir(repo)
        run_command("git lfs install")
        try:
            run_command("git lfs fetch --all")
            run_command(f"git push gitlab --all")
            run_command(f"git lfs push --all http://oauth2:{GITLAB_PAT}@gitlab/{repo}.git")
            print(f"Git LFS completato per {repo}.")
        except subprocess.CalledProcessError:
            print(f"Nessun file LFS trovato per {repo}, proseguo.")
        os.chdir("..")
        shutil.rmtree(repo)
        print(f"Migrazione di {repo} completata con successo!")

    except Exception as e:
        print(f"Errore durante la migrazione di {repo}: {e}")
    finally:
        # Pulisci
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir)
        if os.path.exists(repo):
            shutil.rmtree(repo)

# Esegui la migrazione per ogni repository
def main():
    for repo in REPOS:
        print(f"\nInizio migrazione per {repo}...")
        migrate_repository(repo)

if __name__ == "__main__":
    main()