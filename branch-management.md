# Guida alla gestione dei branch

Basato sulla struttura del repository (`main` per gli studenti, `solution` per la versione completa), ecco il flusso di lavoro consigliato per minimizzare i conflitti e mantenere tutto più semplice:

### 1. La tua "Base" è `solution`
Poiché il branch `solution` contiene **tutto** (codice lab + soluzioni), questo dovrebbe essere il tuo punto di riferimento principale.
*   Crea il tuo branch `dev` partendo da `solution`:
    ```bash
    git checkout solution
    git checkout -b dev
    ```

### 2. Flusso di Lavoro (Workflow)

**Passo A: Sviluppo**
Lavora su `dev`. Modifica codice, `README`, e anche i file `lab-solution.md`.
Quando hai finito, fai il merge su `solution`:
```bash
git checkout solution
git merge dev
git push origin solution
```

**Passo B: Aggiornare `main` (Student Version)**
Questa è la parte delicata. Quando porti le modifiche da `solution` a `main`, Git potrebbe cercare di ricreare i file delle soluzioni che hai cancellato in `main`.

Ecco come gestirlo in modo pulito:

1.  Spostati su `main`:
    ```bash
    git checkout main
    ```
2.  Fai il merge di `solution`:
    ```bash
    git merge solution --no-commit
    ```
    *   *Nota:* Se hai modificato un file che in `main` non esiste (es. `lab-solution.md`), Git potrebbe segnalare un **conflitto** ("deleted in HEAD, modified in solution").
3.  **Risolvi i conflitti "mantenendo la cancellazione":**
    Se ci sono conflitti sui file di soluzione, devi dire a Git di mantenerli cancellati:
    ```bash
    # Per ogni file in conflitto che deve restare cancellato:
    git rm training/moduleXX/lab-solution.md
    ```
    *Suggerimento:* Puoi rimuovere di nuovo tutti i file di soluzione per sicurezza prima di chiudere il commit:
    ```bash
    find . -name "lab-solution.md" -delete
    git add -u
    ```
4.  Completa il merge:
    ```bash
    git commit -m "Merge updates from solution to main"
    git push origin main
    ```

In sintesi: **`dev` -> `solution` -> `main` (con pulizia manuale)**.