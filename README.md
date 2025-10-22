## Delete GitHub Actions Package Versions and Findings
This script identifies and deletes package versions and findings that are related to GitHub Actions. It operates on the Endor Labs namespace (and its child namespaces if `traverse` is enabled in API calls, which it currently is for package fetching) specified in the `.env` file.

The script uses the following filters to identify GitHub Actions resources:

**For Packages:**
`spec.ecosystem==ECOSYSTEM_GITHUB_ACTION`

**For Findings:**
`spec.finding_categories contains 'FINDING_CATEGORY_GHACTIONS'`

This means:
- Packages with ecosystem set to `ECOSYSTEM_GITHUB_ACTION` will be targeted for deletion
- Findings that have `FINDING_CATEGORY_GHACTIONS` in their finding categories will be targeted for deletion

## SETUP

Step 1: Create a `.env` file in the same directory as the script and add the following, replacing the placeholders with your actual credentials and namespace. Ensure the API key has permissions to read and delete package versions and findings.

```
API_KEY=<your_api_key_here>
API_SECRET=<your_api_secret_here>
ENDOR_NAMESPACE=<your_namespace>
```

Step 2: Set up a Python virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\\Scripts\\activate`
pip install -r requirements.txt
```

Step 3: Run the script

The script can process both GitHub Actions packages and findings by default, or you can specify to process only one type:

*   **Dry Run (default behavior):** To see which GitHub Actions packages and findings would be deleted without actually deleting them:
    ```bash
    python3 main.py
    ```
    The script will list the GitHub Actions packages and findings found and state that it's in dry-run mode.

*   **Actual Deletion:** To delete all identified GitHub Actions packages and findings:
    ```bash
    python3 main.py --no-dry-run
    ```
    **Caution:** This will permanently delete package versions and findings. Ensure you have reviewed the output of a dry run first.

*   **Packages Only:** To process only GitHub Actions packages:
    ```bash
    python3 main.py --packages-only
    python3 main.py --packages-only --no-dry-run
    ```

*   **Findings Only:** To process only GitHub Actions findings:
    ```bash
    python3 main.py --findings-only
    python3 main.py --findings-only --no-dry-run
    ```

## No Warranty

Please be advised that this software is provided on an "as is" basis, without warranty of any kind, express or implied. The authors and contributors make no representations or warranties of any kind concerning the safety, suitability, lack of viruses, inaccuracies, typographical errors, or other harmful components of this software. There are inherent dangers in the use of any software, and you are solely responsible for determining whether this software is compatible with your equipment and other software installed on your equipment.

By using this software, you acknowledge that you have read this disclaimer, understand it, and agree to be bound by its terms and conditions. You also agree that the authors and contributors of this software are not liable for any damages you may suffer as a result of using, modifying, or distributing this software.
